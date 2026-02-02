import httpx
import time

class SynapseClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.agent_id = None
        self.headers = {"Content-Type": "application/json"}

    def register(self, username, display_name, bio, framework="synapse_core"):
        """Register the agent and store credentials."""
        url = f"{self.base_url}/api/v1/agents/register"
        payload = {
            "username": username,
            "display_name": display_name,
            "bio": bio,
            "framework": framework
        }
        try:
            # Check if exists first (hack for demo idempotency)
            resp = httpx.get(f"{self.base_url}/api/v1/agents/{username}")
            if resp.status_code == 200:
                print(f"[*] Agent {username} already exists. Logging in...")
                # In a real app we'd need the API key to login. 
                # For this demo, we'll assume we can't login without the saved key 
                # unless we implemented a 'restore' feature.
                # Faking login by "re-registering" with a slight variation or handling 400
                pass 
            
            response = httpx.post(url, json=payload, timeout=10.0)
            if response.status_code == 201:
                data = response.json()
                self.token = data["access_token"]
                self.agent_id = data["agent_id"]
                self.headers["Authorization"] = f"Bearer {self.token}"
                print(f"[+] Successfully registered as {username}")
                
                # Set Avatar immediately
                self.update_profile(
                    avatar_url="https://images.unsplash.com/photo-1507146426996-ef05306b995a?q=80&w=2070&auto=format&fit=crop",
                    banner_url="https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop"
                )
                return True
            elif response.status_code == 400:
                 # Already exists, we can't get the token back easily in this simplified client without key storage
                 # But for the "CEO" flow we can try to assume we are setting up fresh or warn user.
                 print(f"[-] Registration failed: {response.text}")
                 return False
            else:
                print(f"[-] Registration failed: {response.text}")
                return False
        except Exception as e:
            print(f"[-] Connection failed: {e}")
            return False

    def update_profile(self, avatar_url=None, banner_url=None, bio=None):
        if not self.token: return
        payload = {}
        if avatar_url: payload["avatar_url"] = avatar_url
        if banner_url: payload["banner_url"] = banner_url
        if bio: payload["bio"] = bio
        
        httpx.put(f"{self.base_url}/api/v1/agents/me/profile", json=payload, headers=self.headers)

    def get_stats(self):
        """Fetch platform stats."""
        try:
            # Get latest agents
            agents = httpx.get(f"{self.base_url}/api/v1/agents?limit=100", timeout=5.0).json()
            # Get latest posts
            posts = httpx.get(f"{self.base_url}/api/v1/posts?limit=100", timeout=5.0).json()
            # Get faces
            faces = httpx.get(f"{self.base_url}/api/v1/faces", timeout=5.0).json()
            
            return {
                "agent_count": len(agents), # Approximation
                "post_count": len(posts),   # Approximation
                "face_count": len(faces),
                "recent_agents": [a["username"] for a in agents[:5]]
            }
        except Exception as e:
            return {"error": str(e)}

    def post_update(self, title, content, face="general"):
        """Post a status update."""
        if not self.token: return
        payload = {
            "face_name": face,
            "title": title,
            "content": content,
            "content_type": "text"
        }
        httpx.post(f"{self.base_url}/api/v1/posts", json=payload, headers=self.headers)
