const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Face {
    face_id: string;
    name: string;
    display_name: string;
    description: string;
    member_count: number;
    post_count: number;
    is_official: boolean;
    created_at: string;
}

export const FaceService = {
    async getFaces(): Promise<Face[]> {
        const response = await fetch(`${API_URL}/api/v1/faces`);
        if (!response.ok) {
            throw new Error('Failed to fetch faces');
        }
        return response.json();
    },

    async getFace(name: string): Promise<Face> {
        const response = await fetch(`${API_URL}/api/v1/faces/${name}`);
        if (!response.ok) {
            throw new Error('Failed to fetch face');
        }
        return response.json();
    },

    async createFace(data: { name: string; display_name: string; description: string }, token: string): Promise<Face> {
        const response = await fetch(`${API_URL}/api/v1/faces`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create face');
        }
        return response.json();
    }
};
