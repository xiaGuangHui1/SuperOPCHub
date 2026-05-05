import { describe, it, expect, vi, beforeEach } from "vitest";
import { sendChatMessage } from "../api";
import type { ChatMessage } from "../api";

// Mock supabase auth
vi.mock("../supabase", () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({
        data: { session: null },
      }),
    },
  },
}));

const API_BASE = "http://localhost:8000";

function mockFetchResponse(status: number, body: unknown) {
  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    text: () => Promise.resolve(JSON.stringify(body)),
    json: () => Promise.resolve(body),
  });
}

function getFetchBody() {
  const call = (globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls[0];
  return JSON.parse(call[1].body);
}

describe("sendChatMessage", () => {
  const sessionId = "session_1234567890_abc123";
  const messages: ChatMessage[] = [
    { role: "user", content: "我需要一个网页设计" },
    { role: "assistant", content: "好的，请具体说一下" },
  ];

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  // ── 正常响应测试 ──────────────────────────────────

  it("发送消息并返回完整 ChatResponse", async () => {
    const mockResponse = {
      session_id: sessionId,
      assistant_message: "您的需求我已了解，即将为您匹配",
      demand_profile: {
        session_id: sessionId,
        project_type: "Web 设计",
        budget_min: 300,
        budget_max: null,
        timeline: "1周",
        skills_required: ["Figma", "UI设计"],
        description: "两个页面的网页设计",
        is_complete: true,
        missing_fields: [],
      },
      matches: [],
      is_matching_complete: false,
    };
    mockFetchResponse(200, mockResponse);

    const result = await sendChatMessage(sessionId, messages);

    expect(globalThis.fetch).toHaveBeenCalledTimes(1);
    expect(result.session_id).toBe(sessionId);
    expect(result.assistant_message).toContain("即将为您匹配");
    expect(result.demand_profile).not.toBeNull();
    expect(result.demand_profile!.project_type).toBe("Web 设计");
  });

  it("正确构造请求体（session_id, messages, user_id）", async () => {
    mockFetchResponse(200, {
      session_id: sessionId,
      assistant_message: "",
      demand_profile: null,
      matches: [],
      is_matching_complete: false,
    });

    await sendChatMessage(sessionId, messages, "user-1");

    const body = getFetchBody();
    expect(body).toEqual({
      session_id: sessionId,
      messages: [
        { role: "user", content: "我需要一个网页设计" },
        { role: "assistant", content: "好的，请具体说一下" },
      ],
      user_id: "user-1",
    });
  });

  // ── 匹配结果测试 ──────────────────────────────────

  it("解析带匹配结果的响应", async () => {
    const matchResult = {
      id: "opc-1",
      name: "张三",
      avatar_url: "https://example.com/avatar.jpg",
      role: "UI 设计师",
      description: "5年UI设计经验",
      skills: ["Figma", "Sketch", "UI设计"],
      match_rate: 92.5,
      match_reasons: ["技能高度匹配：Figma, UI设计"],
      is_available: true,
    };

    mockFetchResponse(200, {
      session_id: sessionId,
      assistant_message: "为您找到以下匹配人选",
      demand_profile: null,
      matches: [matchResult],
      is_matching_complete: true,
    });

    const result = await sendChatMessage(sessionId, messages);

    expect(result.matches).toHaveLength(1);
    expect(result.matches[0].name).toBe("张三");
    expect(result.matches[0].match_rate).toBe(92.5);
    expect(result.is_matching_complete).toBe(true);
  });

  it("解析多个匹配结果", async () => {
    const matches = [
      { id: "1", name: "张三", avatar_url: null, role: "设计师", description: null, skills: ["Figma"], match_rate: 90, match_reasons: [], is_available: true },
      { id: "2", name: "李四", avatar_url: null, role: "开发者", description: null, skills: ["React"], match_rate: 75, match_reasons: [], is_available: true },
      { id: "3", name: "王五", avatar_url: null, role: "PM", description: null, skills: ["管理"], match_rate: 60, match_reasons: [], is_available: false },
    ];

    mockFetchResponse(200, {
      session_id: sessionId,
      assistant_message: "",
      demand_profile: null,
      matches,
      is_matching_complete: true,
    });

    const result = await sendChatMessage(sessionId, messages);

    expect(result.matches).toHaveLength(3);
    expect(result.matches[0].id).toBe("1");
    expect(result.matches[2].is_available).toBe(false);
  });

  // ── 边界情况测试 ──────────────────────────────────

  it("处理空 matches 数组", async () => {
    mockFetchResponse(200, {
      session_id: sessionId,
      assistant_message: "请输入更多需求信息",
      demand_profile: null,
      matches: [],
      is_matching_complete: false,
    });

    const result = await sendChatMessage(sessionId, messages);

    expect(result.matches).toEqual([]);
  });

  it("处理 demand_profile 为 null", async () => {
    mockFetchResponse(200, {
      session_id: sessionId,
      assistant_message: "请描述您的需求",
      demand_profile: null,
      matches: [],
      is_matching_complete: false,
    });

    const result = await sendChatMessage(sessionId, messages);

    expect(result.demand_profile).toBeNull();
  });

  it("处理空消息列表", async () => {
    mockFetchResponse(200, {
      session_id: sessionId,
      assistant_message: "您好，请描述您的需求",
      demand_profile: null,
      matches: [],
      is_matching_complete: false,
    });

    const result = await sendChatMessage(sessionId, []);

    expect(result.assistant_message).toBeTruthy();
  });

  // ── 错误处理测试 ──────────────────────────────────

  it("API 返回非 2xx 时抛出错误", async () => {
    mockFetchResponse(500, { detail: "Internal Server Error" });

    await expect(sendChatMessage(sessionId, messages)).rejects.toThrow(
      "API error 500"
    );
  });

  it("API 返回 401 时抛出错误", async () => {
    mockFetchResponse(401, { detail: "Unauthorized" });

    await expect(sendChatMessage(sessionId, messages)).rejects.toThrow(
      "API error 401"
    );
  });

  it("请求中包含 Content-Type application/json 头", async () => {
    mockFetchResponse(200, {
      session_id: sessionId,
      assistant_message: "",
      demand_profile: null,
      matches: [],
      is_matching_complete: false,
    });

    await sendChatMessage(sessionId, messages);

    const call = (globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls[0];
    expect(call[1].headers!["Content-Type"]).toBe("application/json");
    expect(call[1].method).toBe("POST");
  });

  it("URL 后缀为 /api/chat", async () => {
    mockFetchResponse(200, {
      session_id: sessionId,
      assistant_message: "",
      demand_profile: null,
      matches: [],
      is_matching_complete: false,
    });

    await sendChatMessage(sessionId, messages);

    const call = (globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls[0];
    expect(call[0]).toBe(`${API_BASE}/api/chat`);
  });
});
