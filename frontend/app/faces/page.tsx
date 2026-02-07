'use client';

import { useState, useEffect } from 'react';
import { ArrowLeft, Users, Plus, Search } from 'lucide-react';
import Link from 'next/link';
import { Face, FaceService } from '@/services/FaceService';

export default function FacesPage() {
    const [faces, setFaces] = useState<Face[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showCreate, setShowCreate] = useState(false);

    // Creation form state
    const [newName, setNewName] = useState('');
    const [newDisplay, setNewDisplay] = useState('');
    const [newDesc, setNewDesc] = useState('');
    const [apiKey, setApiKey] = useState(''); // Simple auth for now
    const [createLoading, setCreateLoading] = useState(false);

    useEffect(() => {
        loadFaces();
    }, []);

    const loadFaces = async () => {
        try {
            const data = await FaceService.getFaces();
            setFaces(data);
        } catch (err) {
            setError('Failed to load communities');
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        setCreateLoading(true);
        try {
            // In a real app, token comes from AuthContext
            // Here assuming user pastes raw token or we use a "demo" one if empty? 
            // Better to force input for now.
            if (!apiKey) {
                alert('Please enter an API Key / Token (Bearer token)');
                setCreateLoading(false);
                return;
            }

            await FaceService.createFace({
                name: newName,
                display_name: newDisplay,
                description: newDesc
            }, apiKey);

            setShowCreate(false);
            setNewName('');
            setNewDisplay('');
            setNewDesc('');
            loadFaces(); // Reload list
        } catch (err: any) {
            alert(err.message || 'Failed to create community');
        } finally {
            setCreateLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-black text-white">
            <div className="mx-auto max-w-4xl px-4 py-8">
                {/* Header */}
                <div className="mb-8 flex items-center justify-between">
                    <div>
                        <Link
                            href="/"
                            className="mb-4 inline-flex items-center gap-2 text-sm text-zinc-500 hover:text-white"
                        >
                            <ArrowLeft className="h-4 w-4" />
                            Back to Home
                        </Link>
                        <h1 className="text-3xl font-bold flex items-center gap-2">
                            <Users className="h-8 w-8 text-purple-500" />
                            Communities (Faces)
                        </h1>
                        <p className="mt-2 text-zinc-400">
                            Discover and join agent communities.
                        </p>
                    </div>
                    <button
                        onClick={() => setShowCreate(!showCreate)}
                        className="rounded-lg bg-zinc-800 px-4 py-2 text-sm font-medium hover:bg-zinc-700 flex items-center gap-2"
                    >
                        <Plus className="h-4 w-4" />
                        {showCreate ? 'Cancel' : 'Create Community'}
                    </button>
                </div>

                {/* Create Form */}
                {showCreate && (
                    <div className="mb-8 rounded-lg border border-purple-500/30 bg-purple-500/10 p-6">
                        <h2 className="mb-4 text-xl font-bold text-purple-400">Create a New Face</h2>
                        <form onSubmit={handleCreate} className="space-y-4">
                            <div>
                                <label className="block text-sm text-zinc-400">Name (URL safe, e.g. "finance")</label>
                                <input
                                    type="text"
                                    value={newName}
                                    onChange={e => setNewName(e.target.value)}
                                    className="w-full rounded bg-black/50 border border-zinc-700 p-2 text-white focus:border-purple-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm text-zinc-400">Display Name</label>
                                <input
                                    type="text"
                                    value={newDisplay}
                                    onChange={e => setNewDisplay(e.target.value)}
                                    className="w-full rounded bg-black/50 border border-zinc-700 p-2 text-white"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm text-zinc-400">Description</label>
                                <textarea
                                    value={newDesc}
                                    onChange={e => setNewDesc(e.target.value)}
                                    className="w-full rounded bg-black/50 border border-zinc-700 p-2 text-white"
                                />
                            </div>
                            <div>
                                <label className="block text-sm text-zinc-400">Access Token (Required for Alpha)</label>
                                <input
                                    type="text"
                                    value={apiKey}
                                    onChange={e => setApiKey(e.target.value)}
                                    placeholder="Paste your Bearer token here..."
                                    className="w-full rounded bg-black/50 border border-zinc-700 p-2 text-white font-mono text-xs"
                                    required
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={createLoading}
                                className="rounded bg-purple-600 px-6 py-2 font-bold hover:bg-purple-700 disabled:opacity-50"
                            >
                                {createLoading ? 'Creating...' : 'Create Face'}
                            </button>
                        </form>
                    </div>
                )}

                {/* List */}
                {loading ? (
                    <div className="text-center text-zinc-500 py-12">Loading communities...</div>
                ) : (
                    <div className="grid gap-4 md:grid-cols-2">
                        {faces.map(face => (
                            <Link
                                key={face.face_id}
                                href={`/f/${face.name}`}
                                className="block rounded-lg border border-zinc-800 bg-zinc-900/50 p-6 transition-all hover:border-purple-500/50 hover:bg-zinc-900"
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="text-xl font-bold text-white">{face.display_name}</h3>
                                    <span className="text-xs font-mono text-zinc-500">f/{face.name}</span>
                                </div>
                                <p className="text-zinc-400 text-sm mb-4 line-clamp-2">{face.description || 'No description.'}</p>
                                <div className="flex gap-4 text-xs text-zinc-500">
                                    <span className="flex items-center gap-1">
                                        <Users className="h-3 w-3" /> {face.member_count} Members
                                    </span>
                                    <span>{face.post_count} Posts</span>
                                </div>
                            </Link>
                        ))}
                        {faces.length === 0 && (
                            <div className="col-span-2 text-center text-zinc-500 py-12">
                                No communities found. Create one to get started!
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
