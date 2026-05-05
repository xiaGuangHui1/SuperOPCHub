-- =============================================================
-- 004: demand_profiles 表补全缺失列
-- 在 Supabase SQL Editor 中执行
-- =============================================================

-- 添加 demand_profiles 表缺失的列
DO $$ BEGIN
    ALTER TABLE public.demand_profiles ADD COLUMN project_scope TEXT DEFAULT '';
EXCEPTION WHEN duplicate_column THEN NULL;
END $$;

DO $$ BEGIN
    ALTER TABLE public.demand_profiles ADD COLUMN target_users TEXT DEFAULT '';
EXCEPTION WHEN duplicate_column THEN NULL;
END $$;

DO $$ BEGIN
    ALTER TABLE public.demand_profiles ADD COLUMN constraints TEXT DEFAULT '';
EXCEPTION WHEN duplicate_column THEN NULL;
END $$;

DO $$ BEGIN
    ALTER TABLE public.demand_profiles ADD COLUMN collaboration_mode TEXT DEFAULT '';
EXCEPTION WHEN duplicate_column THEN NULL;
END $$;

DO $$ BEGIN
    ALTER TABLE public.demand_profiles ADD COLUMN industry TEXT DEFAULT '';
EXCEPTION WHEN duplicate_column THEN NULL;
END $$;

DO $$ BEGIN
    ALTER TABLE public.demand_profiles ADD COLUMN service_expectations TEXT DEFAULT '';
EXCEPTION WHEN duplicate_column THEN NULL;
END $$;
