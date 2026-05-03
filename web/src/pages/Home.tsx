import { useState } from "react";
import { PageMeta } from "@/components/common/PageMeta";
import { Header } from "@/components/generated/Header";
import { ChatInterface } from "@/components/generated/ChatInterface";
import { DemandProfile, type DemandProfileData } from "@/components/generated/DemandProfile";
import { OPCMatchCard } from "@/components/generated/OPCMatchCard";
import type { MatchResult } from "@/lib/api";

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

  const handleDemandUpdate = (demand: DemandProfileData) => {
    setDemandData(demand);
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
      })),
    );
    setShowOPCMatches(true);
  };

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
