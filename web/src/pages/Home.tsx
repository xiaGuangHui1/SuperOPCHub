import { useState } from "react";
import { PageMeta } from "@/components/common/PageMeta";
import { Header } from "@/components/generated/Header";
import { ChatInterface } from "@/components/generated/ChatInterface";
import { DemandProfile } from "@/components/generated/DemandProfile";
import { OPCMatchCard } from "@/components/generated/OPCMatchCard";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function Home() {
  const [showDemandProfile, setShowDemandProfile] = useState(false);
  const [showOPCMatches, setShowOPCMatches] = useState(false);

  const handleDemandSubmit = (_messages: Message[]) => {
    setShowDemandProfile(true);
    setTimeout(() => {
      setShowOPCMatches(true);
    }, 500);
  };

  const opcProfiles = [
    {
      id: "1",
      name: "张设计师",
      avatar: "https://ui-avatars.com/api/?name=%E5%BC%A0%E8%AE%BE%E8%AE%A1%E5%B8%88&background=8B5CF6&color=fff&size=200&bold=true",
      role: "资深 UI 设计师",
      matchRate: 95,
      description: "5 年企业官网设计经验，擅长现代简约风格，服务过 50+ 知名企业客户",
      skills: ["UI 设计", "Figma", "品牌设计"],
    },
    {
      id: "2",
      name: "李开发者",
      avatar: "https://ui-avatars.com/api/?name=%E6%9D%8E%E5%BC%80%E5%8F%91%E8%80%85&background=10B981&color=fff&size=200&bold=true",
      role: "全栈开发者",
      matchRate: 92,
      description: "精通 React/Vue 技术栈，专注响应式网站开发，交付项目 100+ 个",
      skills: ["React", "TypeScript", "Node.js"],
    },
    {
      id: "3",
      name: "王设计师",
      avatar: "https://ui-avatars.com/api/?name=%E7%8E%8B%E8%AE%BE%E8%AE%A1%E5%B8%88&background=3B82F6&color=fff&size=200&bold=true",
      role: "创意设计师",
      matchRate: 88,
      description: "擅长创意视觉设计，多次获得设计奖项，作品风格独特富有创意",
      skills: ["视觉设计", "动效设计", "插画"],
    },
    {
      id: "4",
      name: "陈工程师",
      avatar: "https://ui-avatars.com/api/?name=%E9%99%88%E5%B7%A5%E7%A8%8B%E5%B8%88&background=6366F1&color=fff&size=200&bold=true",
      role: "后端工程师",
      matchRate: 90,
      description: "8 年后端开发经验，擅长高并发系统设计，熟悉云原生架构",
      skills: ["Java", "Python", "Kubernetes"],
    },
    {
      id: "5",
      name: "刘产品经理",
      avatar: "https://ui-avatars.com/api/?name=%E5%88%98%E4%BA%A7%E5%93%81%E7%BB%8F%E7%90%86&background=F59E0B&color=fff&size=200&bold=true",
      role: "资深产品经理",
      matchRate: 87,
      description: "10 年互联网产品经验，擅长从 0 到 1 打造爆款产品",
      skills: ["产品规划", "用户研究", "数据分析"],
    },
    {
      id: "6",
      name: "赵前端",
      avatar: "https://ui-avatars.com/api/?name=%E8%B5%B5%E5%89%8D%E7%AB%AF&background=EC4899&color=fff&size=200&bold=true",
      role: "前端专家",
      matchRate: 89,
      description: "专注前端性能优化，擅长大型单页应用架构设计",
      skills: ["Vue", "Webpack", "性能优化"],
    },
    {
      id: "7",
      name: "孙 UX 设计师",
      avatar: "https://ui-avatars.com/api/?name=%E5%AD%99UX%E8%AE%BE%E8%AE%A1%E5%B8%88&background=14B8A6&color=fff&size=200&bold=true",
      role: "UX 体验设计师",
      matchRate: 86,
      description: "以用户为中心的设计理念，擅长交互设计和用户旅程规划",
      skills: ["交互设计", "原型制作", "用户测试"],
    },
    {
      id: "8",
      name: "周移动端",
      avatar: "https://ui-avatars.com/api/?name=%E5%91%A8%E7%A7%BB%E5%8A%A8%E7%AB%AF&background=F97316&color=fff&size=200&bold=true",
      role: "移动端开发者",
      matchRate: 85,
      description: "精通 iOS 和 Android 原生开发，也有丰富的跨平台项目经验",
      skills: ["Swift", "Kotlin", "Flutter"],
    },
  ];

  return (
    <>
      <PageMeta
        title="Super OPC Hub - AI 驱动的需求匹配平台"
        description="通过 AI 对话帮助甲方和乙方探索创意、明确需求，并智能匹配适合的 OPC 画像"
        keywords={["OPC", "需求匹配", "AI 对话", "设计师", "开发者"]}
      />
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white pb-20">
        <Header />
        <main className="pt-20 px-4 sm:px-6">
          <div className="text-center mb-8">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-700 mb-3 sm:mb-4 tracking-tight">
              Super OPC Hub
            </h2>
            <p className="text-gray-500 text-base sm:text-lg lg:text-xl max-w-2xl mx-auto font-medium px-2">
              通过 AI 对话探索创意、明确需求，智能匹配最适合的专业人士
            </p>
          </div>

          <ChatInterface onDemandSubmit={handleDemandSubmit} />
          <DemandProfile isVisible={showDemandProfile} />
          <OPCMatchCard profiles={opcProfiles} isVisible={showOPCMatches} />
        </main>
      </div>
    </>
  );
}
