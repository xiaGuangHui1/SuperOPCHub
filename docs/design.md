# Super OPC Hub 设计文档

## 1. 项目概述

Super OPC Hub 是一个 AI 驱动的需求匹配平台，帮助甲方通过自然语言对话探索创意、明确需求，并智能匹配最适合的专业人士（OPC - One Professional Consultant）。

### 核心功能

- **AI 对话探索**：用户通过对话描述项目需求，平台引导需求细化
- **需求画像生成**：从对话中提取结构化需求（项目类型、预算、时间、技能）
- **智能 OPC 匹配**：根据需求画像匹配专业人士，展示匹配度和详细资料
- **产业拓扑图**：可视化展示各产业领域的 OPC 活跃度
- **作品广场**：OPC 分享作品和经验的社交动态流
- **邮箱验证码登录**：无密码的 OTP 认证方式

---

## 2. 技术栈

| 分类 | 技术 | 版本 |
|------|------|------|
| 框架 | React | 18.3.1 |
| 语言 | TypeScript | 5.6.2 |
| 构建 | Vite | 5.4.21 |
| 路由 | React Router DOM | 6.30.2 |
| 样式 | Tailwind CSS | 3.4.18 |
| 组件库 | shadcn/ui (Radix UI) | — |
| 动画 | Framer Motion | 11.18.2 |
| 图标 | React Icons (Font Awesome) | 5.5.0 |
| SEO | React Helmet Async | 2.0.5 |
| 后端 | Supabase | JS SDK 2.44.4 |
| 包管理 | pnpm | 10.8.1 |
| Lint | Biome | 2.3.8 |
| Toast | Sonner | 2.0.7 |

---

## 3. 项目结构

```
web/
├── index.html                        # 入口 HTML
├── package.json                      # 依赖与脚本
├── vite.config.ts                    # Vite 配置
├── tailwind.config.js                # Tailwind 配置
├── tsconfig.json                     # TypeScript 配置
├── postcss.config.js                 # PostCSS 配置
├── design.md                         # 本文档
├── supabase/
│   └── migrations/
│       └── create_opc_tables.sql     # 数据库迁移脚本
└── src/
    ├── main.tsx                      # 应用入口
    ├── route.tsx                     # 路由定义
    ├── layout.tsx                    # 全局布局（含底部导航）
    ├── index.css                     # 全局样式与 CSS 变量
    ├── vite-env.d.ts                 # Vite 类型声明
    ├── assets/                       # 静态资源
    │   └── gitkeep
    ├── components/
    │   ├── common/
    │   │   └── PageMeta.tsx          # SEO 元信息组件
    │   ├── generated/
    │   │   ├── Header.tsx            # 顶部导航栏
    │   │   ├── ChatInterface.tsx     # AI 对话界面
    │   │   ├── DemandProfile.tsx     # 需求画像展示
    │   │   ├── OPCMatchCard.tsx      # OPC 匹配卡片列表
    │   │   └── BottomNav.tsx         # 底部导航（未使用）
    │   └── ui/                       # 50 个 shadcn/ui 组件
    │       ├── button.tsx
    │       ├── input.tsx
    │       ├── card.tsx
    │       ├── avatar.tsx
    │       ├── tabs.tsx
    │       └── ... (详见组件清单)
    ├── hooks/
    │   ├── useAuth.ts               # 认证状态 Hook
    │   ├── useLogin.ts              # OTP 登录 Hook
    │   └── use-mobile.ts            # 移动端检测 Hook
    ├── lib/
    │   ├── supabase.ts              # Supabase 客户端
    │   └── utils.ts                 # cn() 工具函数
    ├── pages/
    │   ├── Home.tsx                  # 首页（对话 → 画像 → 匹配）
    │   ├── Login.tsx                 # 登录页（邮箱 OTP）
    │   ├── Square.tsx                # 广场页（动态流）
    │   ├── Discovery.tsx             # 发现页（产业拓扑图）
    │   ├── Profile.tsx               # 我的页（资料 + 历史）
    │   └── OPCDetail.tsx             # OPC 详情页
    └── types/
        └── global.d.ts              # 全局类型声明
```

---

## 4. 路由设计

所有页面嵌套在 `Layout` 组件下，`Layout` 提供底部导航栏（仅 4 个主页面显示）。

