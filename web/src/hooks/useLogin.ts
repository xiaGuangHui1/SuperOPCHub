import { supabase } from "@/lib/supabase";
import { useState } from "react";

type LoginMethod = "email" | "phone";

interface OTPLoginState {
  loading: boolean;
  error: string | null;
  otpSent: boolean;
}

export function useLogin(returnUrl: string) {
  const [state, setState] = useState<OTPLoginState>({
    loading: false,
    error: null,
    otpSent: false,
  });

  // ── OTP 验证码登录 ──────────────────────────

  const sendOTP = async (identifier: string, method: LoginMethod) => {
    setState({ loading: true, error: null, otpSent: false });

    try {
      const options = {
        emailRedirectTo: returnUrl,
      };

      const { error } = await supabase.auth.signInWithOtp(
        method === "email"
          ? { email: identifier, options }
          : { phone: identifier },
      );

      if (error) throw error;

      setState({ loading: false, error: null, otpSent: true });
      return true;
    } catch (err) {
      setState({
        loading: false,
        error: err instanceof Error ? err.message : "发送失败",
        otpSent: false,
      });
      return false;
    }
  };

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
        error: err instanceof Error ? err.message : "验证失败",
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
        error: err instanceof Error ? err.message : "登录失败",
        otpSent: false,
      });
      return false;
    }
  };

  // ── 邮箱 + 密码注册 ─────────────────────────

  const signUp = async (email: string, password: string) => {
    setState({ loading: true, error: null, otpSent: false });

    try {
      const { error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: `${window.location.origin}${returnUrl}`,
        },
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
        error: err instanceof Error ? err.message : "注册失败",
        otpSent: false,
      });
      return false;
    }
  };

  const reset = () => {
    setState({ loading: false, error: null, otpSent: false });
  };

  return { ...state, sendOTP, verifyOTP, signInWithPassword, signUp, reset };
}
