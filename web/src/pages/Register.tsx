import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { PageMeta } from "@/components/common/PageMeta";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { FaEnvelope, FaLock, FaArrowLeft } from "react-icons/fa";
import { motion } from "framer-motion";
import { useLogin } from "@/hooks/useLogin";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [localError, setLocalError] = useState("");
  const { loading, error, signUp } = useLogin("/");
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError("");

    if (!email || !email.includes("@")) {
      setLocalError("请输入有效的邮箱地址");
      return;
    }
    if (password.length < 6) {
      setLocalError("密码至少需要 6 个字符");
      return;
    }
    if (password !== confirmPassword) {
      setLocalError("两次输入的密码不一致");
      return;
    }

    await signUp(email, password);
  };

  const displayError = localError || error;

  return (
    <>
      <PageMeta
        title="注册 - Super OPC Hub"
        description="注册 Super OPC Hub 账号"
        keywords={["注册", "OPC", "账号"]}
      />
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 relative">
            <button
              onClick={() => navigate(-1)}
              className="absolute top-4 left-4 w-8 h-8 flex items-center justify-center rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
              aria-label="返回"
            >
              <FaArrowLeft className="w-4 h-4" />
            </button>
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg mx-auto mb-4">
                <span className="text-white font-bold text-2xl">OPC</span>
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                创建账号
              </h1>
              <p className="text-gray-500 text-sm">
                注册 Super OPC Hub，探索更多可能
              </p>
            </div>

            <form onSubmit={handleRegister} className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium text-gray-700">
                  邮箱地址
                </Label>
                <div className="relative">
                  <FaEnvelope className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your@email.com"
                    className="pl-10 h-12"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium text-gray-700">
                  密码
                </Label>
                <div className="relative">
                  <FaLock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="至少 6 个字符"
                    className="pl-10 h-12"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword" className="text-sm font-medium text-gray-700">
                  确认密码
                </Label>
                <div className="relative">
                  <FaLock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="confirmPassword"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="再次输入密码"
                    className="pl-10 h-12"
                  />
                </div>
              </div>

              {displayError && (
                <p className="text-sm text-red-600">{displayError}</p>
              )}

              <Button
                type="submit"
                disabled={loading}
                className="w-full h-12 bg-blue-500 hover:bg-blue-600 text-white font-medium"
              >
                {loading ? "注册中..." : "注册"}
              </Button>

              <p className="text-xs text-gray-500 text-center">
                注册即表示您同意{" "}
                <a href="#" className="text-blue-500 hover:underline">
                  服务条款
                </a>{" "}
                和{" "}
                <a href="#" className="text-blue-500 hover:underline">
                  隐私政策
                </a>
              </p>
            </form>
          </div>

          <p className="text-center text-sm text-gray-500 mt-6">
            已有账号？{" "}
            <Link to="/login" className="text-blue-500 font-medium hover:underline">
              去登录
            </Link>
          </p>
        </motion.div>
      </div>
    </>
  );
}
