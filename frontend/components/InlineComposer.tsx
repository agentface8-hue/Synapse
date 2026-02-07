'use client';

import { useState } from 'react';
import { Image, X } from 'lucide-react';

interface InlineComposerProps {
    onPostCreated?: () => void;
}

export default function InlineComposer({ onPostCreated }: InlineComposerProps) {
    const [content, setContent] = useState('');
    const [loading, setLoading] = useState(false);
    const [previewUrl, setPreviewUrl] = useState('');
    const [mediaType, setMediaType] = useState<'image' | 'video' | null>(null);

    // Mock functionality: In a real app, this would upload to S3/Supabase
    // Here we just let users paste a URL for "media"
    const [showUrlInput, setShowUrlInput] = useState(false);
    const [mediaUrl, setMediaUrl] = useState('');

    const handlePost = async () => {
        if (!content.trim() && !mediaUrl) return;

        setLoading(true);
        try {
            // Use our existing API
            // For now, we need to handle Auth. 
            // In a real app, we'd use a context/hook. 
            // Here, we might need to prompt or assume a token is stored.
            // For the prototype, we'll just log or error if no token.
            const token = localStorage.getItem('synapse_token'); // Simple hack for prototype
            if (!token) {
                alert('You must be logged in to post (simulated via token)');
                setLoading(false);
                return;
            }

            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/posts`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    face_name: 'general', // Default to general for main feed
                    title: content.slice(0, 50) + (content.length > 50 ? '...' : ''), // Auto-title
                    content: content,
                    url: mediaUrl || undefined,
                    content_type: mediaType || 'text'
                })
            });

            if (!response.ok) {
                throw new Error('Failed to post');
            }

            setContent('');
            setMediaUrl('');
            setShowUrlInput(false);
            if (onPostCreated) onPostCreated();

        } catch (error) {
            console.error(error);
            alert('Failed to post. Ensure you are logged in.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="border-b border-zinc-800 p-4">
            <div className="flex gap-4">
                <div className="h-10 w-10 rounded-full bg-zinc-800"></div> {/* Avatar stub */}
                <div className="flex-1">
                    <textarea
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        placeholder="What is happening?!"
                        className="w-full bg-transparent text-xl placeholder-zinc-500 focus:outline-none resize-none min-h-[50px]"
                        rows={2}
                    />

                    {mediaUrl && (
                        <div className="relative mt-2 mb-4 rounded-xl overflow-hidden border border-zinc-800">
                            <img src={mediaUrl} alt="Preview" className="max-h-[300px] w-full object-cover" onError={() => setMediaType('video')} />
                            <button
                                onClick={() => setMediaUrl('')}
                                className="absolute top-2 right-2 rounded-full bg-black/50 p-1 text-white hover:bg-black/70"
                            >
                                <X className="h-4 w-4" />
                            </button>
                        </div>
                    )}

                    {showUrlInput && (
                        <div className="mt-2 mb-4 flex gap-2">
                            <input
                                type="text"
                                value={mediaUrl}
                                onChange={(e) => setMediaUrl(e.target.value)}
                                placeholder="Paste image/video URL..."
                                className="flex-1 rounded-lg bg-zinc-900 px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-purple-500"
                            />
                            <button onClick={() => setShowUrlInput(false)} className="text-zinc-500 hover:text-white">
                                <X className="h-4 w-4" />
                            </button>
                        </div>
                    )}

                    <div className="mt-2 flex items-center justify-between border-t border-zinc-800 pt-2">
                        <div className="flex gap-2 text-purple-500">
                            <button
                                onClick={() => setShowUrlInput(!showUrlInput)}
                                className="rounded-full p-2 hover:bg-purple-500/10 transition-colors"
                            >
                                <Image className="h-5 w-5" />
                            </button>
                            {/* gif, poll, emoji stubs */}
                        </div>
                        <button
                            onClick={handlePost}
                            disabled={!content.trim() && !mediaUrl || loading}
                            className="rounded-full bg-purple-600 px-4 py-1.5 font-bold text-white hover:bg-purple-700 disabled:opacity-50 transition-colors"
                        >
                            {loading ? 'Posting...' : 'Post'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
