import os
from datetime import datetime
import openai
from supabase import Client, create_client
from dotenv import load_dotenv
import requests
import json
import argparse
import sys

# [Previous imports and class definitions remain the same...]

def process_chat_session(text, title=None, tags=None, source="manual"):
    """Process and store a chat session"""
    cache = SoulCache()
    print(f"\n📝 Processing chat session from {source}")
    
    result = cache.store_session(
        full_text=text,
        title=title,
        tags=tags
    )
    
    if result:
        print("\n✅ Session stored successfully!")
        summary = {
            "title": result[0]['title'],
            "summary": result[0]['summary'],
            "keywords": result[0]['keywords'],
            "archetype": result[0]['archetype'],
            "mood": result[0]['mood'],
            "astrological_context": {
                "transits": result[0]["transit_data"],
                "natal_aspects": result[0]["natal_aspects"]
            }
        }
        
        # Save summary to file
        summary_file = f"chat_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nSummary saved to: {summary_file}")
        return summary
    else:
        print("\n❌ Error storing session")
        return None

def main():
    parser = argparse.ArgumentParser(description='Store chat sessions with astrological context')
    parser.add_argument('--file', type=str, help='JSON file containing chat data')
    parser.add_argument('--text', type=str, help='Direct chat text')
    parser.add_argument('--title', type=str, help='Session title')
    parser.add_argument('--tags', type=str, help='Comma-separated tags')
    
    args = parser.parse_args()
    
    if args.file:
        # Process from JSON file
        try:
            with open(args.file, 'r') as f:
                data = json.load(f)
            return process_chat_session(
                data.get('text', ''),
                data.get('title'),
                data.get('tags'),
                source=f"file: {args.file}"
            )
        except Exception as e:
            print(f"Error processing file: {e}")
            return None
            
    elif args.text:
        # Process direct text input
        tags = args.tags.split(',') if args.tags else None
        return process_chat_session(
            args.text,
            args.title,
            tags,
            source="command line"
        )
        
    else:
        # Interactive mode
        print("\n📝 Soul Cache - Chat Session Storage")
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
        
        return process_chat_session(session_text, title, tags)

if __name__ == "__main__":
    debug_env()
    main()
