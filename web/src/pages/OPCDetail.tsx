import { useState, useEffect } from "react";
import { PageMeta } from "@/components/common/PageMeta";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { FaStar, FaEnvelope, FaPhone, FaArrowLeft, FaCheckCircle } from "react-icons/fa";
import { motion } from "framer-motion";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { supabase } from "@/lib/supabase";
import { useAuth } from "@/hooks/useAuth";

interface OPCProfile {
  id: string;
  name: string;
  avatar_url: string | null;
  role: string;
  description: string | null;
  skills: string[] | null;
  portfolio_urls: string[] | null;
  contact_email: string | null;
  contact_phone: string | null;
  is_available: boolean;
  match_score: number;
}

export default function OPCDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const [opc, setOpc] = useState<OPCProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      fetchOPCDetail();
    }
  }, [id, location]);

  const fetchOPCDetail = async () => {
    setLoading(true);
    const { data, error } = await supabase
      .from("opc_profiles")
      .select("*")
      .eq("id", id)
      .eq("is_deleted", false)
      .single();

    if (data && !error) {
      setOpc(data);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-500">加载中...</p>
        </div>
      </div>
    );
  }

  if (!opc) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500">OPC 不存在</p>
          <Button onClick={() => navigate("/")} className="mt-4">
            返回首页
          </Button>
        </div>
      </div>
    );
  }

  return (
    <>
      <PageMeta
        title={`${opc.name} - ${opc.role} | Super OPC Hub`}
        description={opc.description || `${opc.name}的个人主页`}
        keywords={[opc.name, opc.role, ...(opc.skills || [])]}
      />
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white pb-20">
        <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-40">
          <div className="max-w-4xl mx-auto px-4 h-14 flex items-center">
            <Button
              variant="ghost"
              onClick={() => navigate(-1)}
              className="gap-2 text-gray-700 hover:bg-gray-100"
            >
              <FaArrowLeft className="w-4 h-4" />
              返回
            </Button>
          </div>
        </header>

        <main className="max-w-4xl mx-auto px-4 py-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card className="overflow-hidden">
              <div className="bg-gradient-to-r from-blue-500 to-indigo-600 h-32" />
              <CardContent className="p-6">
                <div className="flex items-end -mt-12 mb-6">
                  <Avatar className="w-24 h-24 border-4 border-white shadow-lg">
                    <AvatarImage src={opc.avatar_url || undefined} />
                    <AvatarFallback className="text-2xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
                      {opc.name[0].toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="ml-4 flex-1">
                    <div className="flex items-center gap-2">
                      <h1 className="text-2xl font-bold text-gray-900">{opc.name}</h1>
                      {opc.is_available && (
                        <Badge className="bg-green-100 text-green-700 hover:bg-green-100">
                          <FaCheckCircle className="w-3 h-3 mr-1" />
                          可接单
                        </Badge>
                      )}
                    </div>
                    <p className="text-blue-600 font-medium">{opc.role}</p>
                    {opc.match_score > 0 && (
                      <div className="flex items-center gap-1 mt-1">
                        <FaStar className="w-4 h-4 text-orange-500" />
                        <span className="text-sm font-bold text-orange-600">
                          匹配度 {opc.match_score}%
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {opc.description && (
                  <div className="mb-6">
                    <h2 className="text-lg font-bold text-gray-900 mb-2">个人介绍</h2>
                    <p className="text-gray-600 leading-relaxed">{opc.description}</p>
                  </div>
                )}

                {opc.skills && opc.skills.length > 0 && (
                  <div className="mb-6">
                    <h2 className="text-lg font-bold text-gray-900 mb-3">专业技能</h2>
                    <div className="flex flex-wrap gap-2">
                      {opc.skills.map((skill, index) => (
                        <Badge
                          key={index}
                          variant="secondary"
                          className="bg-blue-50 text-blue-700 px-3 py-1.5"
                        >
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {opc.portfolio_urls && opc.portfolio_urls.length > 0 && (
                  <div className="mb-6">
                    <h2 className="text-lg font-bold text-gray-900 mb-3">作品集</h2>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      {opc.portfolio_urls.map((url, index) => (
                        <motion.img
                          key={index}
                          src={url}
                          alt={`作品${index + 1}`}
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ duration: 0.3, delay: index * 0.1 }}
                          className="w-full h-40 object-cover rounded-lg cursor-pointer hover:opacity-90 transition-opacity"
                        />
                      ))}
                    </div>
                  </div>
                )}

                <div className="border-t border-gray-100 pt-6">
                  <h2 className="text-lg font-bold text-gray-900 mb-4">联系方式</h2>
                  {user ? (
                    <div className="space-y-3">
                      {opc.contact_email && (
                        <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <FaEnvelope className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">邮箱</p>
                            <p className="font-medium text-gray-900">{opc.contact_email}</p>
                          </div>
                        </div>
                      )}
                      {opc.contact_phone && (
                        <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                          <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                            <FaPhone className="w-5 h-5 text-green-600" />
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">电话</p>
                            <p className="font-medium text-gray-900">{opc.contact_phone}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-center py-6 bg-gray-50 rounded-xl">
                      <p className="text-gray-600 mb-4">登录后即可查看联系方式</p>
                      <Button onClick={() => navigate("/login")} className="gap-2">
                        立即登录
                      </Button>
                    </div>
                  )}
                </div>

                {user && (
                  <div className="mt-6 flex gap-3">
                    <Button className="flex-1 bg-blue-500 hover:bg-blue-600 text-white gap-2">
                      <FaEnvelope className="w-4 h-4" />
                      联系我
                    </Button>
                    <Button variant="outline" className="flex-1 border-blue-200 text-blue-600 hover:bg-blue-50">
                      <FaStar className="w-4 h-4" />
                      收藏
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </main>
      </div>
    </>
  );
}
