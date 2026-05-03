import { useState } from "react";
import { PageMeta } from "@/components/common/PageMeta";
import { motion } from "framer-motion";

interface Node {
  id: string;
  name: string;
  level: number;
  active: boolean;
  opcCount: number;
  children?: Node[];
  x?: number;
  y?: number;
}

const initialData: Node = {
  id: "root",
  name: "OPC 生态",
  level: 0,
  active: true,
  opcCount: 8520,
  children: [
    {
      id: "1",
      name: "软件开发",
      level: 1,
      active: true,
      opcCount: 2156,
      children: [
        { id: "1-1", name: "前端开发", level: 2, active: true, opcCount: 428 },
        { id: "1-2", name: "后端开发", level: 2, active: true, opcCount: 312 },
        { id: "1-3", name: "移动端开发", level: 2, active: true, opcCount: 256 },
        { id: "1-4", name: "全栈开发", level: 2, active: true, opcCount: 389 },
        { id: "1-5", name: "小程序开发", level: 2, active: true, opcCount: 198 },
        { id: "1-6", name: "游戏开发", level: 2, active: true, opcCount: 245 },
        { id: "1-7", name: "嵌入式开发", level: 2, active: true, opcCount: 328 },
      ],
    },
    {
      id: "2",
      name: "设计创意",
      level: 1,
      active: true,
      opcCount: 1823,
      children: [
        { id: "2-1", name: "UI 设计", level: 2, active: true, opcCount: 456 },
        { id: "2-2", name: "UX 设计", level: 2, active: true, opcCount: 289 },
        { id: "2-3", name: "平面设计", level: 2, active: true, opcCount: 178 },
        { id: "2-4", name: "品牌设计", level: 2, active: true, opcCount: 234 },
        { id: "2-5", name: "插画设计", level: 2, active: true, opcCount: 312 },
        { id: "2-6", name: "3D 设计", level: 2, active: true, opcCount: 198 },
        { id: "2-7", name: "动效设计", level: 2, active: true, opcCount: 156 },
      ],
    },
    {
      id: "3",
      name: "产品运营",
      level: 1,
      active: true,
      opcCount: 1967,
      children: [
        { id: "3-1", name: "产品经理", level: 2, active: true, opcCount: 398 },
        { id: "3-2", name: "数据分析师", level: 2, active: true, opcCount: 312 },
        { id: "3-3", name: "用户运营", level: 2, active: true, opcCount: 189 },
        { id: "3-4", name: "内容运营", level: 2, active: true, opcCount: 267 },
        { id: "3-5", name: "增长黑客", level: 2, active: true, opcCount: 234 },
        { id: "3-6", name: "项目管理", level: 2, active: true, opcCount: 198 },
        { id: "3-7", name: "商业分析", level: 2, active: true, opcCount: 369 },
      ],
    },
    {
      id: "4",
      name: "营销推广",
      level: 1,
      active: true,
      opcCount: 1345,
      children: [
        { id: "4-1", name: "数字营销", level: 2, active: true, opcCount: 298 },
        { id: "4-2", name: "SEO 优化", level: 2, active: true, opcCount: 267 },
        { id: "4-3", name: "社交媒体", level: 2, active: true, opcCount: 312 },
        { id: "4-4", name: "内容创作", level: 2, active: true, opcCount: 234 },
        { id: "4-5", name: "视频制作", level: 2, active: true, opcCount: 234 },
      ],
    },
    {
      id: "5",
      name: "技术服务",
      level: 1,
      active: true,
      opcCount: 1229,
      children: [
        { id: "5-1", name: "DevOps", level: 2, active: true, opcCount: 389 },
        { id: "5-2", name: "云计算", level: 2, active: true, opcCount: 312 },
        { id: "5-3", name: "网络安全", level: 2, active: true, opcCount: 267 },
        { id: "5-4", name: "数据库管理", level: 2, active: true, opcCount: 198 },
        { id: "5-5", name: "AI 工程", level: 2, active: true, opcCount: 63 },
      ],
    },
  ],
};

