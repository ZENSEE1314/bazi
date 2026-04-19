import { useEffect, useRef, useState } from "react";
import { useI18n } from "../i18n";

type Props = {
  // 'user' for face (front camera), 'environment' for palm (rear camera)
  facingMode?: "user" | "environment";
  // Optional: called after capture with a data URL for preview. We don't
  // upload the image — users will describe features — but seeing yourself
  // helps answer the form accurately.
  onCapture?: (dataUrl: string) => void;
};

/**
 * Tiny camera+upload helper. The captured image stays in the browser — it's
 * a visual aid while the user fills in the feature form. No server upload.
 */
export function CameraCapture({ facingMode = "user", onCapture }: Props) {
  const { t } = useI18n();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [snapshot, setSnapshot] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    return () => {
      if (stream) stream.getTracks().forEach((tr) => tr.stop());
    };
  }, [stream]);

  async function openCamera() {
    setError(null);
    try {
      const s = await navigator.mediaDevices.getUserMedia({
        video: { facingMode },
        audio: false,
      });
      setStream(s);
      if (videoRef.current) {
        videoRef.current.srcObject = s;
        await videoRef.current.play();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Camera unavailable");
    }
  }

  function capture() {
    const v = videoRef.current;
    const c = canvasRef.current;
    if (!v || !c) return;
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
        {snapshot ? (
          <img src={snapshot} alt="captured" className="w-full h-full object-cover" />
        ) : stream ? (
          <video ref={videoRef} playsInline muted className="w-full h-full object-cover" />
        ) : (
          <div className="text-parchment/60 text-sm">📷</div>
        )}
        <canvas ref={canvasRef} className="hidden" />
      </div>
      {error && <div className="text-fire text-xs mb-2">{error}</div>}
      <div className="flex gap-2 flex-wrap">
        {!stream && !snapshot && (
          <button type="button" className="btn-ghost text-xs" onClick={openCamera}>
            {t("face.camera")}
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
