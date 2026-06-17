"""[실습 워크북] RAG 단계별 모니터링 — 수강생이 직접 채우는 버전.

stages/stageN_*_lab.py 의 ✏️TODO 함수를 구현하면 각 탭에 결과가 나타납니다.
구현 전 단계는 친절한 안내가 표시되어 앱이 죽지 않습니다.

실행:  pipenv run streamlit run app_lab.py
정답:  app.py (기본 코드) / 모범답안: app_solution.py 와 비교
"""
import streamlit as st

from stages.stage1_load_lab import load_documents
from stages.stage2_chunk_lab import make_chunks
from stages.stage3_embed_lab import get_model, embed
from stages.stage4_store_lab import build_index
from stages.stage6_generate_lab import _get_api_key
from stages import (stage1_load_lab, stage2_chunk_lab, stage3_embed_lab, stage4_store_lab,
                    stage5_search_lab, stage6_generate_lab, stage7_chat_lab, stage8_eval_lab)

MODELS = {
    "영어 위주 · all-MiniLM-L6-v2": "all-MiniLM-L6-v2",
    "다국어/한국어 · paraphrase-multilingual-MiniLM-L12-v2":
        "paraphrase-multilingual-MiniLM-L12-v2",
}

st.set_page_config(page_title="RAG 실습 워크북", page_icon="✏️", layout="wide")
st.title("✏️ RAG 파이프라인 실습 워크북")
st.caption("stages/stageN_*_lab.py 의 TODO를 채우세요 · 가상·공개 문서만 사용")


def safe_render(fn, *args):
    """구현 전(TODO) 단계는 안내만 표시하고 앱이 죽지 않게 한다."""
    try:
        fn(*args)
    except NotImplementedError as e:
        st.info(f"✏️ 아직 구현 전입니다 → {e}")
    except Exception as e:  # noqa: BLE001
        st.error(f"오류: {e}")


with st.sidebar:
    st.header("입력 & 설정")
    files = st.file_uploader("PDF / TXT / MD", type=["pdf", "txt", "md"],
                             accept_multiple_files=True)
    include_folder = st.checkbox("docs/ 폴더 포함", value=True)
    model_name = MODELS[st.selectbox("임베딩 모델", list(MODELS.keys()))]
    c1, c2 = st.columns(2)
    size = c1.slider("청크 크기", 200, 1000, 500, 50)
    overlap = c2.slider("오버랩", 0, 200, 80, 10)
    overlap = min(overlap, size - 50)   # 청크 폭발 방어
    k = st.slider("top-k", 1, 8, 4)

    if st.button("▶ 파이프라인 실행", use_container_width=True):
        try:
            docs = load_documents(files, include_folder)      # Stage 1
            records = make_chunks(docs, size, overlap)        # Stage 2
            if not records:
                st.warning("문서가 없거나 텍스트 추출 실패.")
            else:
                with st.spinner(f"{len(records)}개 청크 임베딩 중..."):
                    model = get_model(model_name)
                    emb = embed(records, model)               # Stage 3
                    index = build_index(emb)                  # Stage 4
                st.session_state.kb = {
                    "model_name": model_name, "docs": docs, "records": records,
                    "emb": emb, "index": index, "size": size, "overlap": overlap,
                }
                st.success(f"완료 · 문서 {len(docs)} · 청크 {len(records)}")
        except NotImplementedError as e:
            st.warning(f"✏️ 구현이 필요합니다 → {e}")

    if not _get_api_key():
        st.info("GEMINI_API_KEY 미설정 — Gemini 키 없으면 로컬 Ollama 로 생성(가능 시)")

tabs = st.tabs(["1.적재/파싱", "2.청킹", "3.임베딩", "4.저장",
                "5.검색", "6.생성", "7.챗봇", "8.평가/검수"])
kb = st.session_state.get("kb")

with tabs[0]: safe_render(stage1_load_lab.render, kb)
with tabs[1]: safe_render(stage2_chunk_lab.render, kb)
with tabs[2]: safe_render(stage3_embed_lab.render, kb)
with tabs[3]: safe_render(stage4_store_lab.render, kb)
with tabs[4]: safe_render(stage5_search_lab.render, kb, k)
with tabs[5]: safe_render(stage6_generate_lab.render, kb, k)
with tabs[6]: safe_render(stage7_chat_lab.render, kb, k)
with tabs[7]: safe_render(stage8_eval_lab.render, kb, k)