| 路径 | 页面 | 底部导航 | 说明 |
|------|------|----------|------|
| `/` | Home | 是 | 首页，AI 对话入口 |
| `/login` | Login | 否 | 邮箱 OTP 登录 |
| `/square` | Square | 是 | 作品广场动态流 |
| `/discovery` | Discovery | 是 | 产业拓扑图浏览 |
| `/profile` | Profile | 是 | 个人中心（需登录） |
| `/opc/:id` | OPCDetail | 否 | OPC 详情页 |
| `*` | Home | — | 兜底路由 |

### 路由文件 (`src/route.tsx`)

```tsx
const routes: RouteObject[] = [{
  element: <Layout />,
  children: [
    { path: "/",            element: <Home /> },
    { path: "/login",       element: <Login /> },
    { path: "/square",      element: <Square /> },
    { path: "/discovery",   element: <Discovery /> },
    { path: "/profile",     element: <Profile /> },
    { path: "/opc/:id",     element: <OPCDetail /> },
    { path: "*",            element: <Home /> },
  ],
}];
```

---

## 5. 组件树

```
<StrictMode>
  <HelmetProvider>
    <RouterProvider>
      <Layout>                                 # 全局布局 + 底部导航
        ├── <Home>                             # 首页
        │   ├── <PageMeta>                     # SEO
        │   ├── <Header>                       # 顶部栏（登录按钮）
        │   ├── <ChatInterface>                # AI 对话区
        │   │   ├── 建议标签（3 个快捷输入）
        │   │   ├── 消息列表
        │   │   ├── 打字指示器
        │   │   └── 输入框 + 发送按钮
        │   ├── <DemandProfile>                # 需求画像（步骤 2）
        │   │   └── 4 个信息卡片（类型/预算/时间/技能）
        │   └── <OPCMatchCard>                 # 匹配结果（步骤 3）
        │       └── 8 个 OPC 卡片（头像/匹配度/技能/详情按钮）
        │
        ├── <Login>                            # 登录页
        │   ├── <PageMeta>
        │   ├── 关闭按钮（返回首页）
        │   ├── 邮箱输入表单
        │   └── 验证码输入表单
        │
        ├── <Square>                           # 广场页
        │   ├── <PageMeta>
        │   └── 动态列表（4 篇帖子）
        │       ├── 用户信息（头像/姓名/时间/关注按钮）
        │       ├── 正文
        │       ├── 图片/视频网格
        │       └── 互动栏（点赞/评论/分享）
        │
        ├── <Discovery>                        # 发现页
        │   ├── <PageMeta>
        │   ├── 顶部标题栏（含返回按钮）
        │   ├── 拓扑图容器
        │   │   ├── 根节点（OPC 生态）
        │   │   ├── 一级节点（5 个产业分类）
        │   │   └── 二级节点（点击后展开的子分类）
        │   ├── 当前层级指示条
        │   └── 底部图例
        │
        ├── <Profile>                          # 我的页
        │   ├── <PageMeta>
        │   ├── Tab: 个人资料
        │   │   ├── <Avatar>
        │   │   ├── 编辑表单（姓名/电话/简介/技能/可接单状态）
        │   │   └── 退出登录按钮
        │   └── Tab: 历史对话
        │       └── 会话列表（从 Supabase 加载）
        │
        └── <OPCDetail>                        # OPC 详情页
            ├── <PageMeta>
            ├── 返回按钮
            ├── 头像 + 姓名 + 角色 + 匹配度
            ├── 个人介绍
            ├── 技能标签
            ├── 作品集图片网格
            ├── 联系方式（需登录查看）
            └── 操作按钮（联系/收藏）
      </Layout>
    </RouterProvider>
  </HelmetProvider>
</StrictMode>
```

---

## 6. 页面设计

### 6.1 首页（Home）

**三阶段递进流程**：

