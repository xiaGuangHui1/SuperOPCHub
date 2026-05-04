import { Navigate, Outlet, RouteObject } from "react-router-dom";
import { Layout } from "./layout";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Square from "./pages/Square";
import Discovery from "./pages/Discovery";
import Profile from "./pages/Profile";
import OPCDetail from "./pages/OPCDetail";
import { useAuth } from "./hooks/useAuth";

/** 需要登录才能访问的路由，未登录跳转 /login */
function ProtectedRoute() {
  const { user, loading } = useAuth();

  console.log('[ProtectedRoute] loading:', loading, 'user:', user?.email ?? null);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) {
    console.log('[ProtectedRoute] redirecting to /login');
    return <Navigate to="/login" replace />;
  }

  console.log('[ProtectedRoute] rendering Outlet');
  return <Outlet />;
}

/** 仅未登录可访问的路由（登录/注册），已登录跳转首页 */
function PublicOnlyRoute() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (user) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}

export const routes: RouteObject[] = [
  {
    element: <Layout />,
    children: [
      // 需要登录的页面
      {
        element: <ProtectedRoute />,
        children: [
          { path: "/", element: <Home /> },
          { path: "/square", element: <Square /> },
          { path: "/discovery", element: <Discovery /> },
          { path: "/profile", element: <Profile /> },
          { path: "/opc/:id", element: <OPCDetail /> },
        ],
      },
      // 未登录专属页面（已登录则跳首页）
      {
        element: <PublicOnlyRoute />,
        children: [
          { path: "/login", element: <Login /> },
          { path: "/register", element: <Register /> },
        ],
      },
      // 未匹配路由一律到登录页
      { path: "*", element: <Navigate to="/login" replace /> },
    ],
  },
];
