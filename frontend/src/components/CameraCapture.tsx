import { useEffect, useRef, useState } from "react";
import { useI18n } from "../i18n";

type Props = {
  // 'user' for face (front camera), 'environment' for palm (rear camera).
  // If the device doesn't have the requested camera we fall back to any camera.
  facingMode?: "user" | "environment";
  // Optional: called after capture with a data URL for preview. We don't
  // upload the image — users will describe features — but seeing yourself
  // helps answer the form accurately.
  onCapture?: (dataUrl: string) => void;
};

/**
 * Camera + upload helper. The captured image stays in the browser — it's a
 * visual aid while the user fills in the feature form. No server upload.
 *
 * Implementation notes:
 * - `srcObject` MUST be attached in an effect after React renders the
 *   <video> element; attaching it inside the same click handler that calls
 *   setStream() silently fails because the <video> ref is still null.
 * - `getUserMedia` requires a secure context (https:// or localhost) AND
 *   a user gesture. We tell the user clearly when either precondition is
 *   missing, rather than just showing a blank viewfinder.
 */
export function CameraCapture({ facingMode = "user", onCapture }: Props) {
  const { t } = useI18n();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [snapshot, setSnapshot] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [opening, setOpening] = useState(false);

  // Attach the stream to the <video> whenever either changes. This runs
  // AFTER React commits, so the ref is populated.
  useEffect(() => {
    const v = videoRef.current;
    if (v && stream) {
      v.srcObject = stream;
      const playPromise = v.play();
      if (playPromise && typeof playPromise.catch === "function") {
        playPromise.catch(() => {
          /* play() can reject if the tab is backgrounded; user can retry. */
        });
      }
    }
    if (v && !stream) {
      v.srcObject = null;
    }
  }, [stream]);

  // Release camera tracks when the component unmounts or stream changes.
  useEffect(() => {
    return () => {
      if (stream) stream.getTracks().forEach((tr) => tr.stop());
    };
  }, [stream]);

  async function openCamera() {
    setError(null);

    // Precondition 1: API must exist (older browsers, non-secure context).
    if (typeof navigator === "undefined"
        || !navigator.mediaDevices
        || typeof navigator.mediaDevices.getUserMedia !== "function") {
      const insecure = typeof window !== "undefined"
        && window.location.protocol !== "https:"
        && window.location.hostname !== "localhost";
      setError(
        insecure
          ? t("camera.err_insecure")
          : t("camera.err_unsupported"),
      );
      return;
    }

    setOpening(true);
    try {
      let s: MediaStream;
      try {
        // Preferred: the facingMode the page asked for.
        s = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: { ideal: facingMode } },
          audio: false,
        });
      } catch (firstErr) {
        // Fallback: laptops usually only have the front cam, so asking for
        // 'environment' fails there. Retry with no constraint before giving up.
        if (firstErr instanceof Error && firstErr.name === "OverconstrainedError") {
          s = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        } else {
          throw firstErr;
        }
      }
      setStream(s);
    } catch (err) {
      setError(describeCameraError(err, t));
    } finally {
      setOpening(false);
    }
  }

  function capture() {
    const v = videoRef.current;
    const c = canvasRef.current;
    if (!v || !c) return;
    if (!v.videoWidth || !v.videoHeight) {
      setError(t("camera.err_not_ready"));
      return;
    }
    c.width = v.videoWidth;
    c.height = v.videoHeight;
    const ctx = c.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(v, 0, 0);
    const dataUrl = c.toDataURL("image/jpeg", 0.85);
    setSnapshot(dataUrl);
    onCapture?.(dataUrl);
    if (stream) {
      stream.getTracks().forEach((tr) => tr.stop());
      setStream(null);
    }
  }

  function retake() {
    setSnapshot(null);
    openCamera();
  }

  function onUploadFile(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = () => {
      const url = String(reader.result);
      setSnapshot(url);
      onCapture?.(url);
    };
    reader.readAsDataURL(f);
  }

  return (
    <div className="rounded-2xl border border-ink/10 bg-ink/5 p-3">
      <div className="aspect-[4/3] bg-black/80 rounded-xl overflow-hidden flex items-center justify-center mb-2 relative">
        {/* Always render the <video> once we have a stream so its ref is
            available to the effect above. Hide it when a snapshot replaces it. */}
        {stream && !snapshot && (
          <video
            ref={videoRef}
            playsInline
            autoPlay
            muted
            className="w-full h-full object-cover"
          />
        )}
        {snapshot && (
          <img
            src={snapshot}
            alt=""
            className="w-full h-full object-cover"
          />
        )}
        {!stream && !snapshot && (
          <div className="text-parchment/70 text-sm flex flex-col items-center gap-2">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
              <circle cx="12" cy="13" r="4" />
            </svg>
            <span className="text-xs">{t("camera.idle_hint")}</span>
          </div>
        )}
        <canvas ref={canvasRef} className="hidden" />
      </div>
      {error && (
        <div className="text-fire text-xs mb-2 leading-relaxed">{error}</div>
      )}
      <div className="flex gap-2 flex-wrap">
        {!stream && !snapshot && (
          <button
            type="button"
            className="btn-ghost text-xs"
            onClick={openCamera}
            disabled={opening}
          >
            {opening ? t("camera.opening") : t("face.camera")}
          </button>
        )}
        {stream && !snapshot && (
          <button type="button" className="btn-primary text-xs" onClick={capture}>
            {t("face.capture")}
          </button>
        )}
        {snapshot && (
          <button type="button" className="btn-ghost text-xs" onClick={retake}>
            {t("face.retake")}
          </button>
        )}
        <label className="btn-ghost text-xs cursor-pointer">
          {t("face.upload")}
          <input type="file" accept="image/*" className="hidden" onChange={onUploadFile} />
        </label>
      </div>
    </div>
  );
}

/** Turn the browser's opaque MediaError names into something the user can
 *  actually act on (allow permission, plug in a camera, open in Chrome…). */
function describeCameraError(err: unknown, t: (k: string) => string): string {
  if (!(err instanceof Error)) return t("camera.err_unknown");
  switch (err.name) {
    case "NotAllowedError":
    case "PermissionDeniedError":
      return t("camera.err_denied");
    case "NotFoundError":
    case "DevicesNotFoundError":
      return t("camera.err_not_found");
    case "NotReadableError":
    case "TrackStartError":
      return t("camera.err_in_use");
    case "OverconstrainedError":
      return t("camera.err_overconstrained");
    case "SecurityError":
      return t("camera.err_insecure");
    default:
      return `${t("camera.err_unknown")} (${err.name})`;
  }
}
