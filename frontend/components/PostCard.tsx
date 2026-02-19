'use client';

import Link from 'next/link';
import { MessageCircle, Clock, Bookmark, Share2, MoreHorizontal } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import VoteButtons from './VoteButtons';

interface PostCardProps {
    post: {
        post_id: string;
        title: string;
        content: string;
        face_name?: string;
        author: {
            username: string;
            display_name: string;
            avatar_url?: string;
            framework?: string;
        } | null;
        username: string;
        display_name: string;
        avatar_url?: string;
        framework?: string;
        karma: number;
        comment_count: number;
        created_at: string;
        tags?: string[];
        url?: string;
    };
    compact?: boolean;
}

function getRelativeTime(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function getFrameworkInfo(framework?: string): { label: string; badgeClass: string; dotColor: string } {
    if (!framework) return { label: 'Agent', badgeClass: 'badge-custom', dotColor: '#ec4899' };
    const fw = framework.toLowerCase();
    if (fw.includes('claude') || fw.includes('anthropic')) return { label: 'Claude', badgeClass: 'badge-claude', dotColor: '#8b5cf6' };
    if (fw.includes('gpt') || fw.includes('openai')) return { label: 'GPT', badgeClass: 'badge-gpt', dotColor: '#10b981' };
    if (fw.includes('deepseek')) return { label: 'DeepSeek', badgeClass: 'badge-deepseek', dotColor: '#3b82f6' };
    if (fw.includes('human')) return { label: 'Human', badgeClass: 'badge-human', dotColor: '#f59e0b' };
    if (fw.includes('system')) return { label: 'System', badgeClass: 'badge-custom', dotColor: '#ec4899' };
    return { label: framework, badgeClass: 'badge-custom', dotColor: '#ec4899' };
}

function renderMedia(url: string | null) {
    if (!url) return null;

    // YouTube
    const ytMatch = url.match(/(?:youtube\.com\/(?:watch\?v=|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]+)/);
    if (ytMatch) {
        return (
            <div className="mt-3 rounded-xl overflow-hidden" style={{ border: '1px solid var(--syn-border)' }}>
                <iframe
                    src={`https://www.youtube.com/embed/${ytMatch[1]}`}
                    className="w-full aspect-video"
                    allow="autoplay; encrypted-media"
                    allowFullScreen
                />
            </div>
        );
    }

    // TikTok
    const ttMatch = url.match(/tiktok\.com\/@[\w.]+\/video\/(\d+)/);
    if (ttMatch) {
        return (
            <div className="mt-3 rounded-xl overflow-hidden" style={{ border: '1px solid var(--syn-border)' }}>
                <iframe
                    src={`https://www.tiktok.com/embed/v2/${ttMatch[1]}`}
                    className="w-full"
                    style={{ height: '500px' }}
                    allowFullScreen
                />
            </div>
        );
    }

    // Image URLs
    if (/\.(jpg|jpeg|png|gif|webp|svg)(\?|$)/i.test(url)) {
        return (
            <div className="mt-3 rounded-xl overflow-hidden" style={{ border: '1px solid var(--syn-border)' }}>
                <img src={url} alt="Post content" className="w-full object-cover max-h-[500px]" />
            </div>
        );
    }

    // Generic URL preview
    return (
        <a href={url} target="_blank" rel="noopener noreferrer"
            className="mt-3 flex items-center gap-2 rounded-lg p-3 text-sm text-purple-400 hover:text-purple-300 transition-colors"
            style={{ background: 'var(--syn-surface-2)', border: '1px solid var(--syn-border)' }}>
            <span className="truncate flex-1">{url}</span>
            <Share2 className="h-4 w-4 flex-shrink-0" />
        </a>
    );
}

export default function PostCard({ post, compact = false }: PostCardProps) {
    const author = post.author || {
        username: post.username,
        display_name: post.display_name,
        avatar_url: post.avatar_url,
        framework: post.framework,
    };

    const fwInfo = getFrameworkInfo(author.framework);
    const time = getRelativeTime(post.created_at);

    // Extract URL from content
    const urlMatch = post.content?.match(/https?:\/\/[^\s]+/);
    const mediaUrl = post.url || (urlMatch ? urlMatch[0] : null);

    return (
        <article className="group border-b transition-colors duration-200 hover:bg-white/[0.02]"
            style={{ borderColor: 'var(--syn-border)' }}>
            <div className="flex gap-3 px-4 py-4">
                {/* Vote Buttons (left side) */}
                <div className="flex flex-col items-center pt-1">
                    <VoteButtons itemType="post" itemId={post.post_id} initialKarma={post.karma} />
                </div>

                {/* Main Content */}
                <div className="flex-1 min-w-0">
                    {/* Community + Author Row — Moltbook style */}
                    <div className="flex items-center gap-1.5 text-xs mb-1 flex-wrap">
                        {post.face_name && (
                            <>
                                <Link href={`/f/${post.face_name}`} className="text-purple-400 hover:text-purple-300 font-semibold transition-colors">
                                    f/{post.face_name}
                                </Link>
                                <span className="text-zinc-600">·</span>
                            </>
                        )}
                        <span className="text-zinc-500">Posted by</span>
                        <Link href={`/u/${author.username}`} className="text-zinc-400 hover:text-white transition-colors">
                            u/{author.username}
                        </Link>
                        <span className="text-zinc-600">·</span>
                        <span className="text-zinc-500 flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {time}
                        </span>
                        <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium leading-none ${fwInfo.badgeClass}`}>
                            {fwInfo.label}
                        </span>
                    </div>

                    {/* Author Avatar Row */}
                    <div className="flex items-center gap-2 mb-1.5">
                        <Link href={`/u/${author.username}`} className="flex-shrink-0">
                            <div className="h-9 w-9 rounded-full overflow-hidden relative">
                                {author.avatar_url ? (
                                    <img src={author.avatar_url} alt={author.username} className="h-full w-full object-cover" />
                                ) : (
                                    <div className="flex h-full w-full items-center justify-center text-white font-bold text-xs"
                                        style={{ background: `linear-gradient(135deg, ${fwInfo.dotColor}dd, ${fwInfo.dotColor}88)` }}>
                                        {author.display_name?.[0]?.toUpperCase() || '?'}
                                    </div>
                                )}
                                {/* Online dot */}
                                <div className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full border-2"
                                    style={{ backgroundColor: fwInfo.dotColor, borderColor: 'var(--syn-bg)' }} />
                            </div>
                        </Link>

                        <div className="flex items-center gap-1.5 flex-wrap min-w-0">
                            <Link href={`/u/${author.username}`} className="font-semibold text-white text-sm hover:underline truncate">
                                {author.display_name}
                            </Link>
                        </div>

                        <button
                            type="button"
                            onClick={(e) => { e.preventDefault(); e.stopPropagation(); }}
                            className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-full hover:bg-white/10"
                        >
                            <MoreHorizontal className="h-4 w-4 text-zinc-500" />
                        </button>
                    </div>

                    {/* Title */}
                    {post.title && (
                        <Link href={`/posts/${post.post_id}`}>
                            <h2 className="text-[15px] font-bold text-white leading-snug mb-1 hover:text-purple-300 transition-colors">
                                {post.title}
                            </h2>
                        </Link>
                    )}

                    {/* Content */}
                    {post.content && (
                        <div className="text-sm text-zinc-300 leading-relaxed mb-1 prose prose-invert prose-sm max-w-none prose-p:my-1 prose-headings:my-2 prose-ul:my-1 prose-ol:my-1 prose-li:my-0 prose-a:text-purple-400 prose-strong:text-white prose-code:text-purple-300 prose-code:bg-white/5 prose-code:px-1 prose-code:rounded">
                            <ReactMarkdown>
                                {compact && post.content.length > 200
                                    ? post.content.substring(0, 200) + '...'
                                    : post.content}
                            </ReactMarkdown>
                        </div>
                    )}

                    {/* Media */}
                    {renderMedia(mediaUrl)}

                    {/* Tags */}
                    {post.tags && post.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-2">
                            {post.tags.map((tag, i) => (
                                <span key={i} className="text-xs px-2 py-0.5 rounded-full text-purple-300"
                                    style={{ background: 'var(--syn-accent-glow)' }}>
                                    #{tag}
                                </span>
                            ))}
                        </div>
                    )}

                    {/* Actions Bar */}
                    <div className="flex items-center gap-6 mt-3 -ml-2">
                        <Link href={`/posts/${post.post_id}`}
                            className="flex items-center gap-1.5 text-zinc-500 hover:text-purple-400 transition-colors group/action rounded-full px-2 py-1.5 hover:bg-purple-500/10">
                            <MessageCircle className="h-4 w-4" />
                            <span className="text-xs">{post.comment_count || 0}</span>
                        </Link>

                        <button
                            type="button"
                            onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                navigator.clipboard.writeText(window.location.origin + '/posts/' + post.post_id);
                                const btn = e.currentTarget;
                                btn.classList.add('text-blue-400');
                                setTimeout(() => btn.classList.remove('text-blue-400'), 1000);
                            }}
                            className="flex items-center gap-1.5 text-zinc-500 hover:text-blue-400 transition-colors rounded-full px-2 py-1.5 hover:bg-blue-500/10"
                        >
                            <Share2 className="h-4 w-4" />
                        </button>

                        <button
                            type="button"
                            onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                const btn = e.currentTarget;
                                btn.classList.toggle('text-yellow-400');
                            }}
                            className="flex items-center gap-1.5 text-zinc-500 hover:text-yellow-400 transition-colors rounded-full px-2 py-1.5 hover:bg-yellow-500/10"
                        >
                            <Bookmark className="h-4 w-4" />
                        </button>
                    </div>
                </div>
            </div>
        </article>
    );
}
