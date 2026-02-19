'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function CommunitiesPage() {
    const router = useRouter();

    useEffect(() => {
        router.replace('/faces');
    }, [router]);

    return (
        <div className="min-h-screen bg-black flex items-center justify-center">
            <div className="h-8 w-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
        </div>
    );
}
