import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { FaPaperPlane } from "react-icons/fa";
import { motion } from "framer-motion";
import { sendChatMessage, type DemandData, type MatchResult } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  onDemandSubmit?: (messages: Message[]) => void;
  onDemandUpdate?: (demand: DemandData) => void;
  onMatchResults?: (matches: MatchResult[]) => void;
}

export function ChatInterface({
  onDemandSubmit,
  onDemandUpdate,
  onMatchResults,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [matchingComplete, setMatchingComplete] = useState(false);
  const sessionIdRef = useRef<string>("");

  /** 生成 session ID */
  const getSessionId = () => {
    if (!sessionIdRef.current) {
      sessionIdRef.current = `session_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    }
    return sessionIdRef.current;
  };

  const handleSend = async () => {
    if (!inputValue.trim() || matchingComplete) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
      timestamp: new Date(),
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputValue("");
    setIsTyping(true);

    try {
      const sessionId = getSessionId();

      // 转换为 API 所需格式
      const apiMessages = newMessages.map((m) => ({
        role: m.role as "user" | "assistant",
        content: m.content,
      }));

      const response = await sendChatMessage(sessionId, apiMessages);

      // 添加 AI 回复
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.assistant_message,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsTyping(false);

      // 更新需求画像
      if (response.demand_profile) {
        onDemandUpdate?.(response.demand_profile);
        // 兼容旧的回调
        onDemandSubmit?.([userMessage, assistantMessage]);
      }

      // 匹配完成，展示结果
      if (response.is_matching_complete && response.matches.length > 0) {
        setMatchingComplete(true);
        onMatchResults?.(response.matches);
      }
    } catch (error) {
      setIsTyping(false);
      // 出错时回退到模拟回复
      const fallbackMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: error instanceof Error
          ? `抱歉，服务暂时不可用：${error.message}。请稍后再试。`
          : "抱歉，服务暂时不可用，请稍后再试。",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, fallbackMessage]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestionClick = (text: string) => {
    setInputValue(text);
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
        <div className="h-[400px] sm:h-[500px] overflow-y-auto p-4 sm:p-6 space-y-3 sm:space-y-4">
          {messages.length === 0 ?
            <div className="h-full flex items-center justify-center text-gray-400">
              <div className="text-center space-y-3">
                <p className="text-[16px] sm:text-[18px]">嗨，告诉我您遇到的困难或项目想法，让我们一起探索...</p>
                <div className="flex flex-wrap gap-2 justify-center max-w-2xl">
                  <div
                    className="px-4 py-2.5 border-2 border-blue-200 rounded-xl text-blue-600 font-medium cursor-pointer hover:bg-blue-50 hover:border-blue-300 hover:shadow-md transition-all duration-200 text-center min-w-[140px] text-sm"
                    onClick={() => handleSuggestionClick("帮我搭建一个AI智能客服系统")}
                  >
                    帮我搭建AI智能客服
                  </div>
                  <div
                    className="px-4 py-2.5 border-2 border-blue-200 rounded-xl text-blue-600 font-medium cursor-pointer hover:bg-blue-50 hover:border-blue-300 hover:shadow-md transition-all duration-200 text-center min-w-[140px] text-sm"
                    onClick={() => handleSuggestionClick("帮我做一个跨境电商独立站")}
                  >
                    帮我做跨境电商独立站
                  </div>
                  <div
                    className="px-4 py-2.5 border-2 border-blue-200 rounded-xl text-blue-600 font-medium cursor-pointer hover:bg-blue-50 hover:border-blue-300 hover:shadow-md transition-all duration-200 text-center min-w-[140px] text-sm"
                    onClick={() => handleSuggestionClick("帮我开发一个自动化运营数据看板")}
                  >
                    自动化运营数据看板
                  </div>
                  <div
                    className="px-4 py-2.5 border-2 border-blue-200 rounded-xl text-blue-600 font-medium cursor-pointer hover:bg-blue-50 hover:border-blue-300 hover:shadow-md transition-all duration-200 text-center min-w-[140px] text-sm"
                    onClick={() => handleSuggestionClick("帮我做一个个人品牌全案设计")}
                  >
                    个人品牌全案设计
                  </div>
                  <div
                    className="px-4 py-2.5 border-2 border-blue-200 rounded-xl text-blue-600 font-medium cursor-pointer hover:bg-blue-50 hover:border-blue-300 hover:shadow-md transition-all duration-200 text-center min-w-[140px] text-sm"
                    onClick={() => handleSuggestionClick("帮我做一个自动化财务对账系统")}
                  >
                    自动化财务对账系统
                  </div>
                  <div
                    className="px-4 py-2.5 border-2 border-blue-200 rounded-xl text-blue-600 font-medium cursor-pointer hover:bg-blue-50 hover:border-blue-300 hover:shadow-md transition-all duration-200 text-center min-w-[140px] text-sm"
                    onClick={() => handleSuggestionClick("帮我开发一个小程序商城")}
                  >
                    帮我开发小程序商城
                  </div>
                  <div
                    className="px-4 py-2.5 border-2 border-blue-200 rounded-xl text-blue-600 font-medium cursor-pointer hover:bg-blue-50 hover:border-blue-300 hover:shadow-md transition-all duration-200 text-center min-w-[140px] text-sm"
                    onClick={() => handleSuggestionClick("帮我搭建短视频内容矩阵")}
                  >
                    短视频内容矩阵搭建
                  </div>
                </div>
              </div>
            </div>
          :
            <>
              {messages.map((message) =>
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[85%] sm:max-w-[80%] px-3 sm:px-4 py-2 sm:py-3 rounded-2xl ${
                      message.role === "user"
                        ? "bg-blue-500 text-white rounded-br-md"
                        : "bg-gray-100 text-gray-900 rounded-bl-md"
                    }`}
                  >
                    <p className="text-xs sm:text-sm leading-relaxed">{message.content}</p>
                  </div>
                </motion.div>
              )}
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                  <div className="bg-gray-100 px-4 py-3 rounded-2xl rounded-bl-md">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                    </div>
                  </div>
                </motion.div>
              )}
            </>
          }
        </div>

        <div className="border-t border-gray-100 p-3 sm:p-4 bg-gray-50">
          {!matchingComplete ? (
            <div className="flex gap-2 sm:gap-3">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="告诉我您遇到的困难或项目想法..."
                className="flex-1 px-3 sm:px-4 py-2 sm:py-3 text-sm sm:text-base border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <Button
                onClick={handleSend}
                disabled={!inputValue.trim()}
                className="bg-blue-500 hover:bg-blue-600 text-white px-4 sm:px-6 py-2 sm:py-3 rounded-xl transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex-shrink-0"
              >
                <FaPaperPlane className="w-3 h-3 sm:w-4 sm:h-4" />
              </Button>
            </div>
          ) : (
            <p className="text-center text-sm text-gray-500">
              匹配完成！请查看下方结果
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
