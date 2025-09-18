import { useState, useEffect } from 'react';
import api from '../services/api';
import { isAuthenticated } from '../services/auth';

interface UserInfo {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  roles: string[];
}

export function useAuth() {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isAuthenticated()) {
      fetchUserInfo();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserInfo = async () => {
    try {
      const res = await api.get('/api/v1/auth/me');
      setUser(res.data);
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const hasRole = (role: string): boolean => {
    return user?.roles?.includes(role) || false;
  };

  const isAdmin = (): boolean => {
    return hasRole('admin');
  };

  return {
    user,
    loading,
    hasRole,
    isAdmin,
    refetch: fetchUserInfo,
  };
}
