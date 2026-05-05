-- =============================================================
-- 003: 合并 profiles 到 opc_profiles + 注册时自动创建 OPC 画像
-- 在 Supabase SQL Editor 中执行
-- =============================================================

-- 1. 先给 opc_profiles 添加缺失的列（仅当列不存在时才添加）
DO $$ BEGIN
    ALTER TABLE public.opc_profiles ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL;
EXCEPTION WHEN duplicate_column THEN NULL;
END $$;

DO $$ BEGIN
    ALTER TABLE public.opc_profiles ADD COLUMN contact_phone TEXT;
EXCEPTION WHEN duplicate_column THEN NULL;
END $$;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_opc_profiles_user_id ON opc_profiles(user_id);

-- 2. 注册时自动创建 opc_profiles 行
CREATE OR REPLACE FUNCTION public.handle_new_user_opc()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    INSERT INTO public.opc_profiles (user_id, name, role)
    VALUES (
        NEW.id,
        COALESCE(split_part(NEW.email, '@', 1), '新用户'),
        '未设置'
    );
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created_opc ON auth.users;
CREATE TRIGGER on_auth_user_created_opc
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user_opc();

-- 3. 确保用户可以读自己的 OPC 画像
DROP POLICY IF EXISTS "opc_profiles_select_own" ON opc_profiles;
CREATE POLICY "opc_profiles_select_own" ON opc_profiles
    FOR SELECT TO authenticated
    USING (auth.uid() = user_id);

-- 4. 确保用户可以更新自己的 OPC 画像
DROP POLICY IF EXISTS "opc_profiles_update_own" ON opc_profiles;
CREATE POLICY "opc_profiles_update_own" ON opc_profiles
    FOR UPDATE TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- 5. 给已注册但还没有 opc_profiles 的用户补建画像
INSERT INTO public.opc_profiles (user_id, name, role)
SELECT
    u.id,
    COALESCE(split_part(u.email, '@', 1), '新用户'),
    '未设置'
FROM auth.users u
LEFT JOIN public.opc_profiles o ON o.user_id = u.id
WHERE o.id IS NULL;