export default function Discovery() {
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [zoomLevel, setZoomLevel] = useState(0);

  const handleNodeClick = (node: Node) => {
    if (node.children && node.children.length > 0) {
      setSelectedNode(node);
      setZoomLevel(node.level);
    }
  };

  const handleBack = () => {
    if (zoomLevel > 0) {
      setZoomLevel(zoomLevel - 1);
      setSelectedNode(null);
    }
  };

  const renderNode = (node: Node, index: number, total: number, parentX = 0, parentY = 0) => {
    const angle = (index / total) * 2 * Math.PI - Math.PI / 2;
    const isMobile = typeof window !== 'undefined' && window.innerWidth < 640;
    const radiusBase = node.level === 0 ? 0 : node.level === 1 ? 140 : 220;
    const radius = isMobile ? radiusBase * 0.65 : radiusBase;
    const x = parentX + Math.cos(angle) * radius;                                                    
    const y = parentY + Math.sin(angle) * radius;   

    const sizeClass = node.level === 0 ? "w-16 h-16 sm:w-20 sm:h-20 md:w-24 md:h-24 lg:w-28 lg:h-28 text-[10px] sm:text-[11px] md:text-xs" : node.level === 1 ? "w-14 h-14 sm:w-16 sm:h-16 md:w-20 md:h-20 lg:w-24 lg:h-24 text-[9px] sm:text-[10px] md:text-xs" : "w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 lg:w-20 lg:h-20 text-[8px] sm:text-[9px] md:text-[10px]";

    return (
      <motion.div
        key={node.id}
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        style={{ left: `calc(50% + ${x}px - 5%)`, top: `calc(50% + ${y}px - 10%)` }}
        transition={{ duration: 0.5, delay: index * 0.08 }}
        className={`absolute flex flex-col items-center cursor-pointer transform -translate-x-1/2 -translate-y-1/2 ${
          node.level === 0 ? "z-30" : node.level === 1 ? "z-20" : "z-10"
        }`}
        onClick={() => handleNodeClick(node)}
      >
        <div
          className={`rounded-full flex items-center justify-center shadow-xl transition-all duration-300 ${
            node.active
              ? "bg-gradient-to-br from-blue-500 via-blue-600 to-indigo-700 hover:scale-110 hover:shadow-2xl"
              : "bg-gray-300 cursor-not-allowed"
          } ${sizeClass}`}
        >
          <span className="text-white font-bold text-center px-2 leading-tight">
            {node.name}
          </span>
        </div>
        {node.opcCount > 0 && (
          <div className="mt-2 bg-gradient-to-r from-green-100 to-emerald-100 text-green-700 text-xs px-3 py-1 rounded-full font-bold shadow-sm border border-green-200">
            {node.opcCount.toLocaleString()} 位 OPC
          </div>
        )}
      </motion.div>
    );
  };

  const renderNodes = (nodes: Node[]) => {
    return nodes.map((node, index) => (
      <div key={node.id}>
        {renderNode(node, index, nodes.length)}
        {zoomLevel === node.level && node.children && renderNodes(node.children)}
      </div>
    ));
  };

  return (
    <>
      <PageMeta
        title="发现 - Super OPC Hub"
        description="探索产业拓扑图，发现活跃的 OPC 专业人士"
        keywords={["发现", "产业拓扑", "OPC"]}
      />
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 pb-20">
        <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-40">
          <div className="max-w-4xl mx-auto px-4 h-14 flex items-center justify-center relative">
            <h1 className="text-lg font-bold text-gray-900">发现</h1>
            {zoomLevel > 0 && (
              <button
                onClick={handleBack}
                className="absolute right-4 text-sm text-blue-500 hover:text-blue-600 font-medium"
              >
                返回上一级
              </button>
            )}
          </div>
        </header>

        <main className="max-w-6xl mx-auto px-4 sm:px-6 pb-8">
          <div className="bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 rounded-2xl shadow-xl border border-gray-100 p-4 sm:p-6 h-[500px] sm:h-[600px] lg:h-[650px] relative overflow-hidden">
            <div className="relative w-full h-full">
              {zoomLevel === 0 && renderNodes([initialData])}
              {zoomLevel > 0 && selectedNode && (
                <>
                  {renderNode(
                    { ...selectedNode, level: 0, x: 0, y: 0 },
                    0,
                    1
                  )}
                  {selectedNode.children &&
                    selectedNode.children.map((child, index) =>
                      renderNode(child, index, selectedNode.children!.length, 0, 0)
                    )}
                </>
              )}
            </div>

            {selectedNode && selectedNode.children && (
              <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white text-xs sm:text-sm px-4 sm:px-6 py-1.5 sm:py-2 rounded-full font-bold shadow-lg z-30">
                当前：{selectedNode.name} · {selectedNode.opcCount.toLocaleString()} 位 OPC
              </div>
            )}

            <div className="absolute bottom-3 sm:bottom-4 left-1/2 transform -translate-x-1/2 bg-white/90 backdrop-blur-sm border border-gray-200 rounded-xl p-2.5 sm:p-4 text-xs text-gray-600 shadow-lg z-30 w-[90%] sm:w-auto">
              <div className="flex items-center justify-center gap-2 sm:gap-4 flex-wrap">
                <div className="flex items-center gap-1.5 sm:gap-2">
                  <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 shadow-sm" />
                  <span className="text-xs">活跃产业</span>
                </div>
                <div className="flex items-center gap-1.5 sm:gap-2">
                  <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full bg-gray-300" />
                  <span className="text-xs">暂无 OPC</span>
                </div>
                <div className="h-3 sm:h-4 w-px bg-gray-300 hidden sm:block" />
                <div className="text-gray-500 text-xs sm:text-sm">
                  总 OPC 数：<span className="font-bold text-blue-600">{initialData.opcCount.toLocaleString()}</span> 位
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 bg-blue-50 rounded-xl p-4 border border-blue-100">
            <h3 className="font-bold text-gray-900 mb-2">💡 如何查看产业活跃度</h3>
            <p className="text-sm text-gray-600 leading-relaxed">
              点击拓扑图节点可放大查看细分领域。绿色标签显示该领域的 OPC 专业人士数量，
              数量越多表示该产业越活跃。灰色节点表示暂无 OPC 入驻。
            </p>
          </div>
        </main>
      </div>
    </>
  );
}
