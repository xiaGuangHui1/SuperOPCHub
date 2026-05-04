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
  if (message.includes("only request this after") || message.includes("security purposes")) {
    return "操作太频繁，请稍后再试";
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
   * 注册 + 自动登录：
   * signUp 在 email confirmation 关闭时会直接返回 session；
   * 开启时会返回 null session（需要用户点击确认邮件）。
   * 注册成功用 window.location.assign 做整页重载，
   * 确保 useAuth 挂载时 getSession() 能从 localStorage 读到 session。
   */
  const signUp = async (email: string, password: string) => {
    setState({ loading: true, error: null, otpSent: false });

    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
      });

      if (error) throw error;

      // data.user 为 null → 邮箱已注册（Supabase 安全设计，不返回错误）
      if (!data.user) {
        setState({
          loading: false,
          error: "该邮箱已注册，请直接登录",
          otpSent: false,
        });
        return false;
      }

      // 用户创建成功，返回 true 由调用方决定后续跳转
      setState({ loading: false, error: null, otpSent: false });
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
