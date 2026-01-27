/**
 * Zustand store for user state management
 * Manages user information and authentication state
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * User store interface
 */
interface UserState {
  userId: string | null;
  userEmail: string | null;
  setUserId: (userId: string) => void;
  setUserEmail: (email: string) => void;
  reset: () => void;
}

/**
 * Create user store with persistence
 */
export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      // State
      userId: null,
      userEmail: null,

      // Actions
      setUserId: (userId: string) =>
        set({
          userId,
        }),

      setUserEmail: (userEmail: string) =>
        set({
          userEmail,
        }),

      reset: () =>
        set({
          userId: null,
          userEmail: null,
        }),
    }),
    {
      name: 'user-store',
    }
  )
);
