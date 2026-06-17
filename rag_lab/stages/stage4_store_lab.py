"""[실습] Stage 4 · 저장 — 벡터를 FAISS 인덱스에 적재한다."""
import faiss
import streamlit as st


def build_index(emb):
    """[목표] 임베딩 행렬로 FAISS 인덱스를 만들어 반환.
    입력: emb(np.ndarray N×D, float32) / 출력: faiss 인덱스

    [구현 단계]
      1) 차원 d = emb.shape[1]
      2) 정규화 벡터는 내적 = 코사인 → faiss.IndexFlatIP(d) 생성
      3) index.add(emb) 로 모든 벡터 적재 후 index 반환

    [예제]
        index = faiss.IndexFlatIP(emb.shape[1])
        index.add(emb)
        return index
    """
    # ✏️ TODO: FAISS 내적 인덱스를 만들어 벡터를 넣고 반환하세요.
    raise NotImplementedError("build_index 를 구현하세요 (Stage 4)")


def render(kb):
    """[제공] '4.저장' 탭 — 인덱스 벡터 수·차원."""
    st.subheader("Stage 4 · 저장  ✏️실습")
    if not kb:
        return
    st.metric("인덱스에 저장된 벡터 수", kb["index"].ntotal)
    st.metric("벡터 차원", kb["index"].d)
    st.write("유사도: 정규화 임베딩 + 내적(IndexFlatIP) = 코사인 유사도")