```
┌──────────────────────────────────────────┐
│  Header (Logo + 登录按钮)                  │
├──────────────────────────────────────────┤
│                                          │
│         Super OPC Hub                    │
│  通过 AI 对话探索创意、明确需求...         │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │  [建议1] [建议2] [建议3]            │  │  ← 初始状态：3 个快捷标签
│  └────────────────────────────────────┘  │
│  ┌────────────────────────────────────┐  │
│  │  用户: 我需要一个企业官网设计         │  │
│  │  AI:   好的，请问预算范围是...       │  │  ← 对话状态
│  │  [输入框__________________] [发送] │  │
│  └────────────────────────────────────┘  │
│                                          │
│  ┌───┬───┐                               │
│  │项目│预算│                               │  ← 需求画像（动画出现）
│  │类型│范围│                               │
│  ├───┼───┤                               │
│  │时间│技能│                               │
│  │要求│要求│                               │
│  └───┴───┘                               │
│                                          │
│  ┌──────┐ ┌──────┐ ┌──────┐             │
│  │ OPC1 │ │ OPC2 │ │ OPC3 │             │  ← 匹配结果（卡片网格）
│  │ 95%  │ │ 92%  │ │ 88%  │             │
│  └──────┘ └──────┘ └──────┘             │
│                                          │
├──────────────────────────────────────────┤
│  [首页]  [广场]  [发现]  [我的]           │  ← 底部导航
└──────────────────────────────────────────┘
```

**状态管理**：
- `showDemandProfile`: 控制需求画像显示
- `showOPCMatches`: 控制匹配卡片显示
- 对话提交后依次展示（需求画像 0ms → 匹配结果 500ms 延迟）

### 6.2 登录页（Login）

**两步 OTP 流程**：

1. **邮箱输入阶段**：输入邮箱 → 获取验证码（20 秒冷却）
2. **验证码阶段**：输入 6 位验证码 → 登录/注册

左上角 ✕ 按钮可返回首页。登录成功后自动跳转。

### 6.3 广场页（Square）

社交媒体风格的动态流，包含 4 篇模拟帖子：

| 帖子 | 作者 | 内容主题 | 媒体 |
|------|------|----------|------|
| 1 | 设计师小王 | UI 设计项目分享 | 3 张图（网格 3 列） |
| 2 | 开发者老李 | React 性能优化技巧 | 1 个视频封面 |
| 3 | 产品经理小张 | 产品峰会洞察 | 纯文本 |
| 4 | 创意设计师小陈 | 品牌 VI 设计作品 | 2 张图（网格 2 列） |

**互动功能**（纯本地状态）：
- 点赞/取消点赞（红色爱心动画）
- 关注/取消关注（按钮切换）
- 评论、分享（仅展示数量）

**头像来源**：`i.pravatar.cc`（真人风格头像，按种子固定）

### 6.4 发现页（Discovery）

可缩放产业拓扑图，使用极坐标布局：

```
层级 0（根节点）：OPC 生态（居中）
  ├── 层级 1（一级分类，半径 140px 圆周分布）
  │   ├── 软件开发 (2,156 位)
  │   ├── 设计创意 (1,823 位)
  │   ├── 产品运营 (1,967 位)
  │   ├── 营销推广 (1,345 位)
  │   └── 技术服务 (1,229 位)
  │
  └── 层级 2（点击一级节点后展开，半径 220px 圆周分布）
      └── 例：软件开发 → 前端/后端/移动端/全栈/小程序/游戏/嵌入式
```

**定位算法**：
```typescript
// 圆心偏移：向左 5%, 向上 10%
left: calc(50% + x_px - 5%)
top: calc(50% + y_px - 10%)

// 节点坐标
x = parentX + cos(angle) * radius
y = parentY + sin(angle) * radius
```

每个节点显示 OPC 数量徽章。绿色表示活跃产业，灰色表示暂无 OPC。

### 6.5 个人中心（Profile）

需要登录，未登录自动跳转 `/login`。

**两个 Tab**：

1. **个人资料**：可编辑字段（姓名、电话、个人简介、技能、是否可接单），保存到 Supabase `profiles` 表
2. **历史对话**：从 Supabase 加载会话列表，按 `session_id` 分组，显示创建时间和消息数

### 6.6 OPC 详情页（OPCDetail）

从 URL 参数 `:id` 获取 OPC ID，从 Supabase `opc_profiles` 表加载数据。

- 顶部返回按钮
- 头像 + 姓名 + 角色 + 匹配度星级
- 个人介绍
- 技能标签列表
- 作品集网格（从 `portfolio_urls` 解析）
- 联系方式（未登录显示"登录后即可查看"）
- 操作按钮：联系我、收藏

---

## 7. 数据流设计

