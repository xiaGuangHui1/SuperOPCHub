import { Link } from "react-router-dom";

export function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 sm:h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 sm:gap-4">
          <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg sm:rounded-xl flex items-center justify-center shadow-lg">
            <span className="text-white font-bold text-xs sm:text-base">OPC</span>
          </div>
          <h1 className="text-lg sm:text-2xl font-bold text-gray-900">Super OPC Hub</h1>
        </Link>
        <span className="text-xs sm:text-sm text-gray-400">搜索找到能胜任的人</span>
      </div>
    </header>
  );
}
