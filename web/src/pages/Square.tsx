import { useState } from "react";
import { PageMeta } from "@/components/common/PageMeta";
import { Button } from "@/components/ui/button";
import { FaHeart, FaRegHeart, FaComment, FaShare } from "react-icons/fa";
import { motion } from "framer-motion";

interface Post {
  id: string;
  user: {
    name: string;
    avatar: string;
    isFollowed: boolean;
  };
  content: string;
  images?: string[];
  video?: string;
  likes: number;
  comments: number;
  shares: number;
  isLiked: boolean;
  timestamp: string;
}

export default function Square() {
  const [posts, setPosts] = useState<Post[]>([
    {
      id: "1",
      user: {
        name: "设计师小王",
        avatar: "https://ui-avatars.com/api/?name=%E8%AE%BE%E8%AE%A1%E5%B8%88%E5%B0%8F%E7%8E%8B&background=3B82F6&color=fff&size=200&bold=true",
        isFollowed: false,
      },
      content: "刚完成了一个企业官网设计项目，客户非常满意！分享一下设计过程中的关键思考：1. 色彩搭配要符合品牌调性 2. 布局要突出核心价值 3. 交互要简洁流畅 #UI 设计 #官网设计",
      images: [
        "https://picsum.photos/seed/webdesign1/800/600",
        "https://picsum.photos/seed/webdesign2/800/600",
        "https://picsum.photos/seed/webdesign3/800/600",
      ],
      likes: 128,
      comments: 23,
      shares: 15,
      isLiked: false,
      timestamp: "2 小时前",
    },
    {
      id: "2",
      user: {
        name: "开发者老李",
        avatar: "https://ui-avatars.com/api/?name=%E5%BC%80%E5%8F%91%E8%80%85%E8%80%81%E6%9D%8E&background=10B981&color=fff&size=200&bold=true",
        isFollowed: true,
      },
      content: "分享一个 React 性能优化技巧：使用 useMemo 和 useCallback 避免不必要的重新渲染。代码已开源，欢迎 star！🚀",
      video: "https://picsum.photos/seed/coding/800/600",
      likes: 256,
      comments: 45,
      shares: 38,
      isLiked: true,
      timestamp: "5 小时前",
    },
    {
      id: "3",
      user: {
        name: "产品经理小张",
        avatar: "https://ui-avatars.com/api/?name=%E4%BA%A7%E5%93%81%E7%BB%8F%E7%90%86%E5%B0%8F%E5%BC%A0&background=F59E0B&color=fff&size=200&bold=true",
        isFollowed: false,
      },
      content: "今天参加了一个产品峰会，收获满满。几个关键洞察：AI 驱动的产品体验将成为标配、用户对隐私保护越来越重视、跨平台体验一致性很重要。",
      likes: 89,
      comments: 12,
      shares: 8,
      isLiked: false,
      timestamp: "1 天前",
    },
    {
      id: "4",
      user: {
        name: "创意设计师小陈",
        avatar: "https://ui-avatars.com/api/?name=%E5%88%9B%E6%84%8F%E8%AE%BE%E8%AE%A1%E5%B8%88%E5%B0%8F%E9%99%88&background=8B5CF6&color=fff&size=200&bold=true",
        isFollowed: false,
      },
      content: "最新的品牌 VI 设计作品，采用了大胆的渐变色彩和几何图形，传达现代科技感。大家觉得怎么样？",
      images: [
        "https://picsum.photos/seed/brand1/800/600",
        "https://picsum.photos/seed/brand2/800/600",
      ],
      likes: 312,
      comments: 56,
      shares: 42,
      isLiked: false,
      timestamp: "2 天前",
    },
  ]);

  const toggleLike = (postId: string) => {
    setPosts(posts.map(post => {
      if (post.id === postId) {
        return {
          ...post,
          isLiked: !post.isLiked,
          likes: post.isLiked ? post.likes - 1 : post.likes + 1,
        };
      }
      return post;
    }));
  };

  const toggleFollow = (postId: string) => {
    setPosts(posts.map(post => {
      if (post.id === postId) {
        return {
          ...post,
          user: {
            ...post.user,
            isFollowed: !post.user.isFollowed,
          },
        };
      }
      return post;
    }));
  };

  return (
    <>
      <PageMeta
        title="广场 - Super OPC Hub"
        description="浏览 OPC 专业人士的作品和分享"
        keywords={["广场", "作品展示", "OPC"]}
      />
      <div className="min-h-screen bg-gray-50 pb-20">
        <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
          <div className="max-w-2xl mx-auto px-4 h-14 flex items-center justify-center">
            <h1 className="text-lg font-bold text-gray-900">广场</h1>
          </div>
        </header>

        <main className="max-w-2xl mx-auto">
          {posts.map((post, index) => (
            <motion.article
              key={post.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className="bg-white border-b border-gray-100 py-4"
            >
              <div className="px-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <img
                      src={post.user.avatar}
                      alt={post.user.name}
                      className="w-10 h-10 rounded-full object-cover"
                    />
                    <div>
                      <p className="font-medium text-gray-900 text-sm">{post.user.name}</p>
                      <p className="text-xs text-gray-500">{post.timestamp}</p>
                    </div>
                  </div>
                  <Button
                    variant={post.user.isFollowed ? "outline" : "default"}
                    size="sm"
                    onClick={() => toggleFollow(post.id)}
                    className={`h-8 text-xs ${
                      post.user.isFollowed
                        ? "border-gray-300 text-gray-700 hover:bg-gray-50"
                        : "bg-blue-500 hover:bg-blue-600 text-white"
                    }`}
                  >
                    {post.user.isFollowed ? "已关注" : "关注"}
                  </Button>
                </div>

                <p className="text-sm text-gray-800 mb-3 leading-relaxed">{post.content}</p>

                {post.images && post.images.length > 0 && (
                  <div className={`grid gap-2 mb-3 ${
                    post.images.length === 1 ? "grid-cols-1" :
                    post.images.length === 2 ? "grid-cols-2" :
                    "grid-cols-3"
                  }`}>
                    {post.images.map((img, idx) => (
                      <img
                        key={idx}
                        src={img}
                        alt={`展示${idx + 1}`}
                        className="w-full h-48 object-cover rounded-lg cursor-pointer hover:opacity-90 transition-opacity"
                      />
                    ))}
                  </div>
                )}

                {post.video && (
                  <div className="mb-3">
                    <div className="relative w-full h-64 bg-black rounded-lg overflow-hidden">
                      <img
                        src={post.video}
                        alt="视频封面"
                        className="w-full h-full object-cover"
                      />
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-16 h-16 bg-white/80 rounded-full flex items-center justify-center cursor-pointer hover:bg-white transition-colors">
                          <svg className="w-8 h-8 text-gray-900 ml-1" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M8 5v14l11-7z" />
                          </svg>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                  <button
                    onClick={() => toggleLike(post.id)}
                    className={`flex items-center gap-2 text-sm transition-colors ${
                      post.isLiked ? "text-red-500" : "text-gray-500 hover:text-red-500"
                    }`}
                  >
                    {post.isLiked ? <FaHeart className="w-4 h-4" /> : <FaRegHeart className="w-4 h-4" />}
                    <span>{post.likes}</span>
                  </button>

                  <button className="flex items-center gap-2 text-sm text-gray-500 hover:text-blue-500 transition-colors">
                    <FaComment className="w-4 h-4" />
                    <span>{post.comments}</span>
                  </button>

                  <button className="flex items-center gap-2 text-sm text-gray-500 hover:text-green-500 transition-colors">
                    <FaShare className="w-4 h-4" />
                    <span>{post.shares}</span>
                  </button>
                </div>
              </div>
            </motion.article>
          ))}
        </main>
      </div>
    </>
  );
}
