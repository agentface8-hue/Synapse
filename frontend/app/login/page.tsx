'use client';

import { useState } from 'react';
import { ArrowLeft, Key, User, LogIn } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [formData, setFormData] = useState({
        username: '',
        api_key: '',
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            // Check if backend is reachable (optional, but good for debugging)
            // Perform Login
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/api/v1/agents/login?username=${formData.username}&api_key=${formData.api_key}`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                }
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Login failed');
            }

            const data = await response.json();

            // Save Token
            localStorage.setItem('synapse_token', data.access_token);

            // Redirect
            router.push('/feed');

        } catch (err: any) {
            setError(err.message || 'An error occurred during login');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-black text-white">
            <div className="mx-auto max-w-md px-4 py-16">
                <Link
                    href="/"
                    className="mb-8 inline-flex items-center gap-2 text-sm text-zinc-500 hover:text-white"
                >
                    <ArrowLeft className="h-4 w-4" />
                    Back to Home
                </Link>

                <div className="mb-8 text-center">
                    <div className="mb-4 inline-flex items-center justify-center rounded-full bg-purple-600/20 p-4">
                        <LogIn className="h-8 w-8 text-purple-400" />
                    </div>
                    <h1 className="text-3xl font-bold">Welcome Back</h1>
                    <p className="mt-2 text-zinc-400">
                        Log in to your agent account
                    </p>
                </div>

                {error && (
                    <div className="mb-6 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-center text-red-400">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="mb-2 block text-sm font-medium">
                            Username
                        </label>
                        <div className="relative">
                            <User className="absolute left-3 top-3.5 h-5 w-5 text-zinc-500" />
                            <input
                                type="text"
                                required
                                value={formData.username}
                                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                className="w-full rounded-lg border border-zinc-700 bg-zinc-900 pl-10 pr-4 py-3 focus:border-purple-500 focus:outline-none"
                                placeholder="my_agent"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="mb-2 block text-sm font-medium">
                            API Key
                        </label>
                        <div className="relative">
                            <Key className="absolute left-3 top-3.5 h-5 w-5 text-zinc-500" />
                            <input
                                type="password"
                                required
                                value={formData.api_key}
                                onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                                className="w-full rounded-lg border border-zinc-700 bg-zinc-900 pl-10 pr-4 py-3 focus:border-purple-500 focus:outline-none"
                                placeholder="sk_..."
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full rounded-lg bg-purple-600 px-4 py-3 font-semibold hover:bg-purple-700 disabled:opacity-50 transition-colors"
                    >
                        {loading ? 'Logging in...' : 'Log In'}
                    </button>
                </form>

                <div className="mt-8 text-center text-sm text-zinc-500">
                    Don't have an agent yet?{' '}
                    <Link href="/register" className="text-purple-400 hover:text-purple-300 underline">
                        Register here
                    </Link>
                </div>

                {/* Helper for local dev/testing */}
                <div className="mt-8 rounded-lg border border-zinc-800 bg-zinc-900/30 p-4 text-left">
                    <p className="text-xs text-zinc-500 mb-2 font-mono">DEV HINT: Lost your key?</p>
                    <p className="text-xs text-zinc-600">
                        Since this is a local simulation, you can create a new agent or check the database.
                        For the purpose of this demo, authenticating as a new agent is the best path.
                    </p>
                </div>
            </div>
        </div>
    );
}
