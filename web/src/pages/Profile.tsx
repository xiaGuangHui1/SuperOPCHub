import { useState, useEffect } from "react";
import { PageMeta } from "@/components/common/PageMeta";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FaUser, FaHistory, FaEdit, FaSignOutAlt, FaStar } from "react-icons/fa";
import { motion } from "framer-motion";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/lib/supabase";
import { useNavigate, useLocation } from "react-router-dom";

interface ConversationHistory {
  id: string;
  session_id: string;
  created_at: string;
  message_count: number;
}

export default function Profile() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [activeTab, setActiveTab] = useState("profile");
  const [conversations, setConversations] = useState<ConversationHistory[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    full_name: "",
    phone: "",
    bio: "",
    skills: "",
    is_available: true,
  });

  useEffect(() => {
    if (!loading && !user) {
      navigate("/login", { state: { from: location.pathname } });
    }
  }, [user, loading, navigate, location]);

  useEffect(() => {
    if (user) {
      fetchConversations();
      fetchUserProfile();
    }
  }, [user]);

  const fetchConversations = async () => {
    if (!user) return;
    const { data, error } = await supabase
      .from("conversation_history")
      .select("session_id, created_at")
      .eq("user_id", user.id)
      .eq("is_deleted", false)
      .order("created_at", { ascending: false })
      .limit(10);

    if (data && !error) {
      const grouped = data.reduce((acc, curr) => {
        if (!acc[curr.session_id]) {
          acc[curr.session_id] = {
            id: curr.session_id,
            session_id: curr.session_id,
            created_at: curr.created_at,
            message_count: 0,
          };
        }
        acc[curr.session_id].message_count += 1;
        return acc;
      }, {} as Record<string, ConversationHistory>);
      setConversations(Object.values(grouped));
    }
  };

  const fetchUserProfile = async () => {
    if (!user) return;
    const { data, error } = await supabase
      .from("profiles")
      .select("full_name, phone, avatar_url")
      .eq("id", user.id)
      .single();

    if (data && !error) {
      setFormData((prev) => ({
        ...prev,
        full_name: data.full_name || "",
        phone: data.phone || "",
      }));
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate("/");
  };

  const handleSaveProfile = async () => {
    if (!user) return;
    const { error } = await supabase
      .from("profiles")
      .update({
        full_name: formData.full_name,
        phone: formData.phone,
      })
      .eq("id", user.id);

    if (!error) {
      setIsEditing(false);
    }
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

  if (!user) {
    return null;
  }

  return (
    <>
      <PageMeta
        title="个人中心 - Super OPC Hub"
        description="管理您的个人资料、查看历史对话"
        keywords={["个人中心", "个人资料", "OPC"]}
      />
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white pb-20">
        <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-40">
          <div className="max-w-4xl mx-auto px-4 h-14 flex items-center justify-center">
            <h1 className="text-base sm:text-lg font-bold text-gray-900">个人中心</h1>
          </div>
        </header>

        <main className="max-w-4xl mx-auto px-4 py-4 sm:py-6">
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-500 to-indigo-600 h-24 sm:h-32" />
            <div className="px-4 sm:px-6 pb-4 sm:pb-6">
              <div className="flex items-end -mt-10 sm:-mt-12 mb-4 sm:mb-6">
                <Avatar className="w-20 h-20 sm:w-24 sm:h-24 border-4 border-white shadow-lg">
                  <AvatarImage src={user.avatar_url || undefined} />
                  <AvatarFallback className="text-xl sm:text-2xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
                    {user.nickname?.[0]?.toUpperCase() || user.email[0].toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div className="ml-3 sm:ml-4 flex-1 min-w-0">
                  <h2 className="text-lg sm:text-2xl font-bold text-gray-900 truncate">{user.nickname || "未设置昵称"}</h2>
                  <p className="text-gray-500 text-xs sm:text-sm truncate">{user.email}</p>
                </div>
                <Button
                  variant="outline"
                  onClick={handleLogout}
                  className="gap-1 sm:gap-2 border-gray-300 text-gray-700 hover:bg-gray-50 text-xs sm:text-sm px-2 sm:px-3"
                >
                  <FaSignOutAlt className="w-3 h-3 sm:w-4 sm:h-4" />
                  <span className="hidden sm:inline">退出</span>
                </Button>
              </div>

              <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid w-full grid-cols-2 mb-4 sm:mb-6">
                  <TabsTrigger value="profile" className="gap-1 sm:gap-2 text-xs sm:text-sm">
                    <FaUser className="w-3 h-3 sm:w-4 sm:h-4" />
                    个人资料
                  </TabsTrigger>
                  <TabsTrigger value="history" className="gap-1 sm:gap-2 text-xs sm:text-sm">
                    <FaHistory className="w-3 h-3 sm:w-4 sm:h-4" />
                    历史对话
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="profile" className="space-y-3 sm:space-y-6">
                  <Card>
                    <CardHeader className="pb-3 sm:pb-4">
                      <div className="flex items-center justify-between">
                        <div className="min-w-0">
                          <CardTitle className="text-base sm:text-lg">基本信息</CardTitle>
                          <CardDescription className="text-xs sm:text-sm">管理您的个人信息和联系方式</CardDescription>
                        </div>
                        <Button
                          variant={isEditing ? "default" : "outline"}
                          size="sm"
                          onClick={isEditing ? handleSaveProfile : () => setIsEditing(true)}
                          className="gap-1 sm:gap-2 text-xs sm:text-sm px-2 sm:px-3"
                        >
                          <FaEdit className="w-3 h-3" />
                          <span className="hidden sm:inline">{isEditing ? "保存" : "编辑"}</span>
                          <span className="sm:hidden">{isEditing ? "保存" : "编辑"}</span>
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3 sm:space-y-4">
                      <div className="grid gap-2">
                        <Label htmlFor="email" className="text-xs sm:text-sm">邮箱地址</Label>
                        <Input id="email" value={user.email} disabled className="bg-gray-50 h-9 sm:h-10 text-xs sm:text-sm" />
                      </div>
                      <div className="grid gap-2">
                        <Label htmlFor="full_name" className="text-xs sm:text-sm">昵称</Label>
                        <Input
                          id="full_name"
                          value={formData.full_name}
                          onChange={(e) =>
                            setFormData((prev) => ({ ...prev, full_name: e.target.value }))
                          }
                          disabled={!isEditing}
                          placeholder="请输入昵称"
                          className="h-9 sm:h-10 text-xs sm:text-sm"
                        />
                      </div>
                      <div className="grid gap-2">
                        <Label htmlFor="phone" className="text-xs sm:text-sm">手机号码</Label>
                        <Input
                          id="phone"
                          value={formData.phone}
                          onChange={(e) =>
                            setFormData((prev) => ({ ...prev, phone: e.target.value }))
                          }
                          disabled={!isEditing}
                          placeholder="请输入手机号码"
                          className="h-9 sm:h-10 text-xs sm:text-sm"
                        />
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-3 sm:pb-4">
                      <CardTitle className="text-base sm:text-lg">OPC 身份设置</CardTitle>
                      <CardDescription className="text-xs sm:text-sm">设置您的专业身份，让更多客户找到您</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3 sm:space-y-4">
                      <div className="grid gap-2">
                        <Label htmlFor="bio" className="text-xs sm:text-sm">个人介绍</Label>
                        <Textarea
                          id="bio"
                          value={formData.bio}
                          onChange={(e) =>
                            setFormData((prev) => ({ ...prev, bio: e.target.value }))
                          }
                          disabled={!isEditing}
                          placeholder="介绍一下您的专业背景和经验..."
                          rows={4}
                          className="text-xs sm:text-sm"
                        />
                      </div>
                      <div className="grid gap-2">
                        <Label htmlFor="skills" className="text-xs sm:text-sm">技能标签</Label>
                        <Input
                          id="skills"
                          value={formData.skills}
                          onChange={(e) =>
                            setFormData((prev) => ({ ...prev, skills: e.target.value }))
                          }
                          disabled={!isEditing}
                          placeholder="例如：UI 设计，React, Figma（用逗号分隔）"
                          className="h-9 sm:h-10 text-xs sm:text-sm"
                        />
                      </div>
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          id="is_available"
                          checked={formData.is_available}
                          onChange={(e) =>
                            setFormData((prev) => ({ ...prev, is_available: e.target.checked }))
                          }
                          disabled={!isEditing}
                          className="w-4 h-4 text-blue-500 rounded"
                        />
                        <Label htmlFor="is_available" className="text-xs sm:text-sm cursor-pointer">
                          可接受新项目
                        </Label>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="history">
                  <Card>
                    <CardHeader className="pb-3 sm:pb-4">
                      <CardTitle className="text-base sm:text-lg">历史对话</CardTitle>
                      <CardDescription className="text-xs sm:text-sm">查看您与 AI 智能体的历史对话记录</CardDescription>
                    </CardHeader>
                    <CardContent>
                      {conversations.length === 0 ? (
                        <div className="text-center py-8 sm:py-12">
                          <FaHistory className="w-10 h-10 sm:w-12 sm:h-12 text-gray-300 mx-auto mb-3 sm:mb-4" />
                          <p className="text-gray-500 text-sm sm:text-base">暂无历史对话</p>
                          <p className="text-gray-400 text-xs sm:text-sm mt-2 px-4">
                            返回首页开始与 AI 探索您的项目需求
                          </p>
                        </div>
                      ) : (
                        <div className="space-y-2 sm:space-y-3">
                          {conversations.map((conversation, index) => (
                            <motion.div
                              key={conversation.id}
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ duration: 0.3, delay: index * 0.05 }}
                              className="p-3 sm:p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer"
                            >
                              <div className="flex items-center justify-between">
                                <div className="min-w-0 flex-1">
                                  <p className="font-medium text-gray-900 text-xs sm:text-sm truncate">
                                    对话 {conversation.session_id.slice(0, 8)}...
                                  </p>
                                  <p className="text-xs text-gray-500 mt-1">
                                    {conversation.message_count} 条消息 ·{" "}
                                    {new Date(conversation.created_at).toLocaleDateString("zh-CN")}
                                  </p>
                                </div>
                                <div className="flex items-center gap-1 sm:gap-2 ml-2">
                                  <FaStar className="w-3 h-3 sm:w-4 sm:h-4 text-blue-500 flex-shrink-0" />
                                  <span className="text-xs sm:text-sm text-gray-600 hidden sm:inline">查看详情</span>
                                </div>
                              </div>
                            </motion.div>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            </div>
          </div>
        </main>
      </div>
    </>
  );
}
