import os
from datetime import datetime
import openai
from supabase import create_client
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Astrology API configuration
ASTRO_API_URL = "https://your-astro-api.onrender.com"  # Replace with your actual URL
ASTRO_API_KEY = os.getenv('ASTRO_API_KEY')

class SoulCache:
    def __init__(self):
        self.headers = {
            "X-API-Key": ASTRO_API_KEY
        }

    def get_astro_context(self):
        """Get current astrological context"""
        try:
            transit_data = requests.get(
                f"{ASTRO_API_URL}/transits", 
                headers=self.headers
            ).json()
            
            return {
                "transit_data": transit_data["transits"],
                "natal_aspects": transit_data["aspects_to_natal"],
                "timestamp": transit_data["timestamp"]
            }
        except Exception as e:
            print(f"Error getting astrological context: {e}")
            return None

    def generate_memory_summary(self, full_text):
        """Generate summary using GPT-4"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze this conversation and return a JSON object with:
                        - A poetic summary
                        - Key topics discussed
                        - The dominant archetypal energy
                        - The emotional tone/mood
                        Format as: {"summary": "...", "keywords": [], "archetype": "...", "mood": "..."}"""
                    },
                    {
                        "role": "user",
                        "content": full_text
                    }
                ]
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error generating summary: {e}")
            return None

    def generate_embedding(self, text):
        """Generate embedding using OpenAI"""
        try:
            response = openai.Embedding.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    def store_session(self, full_text, title=None, session_type=None, tags=None):
        """Store a complete session with astrological context"""
        try:
            # Generate memory summary
            memory = self.generate_memory_summary(full_text)
            if not memory:
                return None

            # Generate embedding
            embedding = self.generate_embedding(full_text)
            if not embedding:
                return None

            # Get astrological context
            astro_context = self.get_astro_context()
            if not astro_context:
                return None

            # Prepare data for storage
            session_data = {
                "full_text": full_text,
                "summary": memory["summary"],
                "keywords": memory["keywords"],
                "archetype": memory["archetype"],
                "mood": memory["mood"],
                "embedding": embedding,
                "transit_data": astro_context["transit_data"],
                "natal_aspects": astro_context["natal_aspects"],
                "title": title,
                "session_type": session_type,
                "tags": tags or []
            }

            # Store in Supabase
            result = supabase.table('sessions').insert(session_data).execute()
            return result.data

        except Exception as e:
            print(f"Error storing session: {e}")
            return None

def main():
    cache = SoulCache()
    
    print("📝 Soul Cache - Chat Session Storage")
    print("===================================")
    
    print("\nPaste your session text (press Ctrl+D when done):")
    session_lines = []
    try:
        while True:
            line = input()
            session_lines.append(line)
    except EOFError:
        session_text = "\n".join(session_lines)
    
    title = input("\nSession title (optional): ")
    tags = input("Tags (comma-separated, optional): ").split(',') if input("Add tags? (y/n): ").lower() == 'y' else None
    
    print("\n🔄 Processing session...")
    result = cache.store_session(
        full_text=session_text,
        title=title,
        tags=tags
    )
    
    if result:
        print("\n✅ Session stored successfully!")
        print("\n🌟 Summary:")
        print(f"Title: {result[0]['title']}")
        print(f"Summary: {result[0]['summary']}")
        print(f"Keywords: {', '.join(result[0]['keywords'])}")
        print(f"Archetype: {result[0]['archetype']}")
        print(f"Mood: {result[0]['mood']}")
        
        print("\n🪐 Astrological Context:")
        print(json.dumps(result[0]["transit_data"], indent=2))
        print("\nNatal Aspects:")
        print(json.dumps(result[0]["natal_aspects"], indent=2))
    else:
        print("\n❌ Error storing session")

if __name__ == "__main__":
    main()
