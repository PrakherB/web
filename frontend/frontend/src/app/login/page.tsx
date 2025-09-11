"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import useUserStore from '../store/user';

export default function LoginPage() {
  const [userId, setUserId] = useState('');
  const router = useRouter();
  const setStoreUserId = useUserStore((state) => state.setUserId);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (userId) {
      setStoreUserId(userId);
      router.push('/dashboard');
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-8">Login</h1>
      <form onSubmit={handleLogin} className="w-full max-w-sm">
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="userId">
            User ID
          </label>
          <input
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            id="userId"
            type="text"
            placeholder="Enter your User ID"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
          />
        </div>
        <div className="flex items-center justify-between">
          <button
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            type="submit"
          >
            Login
          </button>
        </div>
      </form>
    </main>
  );
}
