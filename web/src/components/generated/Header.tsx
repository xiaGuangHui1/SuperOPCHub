import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { FaUser } from "react-icons/fa";
import { useAuth } from "@/hooks/useAuth";

export function Header() {
  const { user } = useAuth();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 sm:h-16 flex items-center justify-between">
        <div className="flex items-center gap-2 sm:gap-4">
          <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg sm:rounded-xl flex items-center justify-center shadow-lg">
            <span className="text-white font-bold text-xs sm:text-base">OPC</span>
          </div>
          <h1 className="text-lg sm:text-2xl font-bold text-gray-900">Super OPC Hub</h1>
        </div>
        <Link to={user ? "/profile" : "/login"}>
          <Button
            variant="outline"
            className="gap-1 sm:gap-2 border-blue-200 text-blue-600 hover:bg-blue-50 text-xs sm:text-sm px-3 sm:px-4"
          >
            <FaUser className="w-3 h-3 sm:w-4 sm:h-4" />
            <span className="hidden sm:inline">{user ? "个人中心" : "登录/注册"}</span>
            <span className="sm:hidden">{user ? "我的" : "登录"}</span>
          </Button>
        </Link>
      </div>
    </header>
  );
}
