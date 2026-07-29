import os
import uuid
from typing import List, Dict, Any, Optional

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None

# We store chromadb in the backend dir, alongside sqlite
DB_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db")


class VectorDBService:
    def __init__(self):
        if not chromadb:
            print("[VectorDB] ChromaDB not installed. Semantic search will not work.")
            self.client = None
            return

        os.makedirs(DB_DIR, exist_ok=True)
        # Initialize chroma client with persistence
        self.client = chromadb.PersistentClient(path=DB_DIR, settings=Settings(anonymized_telemetry=False))
        
        # Collection for transcript chunks
        self.chunks_collection = self.client.get_or_create_collection(
            name="meeting_chunks",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Collection for extracted metadata (topics, summaries, etc.)
        self.metadata_collection = self.client.get_or_create_collection(
            name="meeting_metadata",
            metadata={"hnsw:space": "cosine"}
        )

    def is_available(self) -> bool:
        return self.client is not None

    def add_chunks(self, meeting_id: str, texts: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]], chunk_ids: Optional[List[str]] = None):
        """Add embedded transcript chunks to the DB."""
        if not self.is_available() or not texts:
            return
            
        if not chunk_ids:
            chunk_ids = [f"{meeting_id}_chunk_{i}_{uuid.uuid4().hex[:6]}" for i in range(len(texts))]
            
        # Add to chroma
        self.chunks_collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        print(f"[VectorDB] Added {len(texts)} chunks for meeting {meeting_id}")

    def add_metadata_items(self, meeting_id: str, texts: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        """Add embedded metadata items (topics, action items) to the DB."""
        if not self.is_available() or not texts:
            return
            
        item_ids = [f"{meeting_id}_meta_{i}_{uuid.uuid4().hex[:6]}" for i in range(len(texts))]
        
        self.metadata_collection.add(
            ids=item_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        print(f"[VectorDB] Added {len(texts)} metadata items for meeting {meeting_id}")

    def search_all(self, query_embeddings: List[List[float]], n_results: int = 10, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search across chunks and metadata and combine results."""
        if not self.is_available():
            return []
            
        results = []
        
        try:
            # Query chunks
            chunk_results = self.chunks_collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=filter_dict
            )
            
            # Combine chunk results
            if chunk_results and chunk_results['ids'] and chunk_results['ids'][0]:
                for i in range(len(chunk_results['ids'][0])):
                    results.append({
                        "id": chunk_results['ids'][0][i],
                        "document": chunk_results['documents'][0][i] if chunk_results['documents'] else "",
                        "metadata": chunk_results['metadatas'][0][i] if chunk_results['metadatas'] else {},
                        "distance": chunk_results['distances'][0][i] if chunk_results['distances'] else 0.0,
                        "source": "transcript"
                    })
        except Exception as e:
            print(f"[VectorDB] Error querying chunks: {e}")
            
        try:
            # Query metadata
            meta_results = self.metadata_collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=filter_dict
            )
            
            # Combine meta results
            if meta_results and meta_results['ids'] and meta_results['ids'][0]:
                for i in range(len(meta_results['ids'][0])):
                    results.append({
                        "id": meta_results['ids'][0][i],
                        "document": meta_results['documents'][0][i] if meta_results['documents'] else "",
                        "metadata": meta_results['metadatas'][0][i] if meta_results['metadatas'] else {},
                        "distance": meta_results['distances'][0][i] if meta_results['distances'] else 0.0,
                        "source": "metadata"
                    })
        except Exception as e:
            print(f"[VectorDB] Error querying metadata: {e}")
            
        # Sort by distance (lower is closer/better) and take top n
        results.sort(key=lambda x: x["distance"])
        return results[:n_results]

    def delete_meeting(self, meeting_id: str):
        """Delete all vectors for a given meeting."""
        if not self.is_available():
            return
            
        try:
            self.chunks_collection.delete(where={"meeting_id": meeting_id})
            self.metadata_collection.delete(where={"meeting_id": meeting_id})
            print(f"[VectorDB] Deleted vectors for meeting {meeting_id}")
        except Exception as e:
            print(f"[VectorDB] Error deleting meeting vectors: {e}")

# Singleton instance
vector_db = VectorDBService()
