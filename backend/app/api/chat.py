"""AI fortune-teller chat endpoints (backed by Ollama + Gemma)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import get_current_user
from ..models import ChatMessage, ChatSession, Profile, User
from ..schemas import (
    ChatMessageCreate,
    ChatMessageOut,
    ChatReply,
    ChatSessionOut,
)
from ..services.chat import ChatTurn, send_chat

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/sessions", response_model=list[ChatSessionOut])
def list_sessions(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ChatSession]:
    return (
        db.query(ChatSession)
        .filter(ChatSession.owner_id == user.id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageOut])
def list_messages(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ChatMessage]:
    session = db.get(ChatSession, session_id)
    if session is None or session.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.messages


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.get(ChatSession, session_id)
    if session is None or session.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()


@router.post("/message", response_model=ChatReply)
def send_message(
    payload: ChatMessageCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatReply:
    # Resolve profile (optional)
    profile: Profile | None = None
    if payload.profile_id is not None:
        profile = db.get(Profile, payload.profile_id)
        if profile is None or profile.owner_id != user.id:
            raise HTTPException(status_code=404, detail="Profile not found")

    # Resolve or create session
    if payload.session_id is not None:
        session = db.get(ChatSession, payload.session_id)
        if session is None or session.owner_id != user.id:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = ChatSession(
            owner_id=user.id,
            profile_id=payload.profile_id,
            title=payload.question[:80],
        )
        db.add(session)
        db.flush()

    history = [ChatTurn(role=m.role, content=m.content) for m in session.messages]

    # Call Ollama
    try:
        reply_text = send_chat(history, payload.question, profile)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    user_msg = ChatMessage(session_id=session.id, role="user", content=payload.question)
    assistant_msg = ChatMessage(session_id=session.id, role="assistant", content=reply_text)
    db.add_all([user_msg, assistant_msg])
    db.commit()
    db.refresh(user_msg)
    db.refresh(assistant_msg)
    db.refresh(session)

    return ChatReply(
        session=ChatSessionOut.model_validate(session),
        user_message=ChatMessageOut.model_validate(user_msg),
        assistant_message=ChatMessageOut.model_validate(assistant_msg),
    )
