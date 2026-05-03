import { motion } from "framer-motion";
import { FaBriefcase, FaMoneyBillWave, FaClock, FaTools } from "react-icons/fa";

interface DemandProfileProps {
  isVisible: boolean;
}

export function DemandProfile({ isVisible }: DemandProfileProps) {
  if (!isVisible) return null;

  const profileData = {
    projectType: "企业官网设计",
    budget: "¥10,000 - ¥30,000",
    timeline: "2-4 周",
    skills: ["UI 设计", "前端开发", "响应式布局"],
  };

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      transition={{ duration: 0.4 }}
      className="w-full max-w-3xl mx-auto mt-6 sm:mt-8 px-2"
    >
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-4 sm:p-6">
        <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span className="w-1 h-5 sm:h-6 bg-blue-500 rounded-full" />
          需求画像
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
          <div className="flex items-start gap-2 sm:gap-3 p-3 sm:p-4 bg-gray-50 rounded-xl">
            <div className="w-9 h-9 sm:w-10 sm:h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
              <FaBriefcase className="w-4 h-4 sm:w-5 sm:h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-xs sm:text-sm text-gray-500 mb-1">项目类型</p>
              <p className="font-medium text-sm sm:text-base text-gray-900">{profileData.projectType}</p>
            </div>
          </div>

          <div className="flex items-start gap-2 sm:gap-3 p-3 sm:p-4 bg-gray-50 rounded-xl">
            <div className="w-9 h-9 sm:w-10 sm:h-10 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
              <FaMoneyBillWave className="w-4 h-4 sm:w-5 sm:h-5 text-green-600" />
            </div>
            <div>
              <p className="text-xs sm:text-sm text-gray-500 mb-1">预算范围</p>
              <p className="font-medium text-sm sm:text-base text-gray-900">{profileData.budget}</p>
            </div>
          </div>

          <div className="flex items-start gap-2 sm:gap-3 p-3 sm:p-4 bg-gray-50 rounded-xl">
            <div className="w-9 h-9 sm:w-10 sm:h-10 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
              <FaClock className="w-4 h-4 sm:w-5 sm:h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-xs sm:text-sm text-gray-500 mb-1">时间要求</p>
              <p className="font-medium text-sm sm:text-base text-gray-900">{profileData.timeline}</p>
            </div>
          </div>

          <div className="flex items-start gap-2 sm:gap-3 p-3 sm:p-4 bg-gray-50 rounded-xl">
            <div className="w-9 h-9 sm:w-10 sm:h-10 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
              <FaTools className="w-4 h-4 sm:w-5 sm:h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-xs sm:text-sm text-gray-500 mb-1">技能需求</p>
              <div className="flex flex-wrap gap-1 sm:gap-2 mt-1">
                {profileData.skills.map((skill) => (
                  <span
                    key={skill}
                    className="px-2 sm:px-3 py-0.5 sm:py-1 bg-purple-100 text-purple-700 text-xs rounded-full"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