### 7.1 数据分层

```
┌──────────────────────────────────────┐
│           UI Components              │
│  (Home, Square, Discovery, etc.)     │
└──────────────┬───────────────────────┘
               │ props / hooks
┌──────────────▼───────────────────────┐
│         Custom Hooks                 │
│  useAuth, useLogin, useIsMobile     │
└──────────────┬───────────────────────┘
               │ API calls
┌──────────────▼───────────────────────┐
│       Supabase Client                │
│  (src/lib/supabase.ts)              │
└──────┬───────────────┬───────────────┘
       │ REST/WS       │ Auth
┌──────▼───────┐ ┌─────▼──────┐
│  PostgreSQL  │ │ Supabase   │
│  (3 tables)  │ │ Auth (OTP) │
└──────────────┘ └────────────┘
```

### 7.2 数据现状

大部分展示数据为前端硬编码的模拟数据：

| 数据 | 来源 | 状态 |
|------|------|------|
| OPC 匹配列表（8 个） | Home.tsx 内部 state | 硬编码 |
| 对话响应 | ChatInterface.tsx 内部 | 模拟（1.5s 延迟） |
| 需求画像 | DemandProfile.tsx 内部 | 硬编码 |
| 广场帖子（4 篇） | Square.tsx 内部 state | 硬编码 |
| 拓扑图节点 | Discovery.tsx 内部 | 硬编码 |
| 用户资料 | Supabase `profiles` 表 | 实时 |
| 对话历史 | Supabase `conversation_history` 表 | 实时 |
| OPC 详情 | Supabase `opc_profiles` 表 | 实时 |
| 认证状态 | Supabase Auth | 实时 |

---

## 8. 数据库设计

### 8.1 表结构

#### conversation_history（对话历史）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 对话记录 ID |
| user_id | UUID FK | 关联用户 |
| session_id | TEXT | 会话标识（同一轮对话共用） |
| role | TEXT | 'user' 或 'assistant' |
| content | TEXT | 对话内容 |
| created_at | TIMESTAMPTZ | 创建时间 |
| updated_at | TIMESTAMPTZ | 更新时间 |
| is_deleted | BOOLEAN | 软删除标记 |

#### demand_profiles（需求画像）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 需求 ID |
| user_id | UUID FK | 关联用户 |
| session_id | TEXT | 关联对话会话 |
| project_type | TEXT | 项目类型 |
| budget_min | DECIMAL(10,2) | 最低预算 |
| budget_max | DECIMAL(10,2) | 最高预算 |
| timeline | TEXT | 时间要求 |
| skills_required | TEXT | 技能需求（逗号分隔） |
| description | TEXT | 需求描述 |
| status | TEXT | 状态：draft/active/completed |
| is_deleted | BOOLEAN | 软删除标记 |

#### opc_profiles（OPC 画像）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | OPC ID |
| user_id | UUID FK | 关联用户（可空） |
| name | TEXT | 姓名 |
| avatar_url | TEXT | 头像 URL |
| role | TEXT | 专业角色 |
| description | TEXT | 个人介绍 |
| skills | TEXT | 技能标签（逗号分隔） |
| portfolio_urls | TEXT | 作品集 URL（逗号分隔） |
| contact_email | TEXT | 联系邮箱 |
| contact_phone | TEXT | 联系电话 |
| is_available | BOOLEAN | 是否可接单 |
| match_score | INT | 匹配分数 |
| is_deleted | BOOLEAN | 软删除标记 |

### 8.2 RLS 安全策略

- **conversation_history**：认证用户只能操作自己的对话记录
- **demand_profiles**：认证用户 CRUD 自己的需求；匿名用户只读 active 状态
- **opc_profiles**：任何人可读 available 的 OPC；认证用户可 INSERT；仅本人可 UPDATE/DELETE

### 8.3 共享功能

- `fn_update_updated_at()` 触发器函数，所有表 UPDATE 时自动更新 `updated_at`
- 三张表均有 `created_at` / `updated_at` / `is_deleted` 审计字段
- 所有表和字段有中英双语注释

---

## 9. 认证流程

