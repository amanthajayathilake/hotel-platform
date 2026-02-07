import { useEffect } from "react";
import { Toaster } from "react-hot-toast";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Loading from "./components/ui/Loading";
import HotelDetailPage from "./pages/HotelDetailPage";
import HotelFormPage from "./pages/HotelFormPage";
import HotelsPage from "./pages/HotelsPage";
import LoginPage from "./pages/LoginPage";
import RoomTypeFormPage from "./pages/RoomTypeFormPage";
import { useAuthStore } from "./store/authStore";

// Protected Route wrapper
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { token } = useAuthStore();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Public Route wrapper (redirects to hotels if already logged in)
const PublicRoute = ({ children }: { children: React.ReactNode }) => {
  const { token } = useAuthStore();

  if (token) {
    return <Navigate to="/hotels" replace />;
  }

  return <>{children}</>;
};

function App() {
  const { fetchCurrentUser, isLoading } = useAuthStore();

  useEffect(() => {
    // Check if user is already logged in on app load
    fetchCurrentUser();
  }, []);

  if (isLoading) {
    return <Loading fullScreen size="lg" text="Loading..." />;
  }

  return (
    <>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route
            path="/login"
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            }
          />

          {/* Protected routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/hotels" replace />} />
            <Route path="hotels" element={<HotelsPage />} />
            <Route path="hotels/:id" element={<HotelDetailPage />} />
            <Route path="hotels/new" element={<HotelFormPage />} />
            <Route path="hotels/:id/edit" element={<HotelFormPage />} />
            <Route
              path="hotels/:hotelId/room-types/new"
              element={<RoomTypeFormPage />}
            />
          </Route>

          {/* Catch all - redirect to hotels */}
          <Route path="*" element={<Navigate to="/hotels" replace />} />
        </Routes>
      </BrowserRouter>

      {/* Toast notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: "#fff",
            color: "#363636",
          },
          success: {
            iconTheme: {
              primary: "#10b981",
              secondary: "#fff",
            },
          },
          error: {
            iconTheme: {
              primary: "#ef4444",
              secondary: "#fff",
            },
          },
        }}
      />
    </>
  );
}

export default App;
