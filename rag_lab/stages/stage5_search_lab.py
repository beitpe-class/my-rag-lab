"""[실습] Stage 5 · 검색 — 질문과 가장 가까운 top-k 조각을 찾는다."""
import pandas as pd
import streamlit as st

from stages.stage3_embed_lab import get_model


def retrieve(query, k):
    """[목표] 질문을 임베딩해 인덱스에서 가장 가까운 조각 k개를 반환.
    출력: list[dict] — records 원소에 "score"(유사도)를 추가한 것

    [구현 단계]
      1) kb = st.session_state.kb  (model_name·index·records 보유)
      2) model = get_model(kb["model_name"])  # 문서와 같은 모델로 질문 인코딩
      3) q = model.encode([query], normalize_embeddings=True).astype("float32")
      4) scores, idx = kb["index"].search(q, k)
      5) idx[0] 의 각 i(>=0)에 대해 records[i] 를 복사하고 score 를 붙여 모은다

    [예제]
        scores, idx = kb["index"].search(q, k)
        for rank, i in enumerate(idx[0]):
            if i < 0: continue
            r = dict(kb["records"][i]); r["score"] = float(scores[0][rank])
            hits.append(r)
    """
    # ✏️ TODO: 질문 임베딩 → 검색 → hits(점수 포함) 반환을 구현하세요.
    raise NotImplementedError("retrieve 를 구현하세요 (Stage 5)")


def render(kb, k):
    """[제공] '5.검색' 탭 — 검색어 → 순위·유사도·출처 표."""
    st.subheader("Stage 5 · 검색  ✏️실습")
    if not kb:
        return
    sq = st.text_input("검색어를 입력하면 가까운 top-k 청크를 보여줍니다", key="lab_search_q")
    if sq:
        hits = retrieve(sq, k)
        st.dataframe(pd.DataFrame([
            {"순위": i + 1, "source": h["source"], "chunk_id": h["chunk_id"],
             "유사도": round(h["score"], 3), "미리보기": h["text"][:80]}
            for i, h in enumerate(hits)]), width='stretch')
