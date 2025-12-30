from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

_embedding_model = None  # ✅ GLOBAL SINGLETON

class EmbeddingsIndex:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.index = None
        self.texts: List[str] = []

    def _get_model(self):
        global _embedding_model
        if _embedding_model is None:
            logger.info("Loading embedding model into RAM...")
            _embedding_model = SentenceTransformer(self.model_name)
        return _embedding_model


    def build(self, docs: List[str]):
        if not docs:
            raise ValueError("Cannot build index from empty document list")

        model = self._get_model()  # ✅ lazy load

        self.texts = docs
        embeddings = model.encode(
            docs,
            batch_size=16,  # 🔥 lower batch = less RAM spike
            convert_to_numpy=True,
            normalize_embeddings=True  # ✅ avoid manual normalize
        )

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)

        logger.info(f"FAISS index built with {len(docs)} documents")


    def query(self, q: str, k: int = 3) -> List[Tuple[str, float]]:
        if self.index is None:
            raise RuntimeError("Index not built")

        if not q.strip():
            return []

        model = self._get_model()

        q_emb = model.encode(
            [q],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        k = min(k, len(self.texts))
        scores, indices = self.index.search(q_emb, k)

        return [
            (self.texts[i], float(score))
            for i, score in zip(indices[0], scores[0])
            if i < len(self.texts)
        ]

