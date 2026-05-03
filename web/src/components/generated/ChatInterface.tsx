import { useState } from "react";
import { Button } from "@/components/ui/button";
import { FaPaperPlane } from "react-icons/fa";
import { motion } from "framer-motion";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  onDemandSubmit?: (messages: Message[]) => void;
}

export function ChatInterface({ onDemandSubmit }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: inputValue,
      timestamp: new Date()
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "感谢您的分享！我已经了解了您的项目需求。让我为您整理一份详细的需求画像，并匹配最适合的 OPC 专业人士。",
        timestamp: new Date()
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsTyping(false);
      onDemandSubmit?.([...messages, userMessage, assistantMessage]);
    }, 1500);
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
                <p className="text-[16px] sm:text-[18px]">告诉我您的项目想法，让我们一起探索...</p>
                <div className="flex flex-col sm:flex-row gap-2 justify-center">
                  <div
                    className="px-4 py-2.5 border-2 border-blue-200 rounded-xl text-blue-600 font-medium cursor-pointer hover:bg-blue-50 hover:border-blue-300 hover:shadow-md transition-all duration-200 text-center min-w-[140px] text-sm"
                    onClick={() => handleSuggestionClick("帮我找一个UI设计师")}
                  >
                    帮我找一个UI设计师
                  </div>
                  <div
                    className="px-4 py-2.5 border-2 border-blue-200 rounded-xl text-blue-600 text-sm font-medium cursor-pointer hover:bg-blue-50 hover:border-blue-300 hover:shadow-md transition-all duration-200 text-center min-w-[140px]"
                    onClick={() => handleSuggestionClick("我想做一个哄我上班的APP")}
                  >
                    我想做一个哄我上班的APP
                  </div>
                  <div
                    className="px-4 py-2.5 border-2 border-blue-200 rounded-xl text-blue-600 text-sm font-medium cursor-pointer hover:bg-blue-50 hover:border-blue-300 hover:shadow-md transition-all duration-200 text-center min-w-[140px]"
                    onClick={() => handleSuggestionClick("想给我家做一个全屋家电智能系统")}
                  >
                    我想做一个智能电控系统
                  </div>
                </div>
              </div>
            </div> :

          <>
              {messages.map((message) =>
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>

                  <div
                className={`max-w-[85%] sm:max-w-[80%] px-3 sm:px-4 py-2 sm:py-3 rounded-2xl ${
                message.role === "user" ?
                "bg-blue-500 text-white rounded-br-md" :
                "bg-gray-100 text-gray-900 rounded-bl-md"}`
                }>

                    <p className="text-xs sm:text-sm leading-relaxed">{message.content}</p>
                  </div>
                </motion.div>
            )}
              {isTyping &&
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start">

                  <div className="bg-gray-100 px-4 py-3 rounded-2xl rounded-bl-md">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                    </div>
                  </div>
                </motion.div>
            }
            </>
          }
        </div>

        <div className="border-t border-gray-100 p-3 sm:p-4 bg-gray-50">
          <div className="flex gap-2 sm:gap-3">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="告诉我您的项目想法..."
              className="flex-1 px-3 sm:px-4 py-2 sm:py-3 text-sm sm:text-base border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" />

            <Button
              onClick={handleSend}
              disabled={!inputValue.trim()}
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 sm:px-6 py-2 sm:py-3 rounded-xl transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex-shrink-0">

              <FaPaperPlane className="w-3 h-3 sm:w-4 sm:h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>);

}
