/**
 * Super OPC Hub API 客户端
 *
 * 连接到后端 FastAPI 服务，提供对话和匹配接口。
 */

import { supabase } from "./supabase";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface DemandData {
  session_id: string;
  project_type: string;
  budget_min: number | null;
  budget_max: number | null;
  timeline: string;
  skills_required: string[];
  description: string;
  collaboration_mode: string;
  industry: string;
  service_expectations: string;
  is_complete: boolean;
  missing_fields: string[];
}

export interface MatchResult {
  id: string;
  name: string;
  avatar_url: string | null;
  role: string;
  description: string | null;
  skills: string[];
  match_rate: number;
  match_reasons: string[];
  is_available: boolean;
}

export interface ChatResponse {
  session_id: string;
  assistant_message: string;
  demand_profile: DemandData | null;
  matches: MatchResult[];
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
): Promise<ChatResponse> {
  const headers = await getAuthHeaders();

  const response = await fetch(`${API_BASE}/api/chat`, {
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

  return response.json() as Promise<ChatResponse>;
}
