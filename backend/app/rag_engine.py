"""
RAG Engine - Core retrieval-augmented generation logic
Handles chunking, embeddings, vector storage, retrieval, reranking, and LLM answering
"""

import os
import time
import hashlib
from typing import List, Dict, Any, Optional
import cohere
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
import google.generativeai as genai
import tiktoken

from .models import Citation, ChunkMetadata


class RAGEngine:
    """
    RAG Engine Configuration:
    - Vector DB: Pinecone (Serverless)
    - Embeddings: Google Gemini text-embedding-005 (768 dimensions) - FREE!
    - Reranker: Cohere Rerank v3
    - LLM: Groq (Llama 3.1 70B)
    
    Chunking Strategy:
    - Chunk size: 1000 tokens
    - Overlap: 100 tokens (10%)
    - Sentence-aware splitting
    """
    
    # Configuration
    CHUNK_SIZE = 1000  # tokens
    CHUNK_OVERLAP = 100  # tokens (10% overlap)
    EMBEDDING_MODEL = "models/text-embedding-005"  # Gemini embedding model
    EMBEDDING_DIMENSIONS = 768  # Gemini embedding dimensions
    INDEX_NAME = "mini-rag"
    RERANK_MODEL = "rerank-v3.5"
    LLM_MODEL = "llama-3.3-70b-versatile"  # Groq model (updated)
    
    def __init__(self):
        """Initialize connections to all services"""
        # Google Gemini for embeddings (FREE!)
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY") or "")  # type: ignore
        
        # Cohere for reranking
        self.cohere_client = cohere.Client(api_key=os.getenv("COHERE_API_KEY") or "")
        
        # Groq for LLM
        self.groq_client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY") or "",
            base_url="https://api.groq.com/openai/v1"
        )
        
        # Pinecone for vector storage
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY") or "")
        self._ensure_index()
        self.index = self.pc.Index(self.INDEX_NAME)  # type: ignore
        
        # Tokenizer for chunking
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def _ensure_index(self):
        """Create Pinecone index if it doesn't exist"""
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        
        if self.INDEX_NAME not in existing_indexes:
            self.pc.create_index(
                name=self.INDEX_NAME,
                dimension=self.EMBEDDING_DIMENSIONS,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            # Wait for index to be ready
            import time
            time.sleep(10)
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))
    
    def _chunk_text(self, text: str, source: str, title: str) -> List[ChunkMetadata]:
        """
        Chunk text into overlapping segments.
        
        Strategy:
        - Target chunk size: 1000 tokens
        - Overlap: 100 tokens (10%)
        - Split on sentence boundaries when possible
        - Preserve metadata for citations
        """
        chunks = []
        
        # Clean and normalize text
        text = text.strip()
        if not text:
            return chunks
        
        # Split into sentences (simple heuristic)
        sentences = self._split_into_sentences(text)
        
        current_chunk = []
        current_tokens = 0
        chunk_index = 0
        char_position = 0
        
        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)
            
            # If single sentence exceeds chunk size, split it
            if sentence_tokens > self.CHUNK_SIZE:
                # Save current chunk if exists
                if current_chunk:
                    chunk_text = " ".join(current_chunk)
                    chunks.append(self._create_chunk_metadata(
                        text=chunk_text,
                        source=source,
                        title=title,
                        position=chunk_index,
                        char_start=char_position - len(chunk_text),
                        char_end=char_position
                    ))
                    chunk_index += 1
                    current_chunk = []
                    current_tokens = 0
                
                # Split long sentence
                words = sentence.split()
                temp_chunk = []
                temp_tokens = 0
                
                for word in words:
                    word_tokens = self._count_tokens(word + " ")
                    if temp_tokens + word_tokens > self.CHUNK_SIZE:
                        chunk_text = " ".join(temp_chunk)
                        chunks.append(self._create_chunk_metadata(
                            text=chunk_text,
                            source=source,
                            title=title,
                            position=chunk_index,
                            char_start=char_position,
                            char_end=char_position + len(chunk_text)
                        ))
                        char_position += len(chunk_text) + 1
                        chunk_index += 1
                        
                        # Keep overlap
                        overlap_words = temp_chunk[-10:] if len(temp_chunk) > 10 else []
                        temp_chunk = overlap_words + [word]
                        temp_tokens = self._count_tokens(" ".join(temp_chunk))
                    else:
                        temp_chunk.append(word)
                        temp_tokens += word_tokens
                
                if temp_chunk:
                    current_chunk = temp_chunk
                    current_tokens = temp_tokens
                continue
            
            # Check if adding sentence exceeds chunk size
            if current_tokens + sentence_tokens > self.CHUNK_SIZE:
                # Save current chunk
                chunk_text = " ".join(current_chunk)
                chunks.append(self._create_chunk_metadata(
                    text=chunk_text,
                    source=source,
                    title=title,
                    position=chunk_index,
                    char_start=char_position,
                    char_end=char_position + len(chunk_text)
                ))
                char_position += len(chunk_text) + 1
                chunk_index += 1
                
                # Start new chunk with overlap
                overlap_tokens = 0
                overlap_sentences = []
                for s in reversed(current_chunk):
                    s_tokens = self._count_tokens(s)
                    if overlap_tokens + s_tokens <= self.CHUNK_OVERLAP:
                        overlap_sentences.insert(0, s)
                        overlap_tokens += s_tokens
                    else:
                        break
                
                current_chunk = overlap_sentences + [sentence]
                current_tokens = overlap_tokens + sentence_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
        
        # Don't forget the last chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(self._create_chunk_metadata(
                text=chunk_text,
                source=source,
                title=title,
                position=chunk_index,
                char_start=char_position,
                char_end=char_position + len(chunk_text)
            ))
        
        # Update total_chunks count
        total = len(chunks)
        for chunk in chunks:
            chunk.total_chunks = total
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        import re
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _create_chunk_metadata(
        self,
        text: str,
        source: str,
        title: str,
        position: int,
        char_start: int,
        char_end: int
    ) -> ChunkMetadata:
        """Create chunk metadata object"""
        return ChunkMetadata(
            source=source,
            title=title,
            section=None,
            position=position,
            chunk_index=position,
            total_chunks=0,  # Updated later
            char_start=char_start,
            char_end=char_end,
            text=text
        )
    
    def _generate_chunk_id(self, source: str, position: int, text: str) -> str:
        """Generate unique ID for a chunk based on source, position, and content hash"""
        # Include text content hash to ensure uniqueness even with same source name
        content = f"{source}:{position}:{hashlib.md5(text.encode()).hexdigest()[:8]}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts using Google Gemini (FREE!)"""
        embeddings = []
        for text in texts:
            result = genai.embed_content(  # type: ignore
                model=self.EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(result['embedding'])
        return embeddings
    
    async def _get_query_embedding(self, text: str) -> List[float]:
        """Generate embedding for query using Google Gemini"""
        result = genai.embed_content(  # type: ignore
            model=self.EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_query"
        )
        return result['embedding']
    
    async def ingest_text(
        self,
        text: str,
        source: str,
        title: str
    ) -> Dict[str, Any]:
        """
        Ingest text into vector database:
        1. Chunk the text
        2. Generate embeddings
        3. Upsert to Pinecone with metadata
        """
        # Chunk the text
        chunks = self._chunk_text(text, source, title)
        
        if not chunks:
            return {"chunks_count": 0}
        
        # Generate embeddings
        chunk_texts = [c.text for c in chunks]
        embeddings = await self._get_embeddings(chunk_texts)
        
        # Prepare vectors for upsert
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector_id = self._generate_chunk_id(source, chunk.position, chunk.text)
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "source": chunk.source,
                    "title": chunk.title,
                    "section": chunk.section or "",
                    "position": chunk.position,
                    "chunk_index": chunk.chunk_index,
                    "total_chunks": chunk.total_chunks,
                    "text": chunk.text
                }
            })
        
        # Upsert to Pinecone (in batches of 100)
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)  # type: ignore
        
        return {"chunks_count": len(chunks)}
    
    async def query(
        self,
        query: str,
        top_k: int = 10,
        rerank_top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Query the RAG system:
        1. Embed the query
        2. Retrieve top-k from Pinecone
        3. Rerank with Cohere
        4. Generate answer with Groq LLM
        """
        timings = {}
        
        # Step 1: Embed query using Gemini
        start = time.time()
        query_embedding = await self._get_query_embedding(query)
        timings['embedding'] = time.time() - start
        
        # Step 2: Retrieve from Pinecone
        start = time.time()
        results = self.index.query(  # type: ignore
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        timings['retrieval'] = time.time() - start
        retrieval_time_ms = round(timings['retrieval'] * 1000, 2)
        
        # Check if we have results
        if not results.matches:
            return self._no_answer_response(timings)
        
        # Step 3: Rerank with Cohere
        start = time.time()
        documents = [match.metadata['text'] for match in results.matches]
        
        rerank_response = self.cohere_client.rerank(
            model=self.RERANK_MODEL,
            query=query,
            documents=documents,
            top_n=rerank_top_k
        )
        timings['rerank'] = time.time() - start
        rerank_time_ms = round(timings['rerank'] * 1000, 2)
        
        # Get reranked results
        reranked_results = []
        for result in rerank_response.results:
            original_match = results.matches[result.index]
            reranked_results.append({
                "text": original_match.metadata['text'],
                "source": original_match.metadata['source'],
                "title": original_match.metadata['title'],
                "section": original_match.metadata.get('section', ''),
                "position": original_match.metadata['position'],
                "relevance_score": result.relevance_score
            })
        
        # Step 4: Generate answer with LLM
        start = time.time()
        answer, tokens_used = await self._generate_answer(query, reranked_results)
        timings['llm'] = time.time() - start
        llm_time_ms = round(timings['llm'] * 1000, 2)
        
        # Prepare citations
        citations = []
        for i, result in enumerate(reranked_results):
            citations.append(Citation(
                id=i + 1,
                text=result['text'][:500] + "..." if len(result['text']) > 500 else result['text'],
                source=result['source'],
                title=result['title'],
                section=result['section'] if result['section'] else None,
                position=result['position'],
                relevance_score=round(result['relevance_score'], 4)
            ))
        
        # Calculate cost estimate
        cost_estimate = self._estimate_cost(tokens_used)
        
        return {
            "answer": answer,
            "citations": citations,
            "sources": reranked_results,
            "retrieval_time_ms": retrieval_time_ms,
            "rerank_time_ms": rerank_time_ms,
            "llm_time_ms": llm_time_ms,
            "tokens_used": tokens_used,
            "cost_estimate": cost_estimate
        }
    
    async def _generate_answer(
        self,
        query: str,
        context_results: List[Dict[str, Any]]
    ) -> tuple[str, Dict[str, int]]:
        """Generate answer using Groq LLM with citations"""
        
        # Build context string with citation markers
        context_parts = []
        for i, result in enumerate(context_results):
            citation_num = i + 1
            context_parts.append(f"[{citation_num}] {result['text']}")
        
        context = "\n\n".join(context_parts)
        
        system_prompt = """You are a helpful assistant that answers questions based on the provided context.
        
Rules:
1. Only use information from the provided context to answer questions.
2. Always include inline citations like [1], [2], etc. to reference which sources you used.
3. If the context doesn't contain enough information to answer the question, say "I don't have enough information to answer this question based on the provided documents."
4. Be concise but thorough in your answers.
5. If multiple sources support a point, cite all of them.
"""
        
        user_prompt = f"""Context:
{context}

Question: {query}

Please provide a comprehensive answer with inline citations [1], [2], etc. referring to the sources above."""
        
        response = self.groq_client.chat.completions.create(
            model=self.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        
        answer = response.choices[0].message.content or ""
        usage = response.usage
        tokens_used = {
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0
        }
        
        return answer, tokens_used
    
    def _no_answer_response(self, timings: Dict[str, float]) -> Dict[str, Any]:
        """Return response when no relevant documents found"""
        return {
            "answer": "I couldn't find any relevant information in the knowledge base to answer your question. Please try uploading relevant documents first or rephrasing your question.",
            "citations": [],
            "sources": [],
            "retrieval_time_ms": round(timings.get('retrieval', 0) * 1000, 2),
            "rerank_time_ms": 0,
            "llm_time_ms": 0,
            "tokens_used": {},
            "cost_estimate": 0.0
        }
    
    def _estimate_cost(self, tokens_used: Dict[str, int]) -> float:
        """
        Estimate cost based on token usage.
        Prices (approximate):
        - OpenAI embedding: $0.00002/1K tokens
        - Cohere rerank: $0.001/search
        - Groq Llama 70B: $0.0007/1K input, $0.0008/1K output
        """
        cost = 0.0
        
        # Embedding cost (rough estimate)
        cost += 0.00002  # Per query
        
        # Rerank cost
        cost += 0.001
        
        # LLM cost
        if tokens_used:
            input_cost = (tokens_used.get('prompt_tokens', 0) / 1000) * 0.0007
            output_cost = (tokens_used.get('completion_tokens', 0) / 1000) * 0.0008
            cost += input_cost + output_cost
        
        return round(cost, 6)
    
    async def clear_index(self):
        """Delete all vectors from the index"""
        self.index.delete(delete_all=True)  # type: ignore
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        stats = self.index.describe_index_stats()  # type: ignore
        return {
            "total_vectors": stats.total_vector_count,
            "dimensions": self.EMBEDDING_DIMENSIONS,
            "index_name": self.INDEX_NAME
        }


# Export for use
__all__ = ['RAGEngine']
