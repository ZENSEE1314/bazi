import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth";
import { Shell } from "./components/Shell";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { DashboardPage } from "./pages/DashboardPage";
import { ProfilesPage } from "./pages/ProfilesPage";
import { ProfileDetailPage } from "./pages/ProfileDetailPage";
import { NumerologyPage } from "./pages/NumerologyPage";
import { NamePage } from "./pages/NamePage";
import { FengShuiPage } from "./pages/FengShuiPage";
import { ChatPage } from "./pages/ChatPage";
import { CompatibilityPage } from "./pages/CompatibilityPage";

function Private({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center text-muted">
        Loading…
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function Public({ children }: { children: JSX.Element }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (user) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Public><LoginPage /></Public>} />
        <Route path="/register" element={<Public><RegisterPage /></Public>} />
        <Route
          element={
            <Private>
              <Shell />
            </Private>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="/profiles" element={<ProfilesPage />} />
          <Route path="/profiles/:id" element={<ProfileDetailPage />} />
          <Route path="/numerology" element={<NumerologyPage />} />
          <Route path="/name" element={<NamePage />} />
          <Route path="/fengshui" element={<FengShuiPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/compatibility" element={<CompatibilityPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}
