import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { OPCMatchCard } from "../OPCMatchCard";

const baseProfile = {
  id: "opc-1",
  name: "张三",
  avatar: "https://example.com/avatar.jpg",
  role: "UI 设计师",
  matchRate: 92,
  description: "5年UI/UX设计经验，擅长Figma和Sketch",
  skills: ["Figma", "Sketch", "UI设计", "原型制作"],
};

const profiles = [
  baseProfile,
  {
    id: "opc-2",
    name: "李四",
    avatar: "https://example.com/avatar2.jpg",
    role: "前端开发",
    matchRate: 78,
    description: "React 高级开发，5年经验",
    skills: ["React", "TypeScript"],
  },
  {
    id: "opc-3",
    name: "王五",
    avatar: "https://example.com/avatar3.jpg",
    role: "全栈工程师",
    matchRate: 65,
    description: "全栈开发，Node.js + React",
    skills: ["React", "Node.js", "PostgreSQL"],
  },
];

// ── 可见性测试 ─────────────────────────────────────

describe("OPCMatchCard - 可见性", () => {
  it("isVisible=false 时返回 null，不渲染任何内容", () => {
    const { container } = render(
      <OPCMatchCard profiles={profiles} isVisible={false} />
    );
    expect(container.innerHTML).toBe("");
  });

  it("isVisible=true 时渲染匹配卡片", () => {
    render(<OPCMatchCard profiles={profiles} isVisible={true} />);
    expect(screen.getByText("为您匹配的专业人士")).toBeInTheDocument();
  });
});

// ── 标题和描述测试 ──────────────────────────────────

describe("OPCMatchCard - 标题区域", () => {
  it("渲染标题'为您匹配的专业人士'", () => {
    render(<OPCMatchCard profiles={profiles} isVisible={true} />);
    expect(
      screen.getByRole("heading", { name: "为您匹配的专业人士" })
    ).toBeInTheDocument();
  });

  it("渲染副标题描述", () => {
    render(<OPCMatchCard profiles={profiles} isVisible={true} />);
    expect(screen.getByText(/智能匹配最适合的 OPC 专家/)).toBeInTheDocument();
  });
});

// ── 卡片内容测试 ──────────────────────────────────

describe("OPCMatchCard - 卡片内容", () => {
  it("每个 profile 渲染一个卡片", () => {
    render(<OPCMatchCard profiles={profiles} isVisible={true} />);
    expect(screen.getByText("张三")).toBeInTheDocument();
    expect(screen.getByText("李四")).toBeInTheDocument();
    expect(screen.getByText("王五")).toBeInTheDocument();
  });

  it("显示每个 OPC 的角色", () => {
    render(<OPCMatchCard profiles={profiles} isVisible={true} />);
    expect(screen.getByText("UI 设计师")).toBeInTheDocument();
    expect(screen.getByText("前端开发")).toBeInTheDocument();
    expect(screen.getByText("全栈工程师")).toBeInTheDocument();
  });

  it("显示匹配度百分比", () => {
    render(<OPCMatchCard profiles={profiles} isVisible={true} />);
    expect(screen.getByText("92%")).toBeInTheDocument();
    expect(screen.getByText("78%")).toBeInTheDocument();
    expect(screen.getByText("65%")).toBeInTheDocument();
  });

  it("显示 OPC 描述文本", () => {
    render(<OPCMatchCard profiles={profiles} isVisible={true} />);
    expect(
      screen.getByText("5年UI/UX设计经验，擅长Figma和Sketch")
    ).toBeInTheDocument();
  });

  it("显示技能标签", () => {
    render(<OPCMatchCard profiles={profiles} isVisible={true} />);
    expect(screen.getByText("Figma")).toBeInTheDocument();
    expect(screen.getByText("Sketch")).toBeInTheDocument();
    expect(screen.getByText("UI设计")).toBeInTheDocument();
    expect(screen.getByText("原型制作")).toBeInTheDocument();
    // "React" 出现在两个 OPC 的技能列表中，用 getAllByText
    expect(screen.getAllByText("React")).toHaveLength(2);
    expect(screen.getByText("TypeScript")).toBeInTheDocument();
  });

  it("每个卡片显示'查看详情'按钮", () => {
    render(<OPCMatchCard profiles={profiles} isVisible={true} />);
    const buttons = screen.getAllByText("查看详情");
    expect(buttons).toHaveLength(3);
  });

  it("渲染 OPC 头像", () => {
    render(<OPCMatchCard profiles={profiles} isVisible={true} />);
    const avatars = screen.getAllByRole("img");
    expect(avatars).toHaveLength(3);
    expect(avatars[0]).toHaveAttribute("src", "https://example.com/avatar.jpg");
    expect(avatars[0]).toHaveAttribute("alt", "张三");
  });
});

// ── 边界情况测试 ──────────────────────────────────

describe("OPCMatchCard - 边界情况", () => {
  it("空 profiles 数组不渲染卡片", () => {
    render(<OPCMatchCard profiles={[]} isVisible={true} />);
    expect(screen.queryByText("查看详情")).not.toBeInTheDocument();
  });

  it("matchRate=0 显示 0%", () => {
    const lowProfile = [{ ...baseProfile, id: "low", matchRate: 0 }];
    render(<OPCMatchCard profiles={lowProfile} isVisible={true} />);
    expect(screen.getByText("0%")).toBeInTheDocument();
  });

  it("matchRate=100 显示 100%", () => {
    const highProfile = [{ ...baseProfile, id: "high", matchRate: 100 }];
    render(<OPCMatchCard profiles={highProfile} isVisible={true} />);
    expect(screen.getByText("100%")).toBeInTheDocument();
  });

  it("空技能列表正常渲染", () => {
    const noSkills = [{ ...baseProfile, id: "ns", skills: [] }];
    render(<OPCMatchCard profiles={noSkills} isVisible={true} />);
    // 技能标签区域没有内容，卡片本身应该渲染
    expect(screen.getByText("张三")).toBeInTheDocument();
  });

  it("空描述正常渲染", () => {
    const noDesc = [{ ...baseProfile, id: "nd", description: "" }];
    render(<OPCMatchCard profiles={noDesc} isVisible={true} />);
    expect(screen.getByText("张三")).toBeInTheDocument();
  });

  it("大量技能标签正确渲染", () => {
    const manySkills = [
      {
        ...baseProfile,
        id: "many",
        skills: ["Figma", "Sketch", "PS", "AI", "XD", "Framer", "Webflow"],
      },
    ];
    render(<OPCMatchCard profiles={manySkills} isVisible={true} />);
    expect(screen.getByText("Figma")).toBeInTheDocument();
    expect(screen.getByText("Webflow")).toBeInTheDocument();
  });

  it("单个 profile 渲染单个卡片", () => {
    render(
      <OPCMatchCard profiles={[baseProfile]} isVisible={true} />
    );
    expect(screen.getByText("张三")).toBeInTheDocument();
    const buttons = screen.getAllByText("查看详情");
    expect(buttons).toHaveLength(1);
  });
});
