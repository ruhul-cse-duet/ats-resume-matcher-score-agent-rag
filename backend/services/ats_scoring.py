import re
from .embeddings_index import EmbeddingsIndex
from backend.app.config import Config

def simple_keyword_extract(text: str, min_len: int = 2):
    tokens = re.findall(r"[A-Za-z+#\.\-0-9]+", text)
    tokens = [t for t in tokens if len(t) >= min_len]
    return sorted(set([t.lower() for t in tokens]))

def semantic_score(resume_text: str, jd_text: str, embed_model: str = None):
    embed_model = embed_model or Config.EMBEDDING_MODEL
    emb = EmbeddingsIndex(embed_model)
    # for performance: index resume as single doc
    emb.build([resume_text])
    res = emb.query(jd_text, k=1)
    if not res:
        return 0.0
    return round(res[0][1] * 100, 2)
