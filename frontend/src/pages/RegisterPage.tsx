import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth";

export function RegisterPage() {
  const { register } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await register(email, password, name || undefined);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm rounded-2xl border border-ink/10 bg-white p-8 shadow-sm">
        <div className="mb-6 text-center">
          <div className="font-display text-4xl">八字</div>
          <div className="font-display text-sm text-muted mt-1">Create your account</div>
        </div>
        <form onSubmit={onSubmit} className="space-y-3">
          <label className="block">
            <span className="text-xs text-muted">Display name</span>
            <input className="input mt-1" value={name} onChange={(e) => setName(e.target.value)} />
          </label>
          <label className="block">
            <span className="text-xs text-muted">Email</span>
            <input type="email" className="input mt-1" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </label>
          <label className="block">
            <span className="text-xs text-muted">Password (min 8 chars)</span>
            <input type="password" className="input mt-1" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
          </label>
          {error && <div className="text-xs text-fire">{error}</div>}
          <button type="submit" disabled={busy} className="btn-primary w-full">
            {busy ? "Creating…" : "Create account"}
          </button>
        </form>
        <p className="mt-4 text-xs text-muted text-center">
          Already have an account? <Link to="/login" className="underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
