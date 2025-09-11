"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import useUserStore from '../store/user';

interface AnalysisSession {
  id: number;
  session_name: string;
  started_at: string;
  status: string;
  results_count: number;
}

export default function DashboardPage() {
  const router = useRouter();
  const userId = useUserStore((state) => state.userId);
  const [sessions, setSessions] = useState<AnalysisSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!userId) {
      router.push('/login');
      return;
    }

    const fetchSessions = async () => {
      try {
        const response = await fetch(`http://localhost:5000/sessions?userId=${userId}`);
        if (!response.ok) {
          throw new Error('Failed to fetch sessions');
        }
        const data = await response.json();
        setSessions(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
  }, [userId, router]);

  if (!userId) {
    return null;
  }

  if (loading) {
    return <main className="flex min-h-screen flex-col items-center justify-center p-24">Loading...</main>;
  }

  if (error) {
    return <main className="flex min-h-screen flex-col items-center justify-center p-24">Error: {error}</main>;
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-24">
      <h1 className="text-4xl font-bold mb-8">Dashboard</h1>
      <div className="w-full max-w-4xl">
        <h2 className="text-2xl font-bold mb-4">Your Analysis Sessions</h2>
        {sessions.length === 0 ? (
          <p>You have no analysis sessions yet.</p>
        ) : (
          <ul>
            {sessions.map(session => (
              <li key={session.id} className="mb-4 p-4 border rounded shadow">
                <h3 className="text-xl font-semibold">{session.session_name}</h3>
                <p>Started at: {new Date(session.started_at).toLocaleString()}</p>
                <p>Status: {session.status}</p>
                <p>Results: {session.results_count}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  );
}
