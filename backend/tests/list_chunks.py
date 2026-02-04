"""List all chunks in the database to understand the content"""
import os
import sys
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

from pinecone import Pinecone

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
idx = pc.Index('mini-rag')

# Get all vectors
results = idx.query(vector=[0]*768, top_k=50, include_metadata=True)

print("=" * 60)
print("ALL CHUNKS IN DATABASE")
print("=" * 60)
print(f"Total chunks found: {len(results['matches'])}")

for i, match in enumerate(results['matches']):
    meta = match.get('metadata', {})
    print(f"\n{'='*60}")
    print(f"CHUNK {i+1}")
    print(f"{'='*60}")
    print(f"ID: {match['id']}")
    print(f"Source: {meta.get('source', 'N/A')}")
    print(f"Title: {meta.get('title', 'N/A')}")
    print(f"Position: {meta.get('position', 'N/A')}")
    print(f"Text:\n{meta.get('text', 'N/A')[:500]}...")
    print()