```
用户输入邮箱
      │
      ▼
  sendOTP(email)  ← 调用 supabase.auth.signInWithOtp()
      │
      ▼
  显示验证码输入框（20s 冷却倒计时）
      │
      ▼
  用户输入 6 位验证码
      │
      ▼
  verifyOTP(email, otp)  ← 调用 supabase.auth.verifyOtp()
      │
      ├─ 成功 → window.location.assign(returnUrl)
      │
      └─ 失败 → 显示错误信息
```

### 认证 Hook 设计

**useAuth**：提供全局认证状态
- 挂载时检查 Supabase session
- 订阅 `onAuthStateChange` 事件（SIGNED_OUT / SIGNED_IN / TOKEN_REFRESHED）
- 返回 `{ user, loading, isAdmin }`

**useLogin**：管理 OTP 登录流程
- `sendOTP(email, method)` — 发送验证码
- `verifyOTP(email, otp, method)` — 验证码验证
- `reset()` — 重置状态
- 返回 `{ loading, error, otpSent, ... }`

---

## 10. 状态管理策略

采用**分散式状态管理**，不使用全局状态库：

| 状态 | 管理方式 | 范围 |
|------|----------|------|
| 认证状态 | useAuth Hook | 全局（组件内调用） |
| 登录流程 | useLogin Hook + 本地 useState | Login 页面 |
| 对话消息 | ChatInterface 内部 useState | ChatInterface 组件 |
| 首页步骤 | Home 内部 useState | Home 页面 |
| 广场帖子 | Square 内部 useState | Square 页面 |
| 拓扑图缩放 | Discovery 内部 useState | Discovery 页面 |
| 用户资料 | Profile 内部 useState + Supabase | Profile 页面 |
| 路由状态 | React Router | 全局 |
| 移动端检测 | useIsMobile Hook | 按需调用 |

---

## 11. 响应式设计

采用 **mobile-first** 策略，使用 Tailwind 断点：

| 断点 | 宽度 | 适配内容 |
|------|------|----------|
| 默认 | <640px | 手机布局 |
| `sm:` | ≥640px | 平板/小屏 |
| `md:` | ≥768px | 中等屏幕 |
| `lg:` | ≥1024px | 桌面端 |

### 主要响应式处理

- **底部导航**：固定 4 栏，手机端 `h-16`，图标 `w-6 h-6`
- **拓扑图**：移动端半径缩小为 65%（`radius * 0.65`），节点尺寸减小
- **首页标题**：`text-3xl sm:text-4xl lg:text-5xl`
- **OPC 显示**：`max-w-6xl mx-auto`，居中限宽
- **帖子容器**：`max-w-2xl mx-auto`
- **发现页卡片**：`h-[500px] sm:h-[600px] lg:h-[650px]`

---

## 12. 动画设计

使用 Framer Motion 实现动画效果：

| 组件 | 动画 | 参数 |
|------|------|------|
| Login 页面 | 淡入上移 | duration: 0.5s |
| 拓扑图节点 | 缩放出现 | duration: 0.5s, delay: index * 0.08 |
| 广场帖子 | 淡入上移 | duration: 0.3s, delay: index * 0.05 |
| 需求画像 | 淡入上移 | duration: 0.5s |
| 匹配卡片 | 淡入上移 | duration: 0.5s |
| 对话消息 | 缩放出现 | — |

---

## 13. UI 组件清单

### 主动使用的 shadcn/ui 组件

- `Button` — 按钮（多 variant：default/outline/ghost/destructive）
- `Input` — 输入框
- `Label` — 表单标签
- `Card` — 卡片容器
- `Badge` — 标签徽章
- `Avatar` — 头像
- `Tabs` — 标签页切换
- `Textarea` — 多行文本

### 可用但未使用的组件（可供扩展）

accordion, alert-dialog, alert, aspect-ratio, breadcrumb, button-group, calendar, checkbox, collapsible, command, context-menu, dialog, drawer, dropdown-menu, empty, field, form, hover-card, input-group, input-otp, item, menubar, navigation-menu, pagination, popover, progress, radio-group, resizable, scroll-area, select, separator, sheet, sidebar, skeleton, slider, sonner, spinner, switch, table, toggle-group, toggle, tooltip

### 自定义组件

- `PageMeta` — SEO 元信息（react-helmet-async）
- `Header` — 顶部导航栏
- `ChatInterface` — AI 对话界面
- `DemandProfile` — 需求画像卡片
- `OPCMatchCard` — OPC 匹配卡片列表
- `BottomNav` — 底部导航（预留，当前由 Layout 内联实现）

