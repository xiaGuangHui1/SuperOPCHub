import { Outlet, useLocation } from "react-router-dom";
import { Link } from "react-router-dom";
import { FaHome, FaThLarge, FaCompass, FaUser } from "react-icons/fa";

export function Layout() {
  const location = useLocation();
  const showNav = ["/", "/square", "/discovery", "/profile"].includes(location.pathname);

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="flex flex-col min-h-screen">
      <main className="flex-1">
        <Outlet />
      </main>
      {showNav && (
        <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 safe-area-bottom">
          <div className="max-w-7xl mx-auto flex items-center justify-around h-16">
            <Link
              to="/"
              className={`flex flex-col items-center justify-center w-full h-full space-y-1 ${
                isActive("/") ? "text-blue-500" : "text-gray-500"
              }`}
            >
              <FaHome className="w-6 h-6" />
              <span className="text-xs font-medium">首页</span>
            </Link>

            <Link
              to="/square"
              className={`flex flex-col items-center justify-center w-full h-full space-y-1 ${
                isActive("/square") ? "text-blue-500" : "text-gray-500"
              }`}
            >
              <FaThLarge className="w-6 h-6" />
              <span className="text-xs font-medium">广场</span>
            </Link>

            <Link
              to="/discovery"
              className={`flex flex-col items-center justify-center w-full h-full space-y-1 ${
                isActive("/discovery") ? "text-blue-500" : "text-gray-500"
              }`}
            >
              <FaCompass className="w-6 h-6" />
              <span className="text-xs font-medium">发现</span>
            </Link>

            <Link
              to="/profile"
              className={`flex flex-col items-center justify-center w-full h-full space-y-1 ${
                isActive("/profile") ? "text-blue-500" : "text-gray-500"
              }`}
            >
              <FaUser className="w-6 h-6" />
              <span className="text-xs font-medium">我的</span>
            </Link>
          </div>
        </nav>
      )}
    </div>
  );
}
