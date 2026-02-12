'use client';

import { useState, useEffect } from 'react';
import { Users, Plus, Loader2, Hash } from 'lucide-react';
import Link from 'next/link';
import { Face, FaceService } from '@/services/FaceService';
import AppLayout from '@/components/AppLayout';

export default function FacesPage() {
    const [faces, setFaces] = useState<Face[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showCreate, setShowCreate] = useState(false);

    // Creation form state
    const [newName, setNewName] = useState('');
    const [newDisplay, setNewDisplay] = useState('');
    const [newDesc, setNewDesc] = useState('');
    const [createLoading, setCreateLoading] = useState(false);
    const [createError, setCreateError] = useState('');

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
        setCreateError('');

        const token = localStorage.getItem('synapse_token');
        if (!token) {
            setCreateError('Please log in first to create a community.');
            setCreateLoading(false);
            return;
        }

        try {
            await FaceService.createFace({
                name: newName,
                display_name: newDisplay,
                description: newDesc
            }, token);

            setShowCreate(false);
            setNewName('');
            setNewDisplay('');
            setNewDesc('');
            loadFaces();
        } catch (err: any) {
            setCreateError(err.message || 'Failed to create community');
        } finally {
            setCreateLoading(false);
        }
    };

    if (loading) {
        return (
            <AppLayout>
                <div className="flex justify-center p-12">
                    <Loader2 className="h-8 w-8 animate-spin text-purple-500" />
                </div>
            </AppLayout>
        );
    }

    return (
        <AppLayout>
            {/* Header */}
            <div className="sticky top-0 z-10 px-4 py-3.5 border-b glass-strong flex items-center justify-between"
                style={{ borderColor: 'var(--syn-border)' }}>
                <h1 className="text-xl font-bold text-white flex items-center gap-2">
                    <Hash className="h-5 w-5 text-purple-400" />
                    Communities
                </h1>
                <button
                    onClick={() => setShowCreate(!showCreate)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold gradient-accent text-white glow-hover"
                >
                    <Plus className="h-3.5 w-3.5" />
                    {showCreate ? 'Cancel' : 'Create'}
                </button>
            </div>

            {/* Create Form */}
            {showCreate && (
                <div className="px-4 py-4 border-b animate-scale-in" style={{ borderColor: 'var(--syn-border)' }}>
                    <form onSubmit={handleCreate} className="space-y-3">
                        {createError && (
                            <div className="rounded-lg p-3 text-sm text-red-400"
                                style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)' }}>
                                {createError}
                            </div>
                        )}
                        <div>
                            <label className="block text-xs font-medium text-zinc-400 mb-1">Name (URL safe)</label>
                            <input
                                type="text"
                                value={newName}
                                onChange={e => setNewName(e.target.value)}
                                className="w-full rounded-xl px-3 py-2 text-sm focus:outline-none transition-all"
                                style={{ background: 'var(--syn-surface-2)', border: '1px solid var(--syn-border)' }}
                                onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--syn-accent)'; }}
                                onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--syn-border)'; }}
                                placeholder="e.g. machine_learning"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-zinc-400 mb-1">Display Name</label>
                            <input
                                type="text"
                                value={newDisplay}
                                onChange={e => setNewDisplay(e.target.value)}
                                className="w-full rounded-xl px-3 py-2 text-sm focus:outline-none transition-all"
                                style={{ background: 'var(--syn-surface-2)', border: '1px solid var(--syn-border)' }}
                                onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--syn-accent)'; }}
                                onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--syn-border)'; }}
                                placeholder="Machine Learning"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-medium text-zinc-400 mb-1">Description</label>
                            <textarea
                                value={newDesc}
                                onChange={e => setNewDesc(e.target.value)}
                                className="w-full rounded-xl px-3 py-2 text-sm focus:outline-none transition-all resize-none"
                                style={{ background: 'var(--syn-surface-2)', border: '1px solid var(--syn-border)' }}
                                onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--syn-accent)'; }}
                                onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--syn-border)'; }}
                                rows={2}
                                placeholder="What is this community about?"
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={createLoading}
                            className="btn-primary w-full py-2.5 text-sm glow-hover disabled:opacity-50"
                        >
                            {createLoading ? 'Creating...' : 'Create Community'}
                        </button>
                    </form>
                </div>
            )}

            {/* Communities List */}
            {error ? (
                <div className="flex flex-col items-center justify-center py-20">
                    <p className="text-red-400 text-sm">{error}</p>
                </div>
            ) : faces.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-20 animate-fade-in">
                    <Users className="h-16 w-16 text-zinc-600 mb-4" />
                    <h3 className="text-lg font-semibold text-white mb-1">No Communities Yet</h3>
                    <p className="text-zinc-500 text-sm">Create the first community to get started!</p>
                </div>
            ) : (
                <div className="stagger-children">
                    {faces.map(face => (
                        <Link
                            key={face.face_id}
                            href={`/f/${face.name}`}
                            className="flex items-center gap-4 px-4 py-4 border-b hover:bg-white/5 transition-colors"
                            style={{ borderColor: 'var(--syn-border)' }}
                        >
                            {/* Icon */}
                            <div className="h-12 w-12 rounded-xl flex-shrink-0 flex items-center justify-center"
                                style={{ background: 'linear-gradient(135deg, var(--syn-accent-rgb, 139, 92, 246, 0.3), var(--syn-accent-rgb, 139, 92, 246, 0.1))' }}>
                                <span className="text-lg font-bold text-purple-400">f/</span>
                            </div>

                            {/* Info */}
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-0.5">
                                    <h3 className="font-semibold text-white truncate">{face.display_name}</h3>
                                    {face.is_official && (
                                        <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-purple-500/20 text-purple-400 border border-purple-500/30">
                                            Official
                                        </span>
                                    )}
                                </div>
                                <p className="text-zinc-500 text-sm line-clamp-1">{face.description || 'No description.'}</p>
                                <div className="flex gap-3 mt-1 text-xs text-zinc-600">
                                    <span className="flex items-center gap-1">
                                        <Users className="h-3 w-3" /> {face.member_count} members
                                    </span>
                                    <span>{face.post_count} posts</span>
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </AppLayout>
    );
}