---

## 14. 构建与部署

### 开发命令

```bash
pnpm dev          # 启动开发服务器 (localhost:3000)
pnpm build        # 生产构建
pnpm preview      # 预览构建结果
pnpm type-check   # TypeScript 类型检查
pnpm lint         # Biome 代码检查
```

### Vite 配置要点

- 开发端口：3000
- 路径别名：`@` → `./src`
- SVG 插件：`vite-plugin-svgr`（图标组件化）
- SSR 配置：`react-helmet-async`、`react-router` 支持 SSR

### 环境变量

```env
VITE_SUPABASE_URL=          # Supabase 项目 URL
VITE_SUPABASE_ANON_KEY=     # Supabase 匿名密钥
```

---

## 15. 待扩展功能

1. **AI 对话** — 当前为模拟响应，需接入真实 AI API
2. **OPC 匹配算法** — 当前为静态数据，需实现技能匹配/评分
3. **广场动态发布** — 当前为只读展示，需添加发帖功能
4. **评论/分享** — 当前仅展示数量，需实现交互
5. **通知系统** — 匹配结果通知、关注动态等
6. **搜索/筛选** — 按技能、角色、匹配度筛选 OPC
7. **即时通讯** — 匹配后的沟通渠道
8. **支付/计费** — 项目预算和支付流程
9. **暗色模式** — CSS 变量已定义，需切换逻辑

---

## 16. 后端 AI 匹配系统

### 16.1 架构概览

```
┌────────────────────────────────────────────────────┐
│                  Frontend (React)                   │
│  ChatInterface ─── fetch ───► /api/chat            │
│  DemandProfile ◄── updates ── /api/chat            │
│  OPCMatchCard  ◄── matches ── /api/chat            │
└───────────────────────┬────────────────────────────┘
                        │ HTTP
┌───────────────────────▼────────────────────────────┐
│              Backend (FastAPI + Python)             │
│                                                    │
│  POST /api/chat                                    │
│    │                                               │
│    ├─► 1. LLM 需求提取 (services/extraction.py)    │
│    │      └─ Prompt: 从对话提取结构化需求          │
│    │                                               │
│    ├─► 2. 对话引导生成 (services/extraction.py)    │
│    │      └─ 需求不完整 → 追问                      │
│    │      └─ 需求完整   → 触发匹配                  │
│    │                                               │
│    ├─► 3. OPC 匹配引擎 (services/matching.py)      │
│    │      ├─ 维度1: 技能语义匹配  (40%)            │
│    │      │    └─ Embedding 余弦相似度             │
│    │      ├─ 维度2: 角色适配度    (30%)            │
│    │      │    └─ LLM 评估角色匹配                  │
│    │      ├─ 维度3: 描述相关性    (20%)            │
│    │      │    └─ Embedding 余弦相似度             │
│    │      └─ 维度4: 可接单状态    (10%)            │
│    │                                               │
│    └─► 4. 数据持久化 (db/supabase.py)              │
│           ├─ conversation_history (对话记录)        │
│           └─ demand_profiles     (需求画像)          │
│                                                    │
└───────────────────────┬────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────┐
│              External Services                      │
│  ┌──────────────┐  ┌──────────────┐                │
│  │  LLM API     │  │  Supabase     │                │
│  │  (OpenAI/    │  │  (Auth + DB)  │                │
│  │   兼容接口)   │  │               │                │
│  └──────────────┘  └──────────────┘                │
└────────────────────────────────────────────────────┘
```

### 16.2 目录结构

```
api/
├── main.py                     # FastAPI 入口，路由定义
├── config.py                   # 环境变量配置
├── requirements.txt            # Python 依赖
├── .env.example                # 环境变量模板
├── services/
│   ├── llm.py                  # LLM 客户端（OpenAI 兼容）
│   ├── embedding.py            # 嵌入向量计算 + 缓存
│   ├── extraction.py           # 需求提取 + 对话生成
│   ├── matching.py             # 多维匹配引擎
│   └── prompting.py            # Prompt 模板管理
├── models/
│   └── schemas.py              # Pydantic 数据模型
└── db/
    └── supabase.py             # Supabase 客户端封装
```

### 16.3 API 接口

