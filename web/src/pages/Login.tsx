import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { PageMeta } from "@/components/common/PageMeta";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { FaEnvelope, FaLock, FaTimes, FaShieldAlt } from "react-icons/fa";
import { motion } from "framer-motion";
import { useLogin } from "@/hooks/useLogin";

type AuthTab = "otp" | "password";

export default function Login() {
  const [activeTab, setActiveTab] = useState<AuthTab>("password");
  const { loading, error, sendOTP, verifyOTP, signInWithPassword } =
    useLogin("/");
  const navigate = useNavigate();

  // ── OTP 表单 ──────────────────────────────────
  const [otpEmail, setOtpEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [countdown, setCountdown] = useState(0);

  // ── 密码表单 ──────────────────────────────────
  const [pwdEmail, setPwdEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSendOtp = async () => {
    if (!otpEmail || !otpEmail.includes("@")) return;
    const success = await sendOTP(otpEmail, "email");
    if (success) {
      setCountdown(20);
      const timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otp || otp.length < 4) return;
    await verifyOTP(otpEmail, otp, "email");
  };

  const handlePasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pwdEmail || !password) return;
    await signInWithPassword(pwdEmail, password);
  };

  return (
    <>
      <PageMeta
        title="登录 - Super OPC Hub"
        description="登录 Super OPC Hub，探索创意、匹配专业人士"
        keywords={["登录", "OPC", "需求匹配"]}
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
              onClick={() => navigate("/")}
              className="absolute top-4 left-4 w-8 h-8 flex items-center justify-center rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
              aria-label="返回首页"
            >
              <FaTimes className="w-4 h-4" />
            </button>

            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg mx-auto mb-4">
                <span className="text-white font-bold text-2xl">OPC</span>
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                欢迎使用 Super OPC Hub
              </h1>
            </div>

            {/* ── Tab 切换 ─────────────────────── */}
            <div className="flex border-b border-gray-200 mb-6">
              <button
                type="button"
                onClick={() => setActiveTab("password")}
                className={`flex-1 pb-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === "password"
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                密码登录
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("otp")}
                className={`flex-1 pb-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === "otp"
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700"
                }`}
              >
                验证码登录
              </button>
            </div>

            {/* ── OTP 验证码登录 ────────────────── */}
            {activeTab === "otp" && (
              <form onSubmit={handleVerifyOtp} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="otpEmail" className="text-sm font-medium text-gray-700">
                    邮箱地址
                  </Label>
                  <div className="relative">
                    <FaEnvelope className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      id="otpEmail"
                      type="email"
                      value={otpEmail}
                      onChange={(e) => setOtpEmail(e.target.value)}
                      placeholder="your@email.com"
                      className="pl-10 h-12"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="otp" className="text-sm font-medium text-gray-700">
                    验证码
                  </Label>
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <FaShieldAlt className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                      <Input
                        id="otp"
                        type="text"
                        value={otp}
                        onChange={(e) => setOtp(e.target.value)}
                        placeholder="6 位验证码"
                        className="pl-10 h-12"
                        maxLength={6}
                      />
                    </div>
                    <Button
                      type="button"
                      onClick={handleSendOtp}
                      disabled={loading || countdown > 0}
                      variant="outline"
                      className="h-12 px-4 whitespace-nowrap text-sm border-gray-200"
                    >
                      {countdown > 0 ? `${countdown}s` : "发送验证码"}
                    </Button>
                  </div>
                </div>

                {error && <p className="text-sm text-red-600">{error}</p>}

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full h-12 bg-blue-500 hover:bg-blue-600 text-white font-medium"
                >
                  {loading ? "验证中..." : "登录/注册"}
                </Button>
              </form>
            )}

            {/* ── 密码登录 ──────────────────────── */}
            {activeTab === "password" && (
              <form onSubmit={handlePasswordLogin} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="pwdEmail" className="text-sm font-medium text-gray-700">
                    邮箱地址
                  </Label>
                  <div className="relative">
                    <FaEnvelope className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      id="pwdEmail"
                      type="email"
                      value={pwdEmail}
                      onChange={(e) => setPwdEmail(e.target.value)}
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
                      placeholder="输入密码"
                      className="pl-10 h-12"
                    />
                  </div>
                </div>

                {error && <p className="text-sm text-red-600">{error}</p>}

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full h-12 bg-blue-500 hover:bg-blue-600 text-white font-medium"
                >
                  {loading ? "登录中..." : "登录"}
                </Button>
              </form>
            )}

            <p className="text-xs text-gray-500 text-center mt-6">
              点击登录即表示您同意{" "}
              <a href="#" className="text-blue-500 hover:underline">
                服务条款
              </a>{" "}
              和{" "}
              <a href="#" className="text-blue-500 hover:underline">
                隐私政策
              </a>
            </p>
          </div>

          <p className="text-center text-sm text-gray-500 mt-6">
            还没有账号？{" "}
            <Link to="/register" className="text-blue-500 font-medium hover:underline">
              去注册
            </Link>
          </p>
        </motion.div>
      </div>
    </>
  );
}
