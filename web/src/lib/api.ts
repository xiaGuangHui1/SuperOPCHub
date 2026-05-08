/**
 * Super OPC Hub API 客户端
 *
 * 连接到后端 FastAPI 服务，提供对话和匹配接口。
 * V2 版本：直接使用 chat-v2 端点的 Enhanced 数据结构。
 */

import { supabase } from "./supabase";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

// ─── V2 推理维度 ──────────────────────────────────────

export interface InferenceDim {
  value: string;
  confidence: number;
  sources: string[];
  verified: boolean;
}

export interface SkillsDim {
  value: string[];
  confidence: number;
  mandatory: string[];
  optional: string[];
}

export interface BudgetDim {
  value: { min: number | null; max: number | null };
  confidence: number;
}

// ─── V2 需求画像 ─────────────────────────────────────

export interface DemandProfileV2 {
  session_id: string;
  primary_need: InferenceDim;
  domain: InferenceDim;
  required_skills: SkillsDim;
  complexity: InferenceDim;
  estimated_budget_range: BudgetDim;
  timeline: InferenceDim;
  industry: InferenceDim;
  description: InferenceDim;
  overall_confidence: number;
  exit_reason: string;
  ux_message: string;
}

// ─── V2 匹配结果 ─────────────────────────────────────

export interface MatchDetailV2 {
  semantic_similarity: number;
  skill_match: number;
  experience_match: number;
  reputation_score: number;
  response_score: number;
  budget_match: number;
  confidence_penalty: number;
  final_score: number;
}

export interface MatchResultV2 {
  opc_id: string;
  name: string;
  avatar_url: string | null;
  role: string;
  description: string | null;
  skills: string[];
  match_score: number;
  match_reasons: string[];
  match_detail: MatchDetailV2;
  is_available: boolean;
}

export interface ChatResponseV2 {
  session_id: string;
  assistant_message: string;
  demand_profile: DemandProfileV2 | null;
  matches: MatchResultV2[];
  is_matching_complete: boolean;
}

async function getAuthHeaders(): Promise<Record<string, string>> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  try {
    const { data } = await supabase.auth.getSession();
    if (data.session?.access_token) {
      headers["Authorization"] = `Bearer ${data.session.access_token}`;
    }
  } catch {
    // 未登录时不附加 token
  }

  return headers;
}

export async function sendChatMessage(
  sessionId: string,
  messages: ChatMessage[],
  userId?: string,
): Promise<ChatResponseV2> {
  const headers = await getAuthHeaders();

  const response = await fetch(`${API_BASE}/api/chat-v2`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      session_id: sessionId,
      messages,
      user_id: userId,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error ${response.status}: ${errorText}`);
  }

  return response.json() as Promise<ChatResponseV2>;
}
