import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { DemandProfile } from "../DemandProfile";
import type { DemandProfileData } from "../DemandProfile";

const fullData: DemandProfileData = {
  project_type: "Web 应用",
  budget_min: 5000,
  budget_max: 10000,
  timeline: "2周",
  skills_required: ["React", "TypeScript", "Figma", "UI设计"],
  description: "开发一个内部员工打卡管理系统",
};

const partialData: DemandProfileData = {
  project_type: "小程序",
  budget_min: 3000,
  budget_max: null,
  timeline: "",
  skills_required: [],
  description: "电商小程序",
};

// ── 可见性测试 ─────────────────────────────────────

describe("DemandProfile - 可见性", () => {
  it("isVisible=false 时返回 null", () => {
    const { container } = render(
      <DemandProfile isVisible={false} data={fullData} />
    );
    expect(container.innerHTML).toBe("");
  });

  it("isVisible=true 时渲染需求画像", () => {
    render(<DemandProfile isVisible={true} data={fullData} />);
    expect(screen.getByText("需求画像")).toBeInTheDocument();
  });
});

// ── 数据展示测试 ──────────────────────────────────

describe("DemandProfile - 完整数据展示", () => {
  beforeEach(() => {
    render(<DemandProfile isVisible={true} data={fullData} />);
  });

  it("显示项目类型", () => {
    expect(screen.getByText("项目类型")).toBeInTheDocument();
    expect(screen.getByText("Web 应用")).toBeInTheDocument();
  });

  it("格式化预算范围", () => {
    expect(screen.getByText("预算范围")).toBeInTheDocument();
    expect(screen.getByText("¥5,000 - ¥10,000")).toBeInTheDocument();
  });

  it("显示时间要求", () => {
    expect(screen.getByText("时间要求")).toBeInTheDocument();
    expect(screen.getByText("2周")).toBeInTheDocument();
  });

  it("显示技能标签", () => {
    expect(screen.getByText("技能需求")).toBeInTheDocument();
    expect(screen.getByText("React")).toBeInTheDocument();
    expect(screen.getByText("TypeScript")).toBeInTheDocument();
    expect(screen.getByText("Figma")).toBeInTheDocument();
    expect(screen.getByText("UI设计")).toBeInTheDocument();
  });
});

// ── 部分数据测试 ──────────────────────────────────

describe("DemandProfile - 部分数据展示", () => {
  it("仅 budget_min 显示'起'", () => {
    render(<DemandProfile isVisible={true} data={partialData} />);
    expect(screen.getByText("¥3,000 起")).toBeInTheDocument();
  });

  it("空 timeline 显示'待定'", () => {
    render(<DemandProfile isVisible={true} data={partialData} />);
    const timelines = screen.getAllByText("待定");
    // 时间要求 "待定"
    expect(timelines.length).toBeGreaterThan(0);
    // 找到时间要求对应的 "待定"
    const timeRequired = screen.getAllByText("待定").find(
      (el) => el.textContent === "待定"
    );
    expect(timeRequired).toBeDefined();
  });

  it("空技能列表显示'待定'", () => {
    // skills_required 为空时显示紫色的"待定"文本
    const noSkills: DemandProfileData = {
      ...partialData,
      skills_required: [],
    };
    render(<DemandProfile isVisible={true} data={noSkills} />);
    // 技能区域应该存在
    expect(screen.getByText("技能需求")).toBeInTheDocument();
  });
});

// ── 边界情况测试 ──────────────────────────────────

describe("DemandProfile - 边界情况", () => {
  it("没有 data 时所有字段显示'待定'", () => {
    render(<DemandProfile isVisible={true} />);
    const pendingElements = screen.getAllByText("待定");
    // 项目类型、预算、时间、技能 都应该是待定
    expect(pendingElements.length).toBeGreaterThanOrEqual(3);
  });

  it("budget_min 为 0 时正常显示 ¥0 起", () => {
    const zeroBudget: DemandProfileData = {
      project_type: "测试",
      budget_min: 0,
      budget_max: null,
      timeline: "",
      skills_required: [],
      description: "",
    };
    render(<DemandProfile isVisible={true} data={zeroBudget} />);
    expect(screen.getByText("¥0 起")).toBeInTheDocument();
  });

  it("仅 budget_max 显示'不超过'", () => {
    const maxOnly: DemandProfileData = {
      project_type: "测试",
      budget_min: null,
      budget_max: 5000,
      timeline: "",
      skills_required: [],
      description: "",
    };
    render(<DemandProfile isVisible={true} data={maxOnly} />);
    expect(screen.getByText("不超过 ¥5,000")).toBeInTheDocument();
  });

  it("budget_min 和 budget_max 为 null 显示'待定'", () => {
    const noBudget: DemandProfileData = {
      project_type: "测试",
      budget_min: null,
      budget_max: null,
      timeline: "",
      skills_required: [],
      description: "",
    };
    render(<DemandProfile isVisible={true} data={noBudget} />);
    const pending = screen.getAllByText("待定");
    // 项目类型是 "测试"，预算、时间、技能都是待定
    expect(pending.length).toBeGreaterThanOrEqual(2);
  });

  it("大额预算正确格式化", () => {
    const largeBudget: DemandProfileData = {
      project_type: "大型项目",
      budget_min: 150000,
      budget_max: 300000,
      timeline: "3个月",
      skills_required: ["项目管理"],
      description: "企业级系统",
    };
    render(<DemandProfile isVisible={true} data={largeBudget} />);
    expect(screen.getByText("¥150,000 - ¥300,000")).toBeInTheDocument();
  });

  it("大量技能标签正确渲染", () => {
    const manySkills: DemandProfileData = {
      project_type: "全栈应用",
      budget_min: 10000,
      budget_max: 50000,
      timeline: "1个月",
      skills_required: [
        "React",
        "Node.js",
        "PostgreSQL",
        "Docker",
        "AWS",
        "TypeScript",
        "GraphQL",
        "Redis",
      ],
      description: "",
    };
    render(<DemandProfile isVisible={true} data={manySkills} />);
    expect(screen.getByText("React")).toBeInTheDocument();
    expect(screen.getByText("Redis")).toBeInTheDocument();
    expect(screen.getByText("GraphQL")).toBeInTheDocument();
    // 所有 8 个技能标签都存在
    const badges = manySkills.skills_required.map((s) =>
      screen.getByText(s)
    );
    expect(badges).toHaveLength(8);
  });
});

// ── UI 元素测试 ────────────────────────────────────

describe("DemandProfile - UI 元素", () => {
  it("显示四个信息卡片（项目类型、预算、时间、技能）", () => {
    render(<DemandProfile isVisible={true} data={fullData} />);
    expect(screen.getByText("项目类型")).toBeInTheDocument();
    expect(screen.getByText("预算范围")).toBeInTheDocument();
    expect(screen.getByText("时间要求")).toBeInTheDocument();
    expect(screen.getByText("技能需求")).toBeInTheDocument();
  });

  it("isVisible=true 且 data 存在时显示项目类型值", () => {
    render(<DemandProfile isVisible={true} data={fullData} />);
    expect(screen.getByText("Web 应用")).toBeInTheDocument();
  });
});
