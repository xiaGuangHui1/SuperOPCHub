-- =============================================================
-- Super OPC Hub — Supabase 数据库初始化 SQL
-- 在 Supabase SQL Editor 中执行本文件即可创建所有表
-- =============================================================

-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------
-- 1. OPC 画像表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS opc_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    avatar_url TEXT,
    role TEXT NOT NULL,
    description TEXT,
    skills TEXT,           -- 逗号分隔的技能列表，如 "React,Vue,TypeScript"
    is_available BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 示例数据（可选，部署后可删除或修改）
INSERT INTO opc_profiles (name, role, skills, description) VALUES
('张三', '前端开发工程师', 'React,Vue,TypeScript,Next.js,Tailwind CSS', '5年前端开发经验，擅长 React 生态和响应式设计'),
('李四', '全栈开发工程师', 'Python,FastAPI,React,PostgreSQL,Docker', '全栈开发，精通 Python 后端和 React 前端'),
('王五', 'UI/UX 设计师', 'Figma,Sketch,用户研究,交互设计,设计系统', '资深 UI 设计师，有多个 B 端 SaaS 产品设计经验'),
('赵六', '移动端开发工程师', 'React Native,Flutter,Swift,Kotlin,TypeScript', '专注跨平台移动开发，交付过 10+ 上线应用'),
('陈七', '后端开发工程师', 'Go,Python,PostgreSQL,Redis,Kubernetes,gRPC', '后端架构师，擅长高并发系统设计和微服务架构');

-- -----------------------------------------------------------
-- 2. 需求画像表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS demand_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT NOT NULL,
    user_id TEXT,
    project_type TEXT DEFAULT '',
    budget_min FLOAT,
    budget_max FLOAT,
    timeline TEXT DEFAULT '',
    skills_required TEXT DEFAULT '',  -- 逗号分隔
    description TEXT DEFAULT '',
    status TEXT DEFAULT 'active',
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_demand_session ON demand_profiles(session_id, is_deleted);

-- -----------------------------------------------------------
-- 3. 对话历史表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS conversation_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT NOT NULL,
    user_id TEXT,
    role TEXT NOT NULL,       -- 'user' 或 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conv_session ON conversation_history(session_id);
