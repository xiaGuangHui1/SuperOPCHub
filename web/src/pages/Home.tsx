import { useState } from "react";
import { PageMeta } from "@/components/common/PageMeta";
import { Header } from "@/components/generated/Header";
import { ChatInterface } from "@/components/generated/ChatInterface";
import { DemandProfile, type DemandProfileData } from "@/components/generated/DemandProfile";
import { OPCMatchCard } from "@/components/generated/OPCMatchCard";
import type { DemandData, MatchResult } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export default function Home() {
  const [showDemandProfile, setShowDemandProfile] = useState(false);
  const [showOPCMatches, setShowOPCMatches] = useState(false);
  const [demandData, setDemandData] = useState<DemandProfileData | undefined>();
  const [opcMatches, setOpcMatches] = useState<OpcProfile[]>([]);

  const handleDemandSubmit = (_messages: Message[]) => {
    setShowDemandProfile(true);
  };

  const handleDemandUpdate = (demand: DemandData) => {
    setDemandData({
      project_type: demand.project_type,
      budget_min: demand.budget_min,
      budget_max: demand.budget_max,
      timeline: demand.timeline,
      skills_required: demand.skills_required,
      description: demand.description,
      collaboration_mode: demand.collaboration_mode,
      industry: demand.industry,
      service_expectations: demand.service_expectations,
    });
    setShowDemandProfile(true);
  };

  const handleMatchResults = (matches: MatchResult[]) => {
    setOpcMatches(
      matches.map((m) => ({
        id: m.id,
        name: m.name,
        avatar: m.avatar_url || "",
        role: m.role,
        matchRate: m.match_rate,
        description: m.description || "",
        skills: m.skills,
        matchReasons: m.match_reasons || [],
      })),
    );
    setShowOPCMatches(true);
  };

  return (
    <>
      <PageMeta
        title="Super OPC Hub - 搜索找到能胜任的人"
        description="描述你的需求，帮你搜索个人网站，找到最能胜任的人"
        keywords={["OPC", "搜索", "匹配", "个人网站", "独立开发者", "设计师"]}
      />
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white pb-20">
        <Header />
        <main className="pt-20 px-4 sm:px-6">
          <div className="text-center mb-8">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-700 mb-3 sm:mb-4 tracking-tight">
              Super OPC Hub
            </h2>
            <p className="text-gray-500 text-base sm:text-lg lg:text-xl max-w-2xl mx-auto font-medium px-2">
              说出你想做的事，帮你找到全网最能胜任的人
            </p>
          </div>

          <ChatInterface
            onDemandSubmit={handleDemandSubmit}
            onDemandUpdate={handleDemandUpdate}
            onMatchResults={handleMatchResults}
          />
          <DemandProfile isVisible={showDemandProfile} data={demandData} />
          <OPCMatchCard profiles={opcMatches} isVisible={showOPCMatches} />
        </main>
      </div>
    </>
  );
}

/* OPCMatchCard 依赖的接口 */
interface OpcProfile {
  id: string;
  name: string;
  avatar: string;
  role: string;
  matchRate: number;
  description: string;
  skills: string[];
  matchReasons: string[];
}
