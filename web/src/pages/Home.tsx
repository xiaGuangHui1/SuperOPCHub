import { useState } from "react";
import { PageMeta } from "@/components/common/PageMeta";
import { Header } from "@/components/generated/Header";
import { ChatInterface } from "@/components/generated/ChatInterface";
import { DemandProfile, type DemandProfileData } from "@/components/generated/DemandProfile";
import { OPCMatchCard } from "@/components/generated/OPCMatchCard";
import type { DemandProfileV2, MatchResultV2 } from "@/lib/api";

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

  const handleDemandUpdate = (demand: DemandProfileV2) => {
    setDemandData({
      project_type: demand.primary_need?.value || "",
      budget_min: demand.estimated_budget_range?.value?.min ?? null,
      budget_max: demand.estimated_budget_range?.value?.max ?? null,
      timeline: demand.timeline?.value || "",
      skills_required: demand.required_skills?.value || [],
      description: demand.description?.value || "",
      collaboration_mode: "",
      industry: demand.industry?.value || demand.domain?.value || "",
      service_expectations: "",
      overall_confidence: demand.overall_confidence,
    });
    setShowDemandProfile(true);
  };

  const handleMatchResults = (matches: MatchResultV2[]) => {
    setOpcMatches(
      matches.map((m) => ({
        id: m.opc_id,
        name: m.name,
        avatar: m.avatar_url || "",
        role: m.role,
        matchRate: m.match_score,
        description: m.description || "",
        skills: m.skills,
      })),
    );
    setShowOPCMatches(true);
  };

  return (
    <>
      <PageMeta
        title="Super OPC Hub - AI 驱动的合作对接平台"
        description="通过 AI 对话探索想法、明确需求，精准对接适合的 OPC 一人公司"
        keywords={["OPC", "合作对接", "AI 对话", "一人公司", "独立开发者", "设计师"]}
      />
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white pb-20">
        <Header />
        <main className="pt-20 px-4 sm:px-6">
          <div className="text-center mb-8">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-700 mb-3 sm:mb-4 tracking-tight">
              Super OPC Hub
            </h2>
            <p className="text-gray-500 text-base sm:text-lg lg:text-xl max-w-2xl mx-auto font-medium px-2">
              通过 AI 对话探索想法、明确需求，精准对接合适的 OPC 一人公司
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
}
