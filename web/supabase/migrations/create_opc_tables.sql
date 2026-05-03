-- ============================================
-- Super OPC Hub 数据库表
-- ============================================
-- 删除旧对象
DROP TRIGGER IF EXISTS update_conversation_history_updated_at ON conversation_history;
DROP TRIGGER IF EXISTS update_demand_profiles_updated_at ON demand_profiles;
DROP TRIGGER IF EXISTS update_opc_profiles_updated_at ON opc_profiles;
DROP TABLE IF EXISTS conversation_history CASCADE;
DROP TABLE IF EXISTS demand_profiles CASCADE;
DROP TABLE IF EXISTS opc_profiles CASCADE;
DROP FUNCTION IF EXISTS fn_update_updated_at() CASCADE;
-- 创建共享函数
CREATE OR REPLACE FUNCTION fn_update_updated_at()
RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW(); RETURN NEW; END; $$ LANGUAGE plpgsql;
-- 1. 对话历史表
CREATE TABLE IF NOT EXISTS conversation_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  is_deleted BOOLEAN DEFAULT false NOT NULL
);
COMMENT ON TABLE conversation_history IS '{"chinese_title": "对话历史表", "english_title": "Conversation History", "chinese_description": "存储用户与 AI 智能体的对话记录，支持多轮对话和历史追溯", "english_description": "Stores conversation records between users and AI assistant, supports multi-turn conversations and history tracking"}';
COMMENT ON COLUMN conversation_history.id IS '{"chinese_title": "对话 ID", "english_title": "Conversation ID", "chinese_description": "对话记录的唯一标识符，自动生成 UUID", "english_description": "Unique identifier for conversation record, auto-generated UUID", "format": "uuid"}';
COMMENT ON COLUMN conversation_history.user_id IS '{"chinese_title": "用户 ID", "english_title": "User ID", "chinese_description": "关联的用户 ID，用于标识对话归属", "english_description": "Associated user ID, used to identify conversation ownership", "format": "uuid"}';
COMMENT ON COLUMN conversation_history.session_id IS '{"chinese_title": "会话 ID", "english_title": "Session ID", "chinese_description": "会话标识符，用于 grouping 同一轮对话的多条消息", "english_description": "Session identifier, used to group multiple messages in the same conversation round"}';
COMMENT ON COLUMN conversation_history.role IS '{"chinese_title": "角色", "english_title": "Role", "chinese_description": "消息发送者角色，user 表示用户，assistant 表示 AI", "english_description": "Message sender role, user indicates user, assistant indicates AI", "enum": ["user", "assistant"], "enumDescriptions": ["用户", "AI 助手"]}';
COMMENT ON COLUMN conversation_history.content IS '{"chinese_title": "对话内容", "english_title": "Content", "chinese_description": "对话的具体文本内容", "english_description": "Specific text content of the conversation"}';
COMMENT ON COLUMN conversation_history.created_at IS '{"chinese_title": "创建时间", "english_title": "Created At", "chinese_description": "对话记录的创建时间戳", "english_description": "Creation timestamp of conversation record", "format": "date-time"}';
COMMENT ON COLUMN conversation_history.updated_at IS '{"chinese_title": "更新时间", "english_title": "Updated At", "chinese_description": "对话记录的最后更新时间戳", "english_description": "Last update timestamp of conversation record", "format": "date-time"}';
COMMENT ON COLUMN conversation_history.is_deleted IS '{"chinese_title": "软删除标记", "english_title": "Soft Delete Flag", "chinese_description": "标记该对话是否已被删除", "english_description": "Marks whether this conversation has been deleted"}';
CREATE INDEX idx_conversation_history_user_id ON conversation_history(user_id);
CREATE INDEX idx_conversation_history_session_id ON conversation_history(session_id);
CREATE INDEX idx_conversation_history_is_deleted ON conversation_history(is_deleted);
-- 2. 需求画像表
CREATE TABLE IF NOT EXISTS demand_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  session_id TEXT NOT NULL,
  project_type TEXT NOT NULL,
  budget_min DECIMAL(10,2),
  budget_max DECIMAL(10,2),
  timeline TEXT,
  skills_required TEXT,
  description TEXT,
  status TEXT NOT NULL CHECK (status IN ('draft', 'active', 'completed')) DEFAULT 'draft',
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  is_deleted BOOLEAN DEFAULT false NOT NULL
);
COMMENT ON TABLE demand_profiles IS '{"chinese_title": "需求画像表", "english_title": "Demand Profiles", "chinese_description": "存储通过 AI 对话生成的用户需求画像，用于 OPC 匹配", "english_description": "Stores user demand profiles generated through AI conversations, used for OPC matching"}';
COMMENT ON COLUMN demand_profiles.id IS '{"chinese_title": "需求 ID", "english_title": "Demand ID", "chinese_description": "需求画像的唯一标识符", "english_description": "Unique identifier for demand profile", "format": "uuid"}';
COMMENT ON COLUMN demand_profiles.user_id IS '{"chinese_title": "用户 ID", "english_title": "User ID", "chinese_description": "关联的用户 ID", "english_description": "Associated user ID", "format": "uuid"}';
COMMENT ON COLUMN demand_profiles.session_id IS '{"chinese_title": "会话 ID", "english_title": "Session ID", "chinese_description": "关联的对话会话 ID", "english_description": "Associated conversation session ID"}';
COMMENT ON COLUMN demand_profiles.project_type IS '{"chinese_title": "项目类型", "english_title": "Project Type", "chinese_description": "项目类型描述，如企业官网、电商 APP 等", "english_description": "Project type description, e.g., corporate website, e-commerce APP"}';
COMMENT ON COLUMN demand_profiles.budget_min IS '{"chinese_title": "最低预算", "english_title": "Budget Min", "chinese_description": "项目预算范围的最小值", "english_description": "Minimum value of project budget range"}';
COMMENT ON COLUMN demand_profiles.budget_max IS '{"chinese_title": "最高预算", "english_title": "Budget Max", "chinese_description": "项目预算范围的最大值", "english_description": "Maximum value of project budget range"}';
COMMENT ON COLUMN demand_profiles.timeline IS '{"chinese_title": "时间要求", "english_title": "Timeline", "chinese_description": "项目时间要求，如 2-4 周", "english_description": "Project timeline requirement, e.g., 2-4 weeks"}';
COMMENT ON COLUMN demand_profiles.skills_required IS '{"chinese_title": "技能需求", "english_title": "Skills Required", "chinese_description": "项目需要的技能标签，多个用逗号分隔", "english_description": "Skill tags required for the project, multiple separated by commas"}';
COMMENT ON COLUMN demand_profiles.description IS '{"chinese_title": "需求描述", "english_title": "Description", "chinese_description": "详细的需求描述", "english_description": "Detailed requirement description"}';
COMMENT ON COLUMN demand_profiles.status IS '{"chinese_title": "状态", "english_title": "Status", "chinese_description": "需求状态，控制需求的可见性和匹配", "english_description": "Demand status, controls demand visibility and matching", "enum": ["draft", "active", "completed"], "enumDescriptions": ["草稿", "进行中", "已完成"]}';
COMMENT ON COLUMN demand_profiles.created_at IS '{"chinese_title": "创建时间", "english_title": "Created At", "chinese_description": "需求画像的创建时间戳", "english_description": "Creation timestamp of demand profile", "format": "date-time"}';
COMMENT ON COLUMN demand_profiles.updated_at IS '{"chinese_title": "更新时间", "english_title": "Updated At", "chinese_description": "需求画像的最后更新时间戳", "english_description": "Last update timestamp of demand profile", "format": "date-time"}';
COMMENT ON COLUMN demand_profiles.is_deleted IS '{"chinese_title": "软删除标记", "english_title": "Soft Delete Flag", "chinese_description": "标记该需求是否已被删除", "english_description": "Marks whether this demand has been deleted"}';
CREATE INDEX idx_demand_profiles_user_id ON demand_profiles(user_id);
CREATE INDEX idx_demand_profiles_status ON demand_profiles(status);
CREATE INDEX idx_demand_profiles_is_deleted ON demand_profiles(is_deleted);
-- 3. OPC 画像表
CREATE TABLE IF NOT EXISTS opc_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  name TEXT NOT NULL,
  avatar_url TEXT,
  role TEXT NOT NULL,
  description TEXT,
  skills TEXT,
  portfolio_urls TEXT,
  contact_email TEXT,
  contact_phone TEXT,
  is_available BOOLEAN DEFAULT true NOT NULL,
  match_score INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  is_deleted BOOLEAN DEFAULT false NOT NULL
);
COMMENT ON TABLE opc_profiles IS '{"chinese_title": "OPC 画像表", "english_title": "OPC Profiles", "chinese_description": "存储专业人士（设计师、开发者等）的画像信息，用于需求匹配", "english_description": "Stores professional profiles (designers, developers, etc.) for demand matching"}';
COMMENT ON COLUMN opc_profiles.id IS '{"chinese_title": "OPC ID", "english_title": "OPC ID", "chinese_description": "OPC 画像的唯一标识符", "english_description": "Unique identifier for OPC profile", "format": "uuid"}';
COMMENT ON COLUMN opc_profiles.user_id IS '{"chinese_title": "关联用户 ID", "english_title": "User ID", "chinese_description": "关联的用户 ID，如果 OPC 已注册", "english_description": "Associated user ID, if OPC is registered", "format": "uuid"}';
COMMENT ON COLUMN opc_profiles.name IS '{"chinese_title": "姓名", "english_title": "Name", "chinese_description": "OPC 的姓名或昵称", "english_description": "OPC name or nickname"}';
COMMENT ON COLUMN opc_profiles.avatar_url IS '{"chinese_title": "头像 URL", "english_title": "Avatar URL", "chinese_description": "OPC 头像图片 URL", "english_description": "OPC avatar image URL", "format": "image"}';
COMMENT ON COLUMN opc_profiles.role IS '{"chinese_title": "专业角色", "english_title": "Role", "chinese_description": "专业角色，如 UI 设计师、全栈开发者", "english_description": "Professional role, e.g., UI Designer, Full-stack Developer"}';
COMMENT ON COLUMN opc_profiles.description IS '{"chinese_title": "个人介绍", "english_title": "Description", "chinese_description": "个人介绍和专长描述", "english_description": "Personal introduction and expertise description"}';
COMMENT ON COLUMN opc_profiles.skills IS '{"chinese_title": "技能标签", "english_title": "Skills", "chinese_description": "技能标签，多个用逗号分隔", "english_description": "Skill tags, multiple separated by commas"}';
COMMENT ON COLUMN opc_profiles.portfolio_urls IS '{"chinese_title": "作品集 URL", "english_title": "Portfolio URLs", "chinese_description": "作品集图片 URL，多个用逗号分隔", "english_description": "Portfolio image URLs, multiple separated by commas", "format": "image"}';
COMMENT ON COLUMN opc_profiles.contact_email IS '{"chinese_title": "联系邮箱", "english_title": "Contact Email", "chinese_description": "联系邮箱地址", "english_description": "Contact email address", "format": "email"}';
COMMENT ON COLUMN opc_profiles.contact_phone IS '{"chinese_title": "联系电话", "english_title": "Contact Phone", "chinese_description": "联系电话号码", "english_description": "Contact phone number"}';
COMMENT ON COLUMN opc_profiles.is_available IS '{"chinese_title": "是否可接单", "english_title": "Is Available", "chinese_description": "标记是否可接受新项目", "english_description": "Marks whether available for new projects"}';
COMMENT ON COLUMN opc_profiles.match_score IS '{"chinese_title": "匹配分数", "english_title": "Match Score", "chinese_description": "智能匹配的分数，用于排序", "english_description": "Intelligent matching score for sorting"}';
COMMENT ON COLUMN opc_profiles.created_at IS '{"chinese_title": "创建时间", "english_title": "Created At", "chinese_description": "OPC 画像的创建时间戳", "english_description": "Creation timestamp of OPC profile", "format": "date-time"}';
COMMENT ON COLUMN opc_profiles.updated_at IS '{"chinese_title": "更新时间", "english_title": "Updated At", "chinese_description": "OPC 画像的最后更新时间戳", "english_description": "Last update timestamp of OPC profile", "format": "date-time"}';
COMMENT ON COLUMN opc_profiles.is_deleted IS '{"chinese_title": "软删除标记", "english_title": "Soft Delete Flag", "chinese_description": "标记该 OPC 是否已被删除", "english_description": "Marks whether this OPC has been deleted"}';
CREATE INDEX idx_opc_profiles_user_id ON opc_profiles(user_id);
CREATE INDEX idx_opc_profiles_role ON opc_profiles(role);
CREATE INDEX idx_opc_profiles_is_available ON opc_profiles(is_available);
CREATE INDEX idx_opc_profiles_is_deleted ON opc_profiles(is_deleted);
-- 创建触发器
DROP TRIGGER IF EXISTS trigger_update_conversation_history_updated_at ON conversation_history;
CREATE TRIGGER trigger_update_conversation_history_updated_at BEFORE UPDATE ON conversation_history
  FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
