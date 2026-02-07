'use client';

import AppLayout from '../../components/AppLayout';

export default function NotificationsPage() {
    return (
        <AppLayout>
            <div className="p-4">
                <h1 className="text-2xl font-bold mb-4">Notifications</h1>
                <div className="flex flex-col items-center justify-center py-20 text-zinc-500">
                    <p>No new notifications.</p>
                </div>
            </div>
        </AppLayout>
    );
}
