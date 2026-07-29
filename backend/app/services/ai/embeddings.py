from typing import List
import os

# Default to sentence-transformers if not configured otherwise
try:
    from sentence_transformers import SentenceTransformer
    # We load a small, fast model suitable for local use
    _model = SentenceTransformer('all-MiniLM-L6-v2')
except ImportError:
    _model = None


class EmbeddingService:
    def __init__(self):
        self.model = _model
        if not self.model:
            print("[Embeddings] sentence-transformers not installed. Embeddings will not be generated locally.")

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        if not self.model:
            return []
        
        # SentenceTransformer returns numpy array, we need a list of floats
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def chunk_transcript(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """
        Split a transcript into overlapping chunks of approximately `chunk_size` words.
        """
        if not text:
            return []
            
        words = text.split()
        if not words:
            return []
            
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            i += chunk_size - overlap
            
        return chunks


# Singleton instance
embedding_service = EmbeddingService()
