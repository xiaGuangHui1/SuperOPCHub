import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';

interface User {
  id: string;
  email: string;
  nickname?: string;
  avatar_url?: string;
  phone?: string;
  role?: string;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();

        console.log('[useAuth] session:', session?.user?.email ?? null);

        if (!session?.user) {
          setUser(null);
          setLoading(false);
          return;
        }

        // 先基于 session 设置最基本的用户信息，
        // 即使 profiles 表查询失败也不影响登录状态
        setUser({
          id: session.user.id,
          email: session.user.email || '',
        });

        try {
          const { data: profile } = await supabase
            .from('opc_profiles')
            .select('*')
            .eq('user_id', session.user.id)
            .single();

          setUser({
            id: session.user.id,
            email: session.user.email || '',
            nickname: profile?.name,
            avatar_url: profile?.avatar_url,
            phone: profile?.contact_phone,
            role: profile?.role,
          });
        } catch {
          // opc_profiles 无记录不影响登录态
          console.warn('无法读取 opc_profiles，使用 session 基本信息');
        }
      } catch (error) {
        // getSession 本身失败才视为未登录
        console.error('Error checking session:', error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkSession();

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event) => {
      if (event === 'SIGNED_OUT') {
        setUser(null);
      } else if (event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED') {
        checkSession();
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const isAdmin = user?.role === 'admin';

  return { user, loading, isAdmin };
}
