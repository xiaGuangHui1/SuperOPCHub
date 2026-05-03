import { Button } from "@/components/ui/button";
import { FaStar, FaArrowRight } from "react-icons/fa";
import { motion } from "framer-motion";

interface OPCProfile {
  id: string;
  name: string;
  avatar: string;
  role: string;
  matchRate: number;
  description: string;
  skills: string[];
}

interface OPCMatchCardProps {
  profiles: OPCProfile[];
  isVisible: boolean;
}

export function OPCMatchCard({ profiles, isVisible }: OPCMatchCardProps) {
  if (!isVisible) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="w-full max-w-5xl mx-auto mt-6 sm:mt-8 px-2 sm:px-6"
    >
      <div className="text-center mb-4 sm:mb-6">
        <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-2">
          为您匹配的专业人士
        </h3>
        <p className="text-gray-500 text-xs sm:text-sm">
          基于您的需求画像，智能匹配最适合的 OPC 专家
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
        {profiles.map((profile, index) => (
          <motion.div
            key={profile.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.08 }}
            className="bg-white rounded-2xl shadow-lg border border-gray-100 p-4 sm:p-6 hover:shadow-xl transition-shadow duration-300"
          >
            <div className="flex items-center gap-3 sm:gap-4 mb-3 sm:mb-4">
              <img
                src={profile.avatar}
                alt={profile.name}
                className="w-12 h-12 sm:w-16 sm:h-16 rounded-full object-cover border-2 border-blue-100"
              />
              <div className="flex-1 min-w-0">
                <h4 className="font-bold text-gray-900 text-base sm:text-lg truncate">{profile.name}</h4>
                <p className="text-xs sm:text-sm text-gray-500">{profile.role}</p>
              </div>
            </div>

            <div className="mb-3 sm:mb-4">
              <div className="flex items-center gap-1 sm:gap-2 mb-2">
                <FaStar className="w-3 h-3 sm:w-4 sm:h-4 text-orange-500" />
                <span className="text-xs sm:text-sm font-medium text-gray-700">匹配度</span>
                <span className="ml-auto px-2 sm:px-3 py-0.5 sm:py-1 bg-orange-100 text-orange-700 text-xs sm:text-sm font-bold rounded-full">
                  {profile.matchRate}%
                </span>
              </div>
              <p className="text-xs sm:text-sm text-gray-600 line-clamp-2">{profile.description}</p>
            </div>

            <div className="flex flex-wrap gap-1 sm:gap-2 mb-3 sm:mb-4">
              {profile.skills.map((skill) => (
                <span
                  key={skill}
                  className="px-1.5 sm:px-2 py-0.5 sm:py-1 bg-blue-50 text-blue-600 text-xs rounded-md"
                >
                  {skill}
                </span>
              ))}
            </div>

            <Button className="w-full bg-blue-500 hover:bg-blue-600 text-white gap-2 text-sm py-2 sm:py-3">
              查看详情
              <FaArrowRight className="w-2.5 h-2.5 sm:w-3 sm:h-3" />
            </Button>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