DROP TRIGGER IF EXISTS trigger_update_demand_profiles_updated_at ON demand_profiles;
CREATE TRIGGER trigger_update_demand_profiles_updated_at BEFORE UPDATE ON demand_profiles
  FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
DROP TRIGGER IF EXISTS trigger_update_opc_profiles_updated_at ON opc_profiles;
CREATE TRIGGER trigger_update_opc_profiles_updated_at BEFORE UPDATE ON opc_profiles
  FOR EACH ROW EXECUTE FUNCTION fn_update_updated_at();
-- 插入测试数据
INSERT INTO opc_profiles (name, avatar_url, role, description, skills, is_available, match_score) VALUES
  ('张设计师', 'https://placehold.co/200x200/e2e8f0/475569?text=Avatar
  ('李开发者', 'https://placehold.co/200x200/e2e8f0/475569?text=Avatar
  ('王设计师', 'https://placehold.co/200x200/e2e8f0/475569?text=Avatar
  ('陈工程师', 'https://placehold.co/200x200/e2e8f0/475569?text=Avatar
  ('刘产品经理', 'https://placehold.co/200x200/e2e8f0/475569?text=Avatar
-- 启用 RLS
ALTER TABLE conversation_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE demand_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE opc_profiles ENABLE ROW LEVEL SECURITY;
-- 创建策略
DROP POLICY IF EXISTS "conversation_history_select_own" ON conversation_history;
CREATE POLICY "conversation_history_select_own" ON conversation_history
  FOR SELECT TO authenticated USING (auth.uid() = user_id OR user_id IS NULL);
DROP POLICY IF EXISTS "conversation_history_insert_authenticated" ON conversation_history;
CREATE POLICY "conversation_history_insert_authenticated" ON conversation_history
  FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "conversation_history_update_own" ON conversation_history;
CREATE POLICY "conversation_history_update_own" ON conversation_history
  FOR UPDATE TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "conversation_history_delete_own" ON conversation_history;
CREATE POLICY "conversation_history_delete_own" ON conversation_history
  FOR DELETE TO authenticated USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "demand_profiles_select_own" ON demand_profiles;
CREATE POLICY "demand_profiles_select_own" ON demand_profiles
  FOR SELECT TO authenticated USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "demand_profiles_select_public" ON demand_profiles;
CREATE POLICY "demand_profiles_select_public" ON demand_profiles
  FOR SELECT TO anon USING (status = 'active' AND is_deleted = false);
DROP POLICY IF EXISTS "demand_profiles_insert_authenticated" ON demand_profiles;
CREATE POLICY "demand_profiles_insert_authenticated" ON demand_profiles
  FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "demand_profiles_update_own" ON demand_profiles;
CREATE POLICY "demand_profiles_update_own" ON demand_profiles
  FOR UPDATE TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "demand_profiles_delete_own" ON demand_profiles;
CREATE POLICY "demand_profiles_delete_own" ON demand_profiles
  FOR DELETE TO authenticated USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "opc_profiles_select_public" ON opc_profiles;
CREATE POLICY "opc_profiles_select_public" ON opc_profiles
  FOR SELECT TO anon, authenticated USING (is_available = true AND is_deleted = false);
DROP POLICY IF EXISTS "opc_profiles_insert_authenticated" ON opc_profiles;
CREATE POLICY "opc_profiles_insert_authenticated" ON opc_profiles
  FOR INSERT TO authenticated WITH CHECK (true);
DROP POLICY IF EXISTS "opc_profiles_update_own" ON opc_profiles;
CREATE POLICY "opc_profiles_update_own" ON opc_profiles
  FOR UPDATE TO authenticated USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "opc_profiles_delete_own" ON opc_profiles;
CREATE POLICY "opc_profiles_delete_own" ON opc_profiles
  FOR DELETE TO authenticated USING (auth.uid() = user_id);
-- 授予权限
GRANT SELECT, INSERT, UPDATE, DELETE ON conversation_history TO authenticated;
GRANT SELECT ON conversation_history TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON demand_profiles TO authenticated;
GRANT SELECT ON demand_profiles TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON opc_profiles TO authenticated;
GRANT SELECT ON opc_profiles TO anon;
