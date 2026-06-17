"""[실습] Stage 3 · 임베딩 — 조각을 의미 벡터로 변환한다."""
import numpy as np
import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer


@st.cache_resource(show_spinner=False)
def get_model(name: str):
    """[제공] 임베딩 모델 로드(비싸므로 캐싱). 그대로 사용하세요."""
    return SentenceTransformer(name)


def embed(records, model):
    """[목표] 조각 텍스트들을 정규화된 임베딩 행렬(float32)로 변환.
    입력: records(list[dict]), model(SentenceTransformer) / 출력: np.ndarray (N×D)

    [구현 단계]
      1) records 에서 텍스트만 추출: [r["text"] for r in records]
      2) model.encode(texts, normalize_embeddings=True) 로 인코딩
         (정규화하면 내적 = 코사인 유사도 → Stage 4/5 에서 활용)
      3) .astype("float32") 로 변환해 반환 (FAISS 요구 타입)

    [예제]
        vecs = model.encode([r["text"] for r in records], normalize_embeddings=True)
        return vecs.astype("float32")
    """
    # ✏️ TODO: 임베딩 행렬을 만들어 반환하세요.
    raise NotImplementedError("embed 를 구현하세요 (Stage 3)")


def pca_2d(emb):
    """[제공] sklearn 없이 SVD로 2D 투영(시각화용). 그대로 사용하세요."""
    X = emb - emb.mean(axis=0, keepdims=True)
    U, S, _ = np.linalg.svd(X, full_matrices=False)
    return U[:, :2] * S[:2]


def render(kb):
    """[제공] '3.임베딩' 탭 — shape·샘플 벡터·PCA 2D 산점도."""
    st.subheader("Stage 3 · 임베딩  ✏️실습")
    if not kb:
        return
    emb = kb["emb"]
    st.write(f"임베딩 행렬 shape: **{emb.shape}** (청크 수 × 차원)")
    st.code(np.round(emb[0][:10], 4).tolist())
    coords = pca_2d(emb)
    proj = pd.DataFrame({"x": coords[:, 0], "y": coords[:, 1],
                         "source": [r["source"] for r in kb["records"]]})
    st.scatter_chart(proj, x="x", y="y", color="source")