#### POST /api/chat — 核心对话接口

**请求**：
```json
{
  "session_id": "session_xxx",
  "messages": [
    {"role": "user", "content": "帮我找一个UI设计师"},
    {"role": "assistant", "content": "好的，请问项目预算是多少？"},
    {"role": "user", "content": "预算1-3万"}
  ],
  "user_id": "optional-uuid"
}
```

**响应（需求不完整时）**：
```json
{
  "session_id": "session_xxx",
  "assistant_message": "请问您需要设计的具体是什么类型的项目？比如企业官网、电商App还是小程序？",
  "demand_profile": {
    "project_type": "UI设计",
    "budget_min": 10000,
    "budget_max": 30000,
    "skills_required": ["UI设计"],
    "is_complete": false,
    "missing_fields": ["timeline", "skills_required"]
  },
  "matches": [],
  "is_matching_complete": false
}
```

**响应（需求完整时）**：
```json
{
  "session_id": "session_xxx",
  "assistant_message": "需求已经很清晰了！让我为您匹配最适合的专业人士...",
  "demand_profile": {
    "project_type": "企业官网设计",
    "budget_min": 10000,
    "budget_max": 30000,
    "timeline": "2-4周",
    "skills_required": ["UI设计", "前端开发", "响应式布局"],
    "is_complete": true,
    "missing_fields": []
  },
  "matches": [
    {
      "id": "uuid",
      "name": "张设计师",
      "avatar_url": "https://...",
      "role": "资深 UI 设计师",
      "description": "5年企业官网设计经验...",
      "skills": ["UI设计", "Figma", "品牌设计"],
      "match_rate": 95.0,
      "match_reasons": [
        "技能高度匹配：UI设计、Figma",
        "角色高度匹配：资深 UI 设计师 与项目需求契合",
        "综合匹配度优秀，推荐优先联系"
      ],
      "is_available": true
    }
  ],
  "is_matching_complete": true
}
```

### 16.4 匹配算法详解

```
总匹配度 = 技能语义 × 0.40 + 角色适配 × 0.30 + 描述相关 × 0.20 + 可接单 × 0.10
```

| 维度 | 权重 | 实现方式 | 说明 |
|------|------|----------|------|
| 技能语义匹配 | 40% | Embedding 余弦相似度 | 需求技能 vs OPC 技能 |
| 角色适配度 | 30% | LLM 评分 (0-100) | LLM 判断角色是否匹配项目类型 |
| 描述相关性 | 20% | Embedding 余弦相似度 | 需求描述 vs OPC 介绍 |
| 可接单状态 | 10% | 规则判定 | online=100, offline=30 |

**排序 + 过滤**：
- 按加权总分降序排列
- 过滤低于 `MATCH_MIN_SCORE`（默认 40）的结果
- 返回 Top-K（默认 8）个匹配

### 16.5 LLM 集成

支持任何 OpenAI API 兼容接口，通过环境变量配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLM_API_KEY` | API 密钥 | — |
| `LLM_BASE_URL` | API 地址 | `https://api.openai.com/v1` |
| `LLM_MODEL` | 对话模型 | `gpt-4o` |
| `EMBEDDING_MODEL` | 嵌入模型 | `text-embedding-3-small` |

兼容的 LLM 提供商：
- **OpenAI** — GPT-4o, GPT-4, GPT-3.5
- **DeepSeek** — `LLM_BASE_URL=https://api.deepseek.com/v1`
- **通义千问** — `LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1`
- **本地 Ollama** — `LLM_BASE_URL=http://localhost:11434/v1`
- **Azure OpenAI** — 需适配（配置 base_url 和 api_version）

### 16.6 启动方式

```bash
cd api

# 1. 复制环境变量配置
cp .env.example .env
# 编辑 .env，填入 LLM_API_KEY 和 SUPABASE_SERVICE_KEY

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
uvicorn main:app --reload --port 8000
```

### 16.7 前端集成

前端 `src/lib/api.ts` 封装了 API 调用，`ChatInterface` 组件通过以下回调与后端交互：

- `onDemandUpdate(demand)` — 每次 API 返回需求更新时触发
- `onMatchResults(matches)` — 匹配完成时触发，传入排序后的结果

环境变量 `VITE_API_URL=http://localhost:8000` 配置后端地址。
