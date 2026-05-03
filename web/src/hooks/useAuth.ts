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

        if (session?.user) {
          const { data: profile } = await supabase
            .from('profiles')
            .select('*')
            .eq('id', session.user.id)
            .single();

          setUser({
            id: session.user.id,
            email: session.user.email || '',
            nickname: profile?.nickname,
            avatar_url: profile?.avatar_url,
            phone: profile?.phone,
            role: profile?.role,
          });
        } else {
          setUser(null);
        }
      } catch (error) {
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
