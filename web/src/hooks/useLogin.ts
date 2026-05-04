import { supabase } from "@/lib/supabase";
import { useState } from "react";

type LoginMethod = "email" | "phone";

interface OTPLoginState {
  loading: boolean;
  error: string | null;
  otpSent: boolean;
}

/** 翻译 Supabase 常见错误为中文 */
function translateError(message: string): string {
  if (message.includes("rate limit")) {
    return "邮件发送太频繁，请稍后再试";
  }
  if (message.includes("already registered") || message.includes("already exists")) {
    return "该邮箱已注册，请直接登录";
  }
  if (message.includes("Invalid login credentials")) {
    return "邮箱或密码错误";
  }
  if (message.includes("token has expired") || message.includes("expired")) {
    return "验证码已过期，请重新获取";
  }
  if (message.includes("token is invalid")) {
    return "验证码错误，请检查后重试";
  }
  return message;
}

export function useLogin(returnUrl: string) {
  const [state, setState] = useState<OTPLoginState>({
    loading: false,
    error: null,
    otpSent: false,
  });

  // ── OTP 验证码发送 ──────────────────────────

  const sendOTP = async (identifier: string, method: LoginMethod) => {
    setState({ loading: true, error: null, otpSent: false });

    try {
      const { error } = await supabase.auth.signInWithOtp(
        method === "email"
          ? { email: identifier }
          : { phone: identifier },
      );

      if (error) throw error;

      setState({ loading: false, error: null, otpSent: true });
      return true;
    } catch (err) {
      setState({
        loading: false,
        error: translateError(err instanceof Error ? err.message : "发送失败"),
        otpSent: false,
      });
      return false;
    }
  };

  // ── OTP 验证码验证（登录用，验证后直接跳转）───

  const verifyOTP = async (
    identifier: string,
    token: string,
    method: LoginMethod,
  ) => {
    setState({ ...state, loading: true, error: null });

    try {
      const { error } = await supabase.auth.verifyOtp(
        method === "email"
          ? { email: identifier, token, type: "email" }
          : { phone: identifier, token, type: "sms" },
      );

      if (error) throw error;

      setState({ loading: false, error: null, otpSent: true });

      if (returnUrl) {
        window.location.assign(returnUrl);
      }

      return true;
    } catch (err) {
      setState({
        ...state,
        loading: false,
        error: translateError(err instanceof Error ? err.message : "验证失败"),
      });
      return false;
    }
  };

  // ── 邮箱 + 密码登录 ─────────────────────────

  const signInWithPassword = async (email: string, password: string) => {
    setState({ loading: true, error: null, otpSent: false });

    try {
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) throw error;

      setState({ loading: false, error: null, otpSent: false });

      if (returnUrl) {
        window.location.assign(returnUrl);
      }

      return true;
    } catch (err) {
      setState({
        loading: false,
        error: translateError(err instanceof Error ? err.message : "登录失败"),
        otpSent: false,
      });
      return false;
    }
  };

  // ── 邮箱 + 密码注册 ─────────────────────────

  /**
   * 直接调用 signUp 创建持久账号。
   * 强制 signOut 清空旧会话，确保用新账号登录。
   */
  const signUp = async (email: string, password: string) => {
    setState({ loading: true, error: null, otpSent: false });

    try {
      // 先登出旧会话，避免状态冲突
      await supabase.auth.signOut();

      const { error } = await supabase.auth.signUp({
        email,
        password,
      });

      if (error) throw error;

      setState({ loading: false, error: null, otpSent: false });

      if (returnUrl) {
        window.location.assign(returnUrl);
      }

      return true;
    } catch (err) {
      setState({
        loading: false,
        error: translateError(err instanceof Error ? err.message : "注册失败"),
        otpSent: false,
      });
      return false;
    }
  };

  const reset = () => {
    setState({ loading: false, error: null, otpSent: false });
  };

  return {
    ...state,
    sendOTP,
    verifyOTP,
    signInWithPassword,
    signUp,
    reset,
  };
}
