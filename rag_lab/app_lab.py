"""[실습 워크북] RAG 단계별 모니터링 — 수강생이 직접 채우는 버전.

stages/stageN_*_lab.py 의 ✏️TODO 함수를 구현하면 각 탭에 결과가 나타납니다.
각 탭의 '이 단계 실행' 버튼으로 단계를 따로따로 실행할 수 있어, 모든 단계를
다 구현하지 않아도 완성한 단계까지의 중간 결과를 바로 확인할 수 있습니다.
(사이드바의 '전체 파이프라인 실행' 은 1~4단계를 한 번에 실행합니다.)

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
st.caption("각 탭의 '이 단계 실행' 버튼으로 단계별 실행 · 가상·공개 문서만 사용")

# 단계별 산출물을 누적 저장하는 통합 상태(kb). 단계를 실행할 때마다 채워진다.
kb = st.session_state.setdefault("kb", {})

# 빌드 단계 산출 키 순서 — 상위 단계를 다시 실행하면 하위 결과를 비워 오래된 값 방지.
BUILD_KEYS = ["docs", "records", "emb", "index"]


def _clear_after(key):
    """key 다음 단계의 산출물을 제거(상위 단계 재실행 시 하위 결과 무효화)."""
    if key in BUILD_KEYS:
        for stale in BUILD_KEYS[BUILD_KEYS.index(key) + 1:]:
            kb.pop(stale, None)


def safe_render(fn, *args):
    """구현 전(TODO)·오류 단계도 안내만 표시하고 앱이 죽지 않게 한다."""
    try:
        fn(*args)
    except NotImplementedError as e:
        st.info(f"✏️ 아직 구현 전입니다 → {e}")
    except Exception as e:  # noqa: BLE001
        st.error(f"오류: {e}")


def run_step(label, key, compute, need_key=None, need_msg=""):
    """'이 단계 실행' 버튼. 누르면 compute() 결과를 kb[key] 에 저장한다.
    need_key: 선행 단계 산출물 키(없으면 안내만). 성공/실패 모두 앱은 유지된다."""
    if st.button(label, key=f"run_{key}", use_container_width=True):
        if need_key and need_key not in kb:
            st.warning(f"⚠️ {need_msg}")
            return
        try:
            kb[key] = compute()
            _clear_after(key)
            st.success(f"✅ {label} 완료")
        except NotImplementedError as e:
            st.warning(f"✏️ 구현이 필요합니다 → {e}")
        except Exception as e:  # noqa: BLE001
            st.error(f"오류: {e}")


def gated_render(ready_key, hint, render_fn, *args):
    """선행 산출물(ready_key)이 있으면 render, 없으면 안내."""
    if ready_key in kb:
        safe_render(render_fn, *args)
    else:
        st.info(hint)


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

    st.divider()
    if st.button("▶ 전체 파이프라인 실행", use_container_width=True,
                 help="Stage 1~4를 한 번에 실행(구현 안 된 단계에서 멈춤)"):
        try:
            kb["docs"] = load_documents(files, include_folder)         # Stage 1
            kb["records"] = make_chunks(kb["docs"], size, overlap)     # Stage 2
            if not kb["records"]:
                st.warning("문서가 없거나 텍스트 추출 실패.")
            else:
                with st.spinner(f"{len(kb['records'])}개 청크 임베딩 중..."):
                    kb["model_name"] = model_name
                    kb["emb"] = embed(kb["records"], get_model(model_name))  # Stage 3
                    kb["index"] = build_index(kb["emb"])                     # Stage 4
                kb["size"], kb["overlap"] = size, overlap
                st.success(f"완료 · 문서 {len(kb['docs'])} · 청크 {len(kb['records'])}")
        except NotImplementedError as e:
            st.warning(f"✏️ 구현이 필요합니다 → {e}")
        except Exception as e:  # noqa: BLE001
            st.error(f"오류: {e}")

    if st.button("🗑️ 상태 초기화", use_container_width=True,
                 help="적재/청크/임베딩/인덱스 등 누적 결과를 모두 비웁니다"):
        kb.clear()
        st.success("초기화 완료")

    if not _get_api_key():
        st.info("GEMINI_API_KEY 미설정 — Gemini 키 없으면 로컬 Ollama 로 생성(가능 시)")

tabs = st.tabs(["1.적재/파싱", "2.청킹", "3.임베딩", "4.저장",
                "5.검색", "6.생성", "7.챗봇", "8.평가/검수"])

# --- Stage 1~4: 각 탭에서 '이 단계 실행' 으로 산출물을 만들고 바로 확인 ---
with tabs[0]:
    run_step("① 이 단계 실행 · 적재/파싱", "docs",
             lambda: load_documents(files, include_folder))
    gated_render("docs", "⬆️ **이 단계 실행** 을 눌러 문서를 적재하세요.",
                 stage1_load_lab.render, kb)

with tabs[1]:
    run_step("② 이 단계 실행 · 청킹", "records",
             lambda: make_chunks(kb["docs"], size, overlap),
             need_key="docs", need_msg="먼저 Stage 1(적재/파싱)을 실행하세요.")
    gated_render("records", "⬆️ **이 단계 실행** 을 눌러 청킹하세요. (Stage 1 먼저)",
                 stage2_chunk_lab.render, kb)

with tabs[2]:
    def _embed():
        kb["model_name"] = model_name           # 검색 단계가 같은 모델을 쓰도록 기록
        return embed(kb["records"], get_model(model_name))
    run_step("③ 이 단계 실행 · 임베딩", "emb", _embed,
             need_key="records", need_msg="먼저 Stage 2(청킹)를 실행하세요.")
    gated_render("emb", "⬆️ **이 단계 실행** 을 눌러 임베딩하세요. (Stage 2 먼저)",
                 stage3_embed_lab.render, kb)

with tabs[3]:
    run_step("④ 이 단계 실행 · 저장(인덱싱)", "index",
             lambda: build_index(kb["emb"]),
             need_key="emb", need_msg="먼저 Stage 3(임베딩)을 실행하세요.")
    gated_render("index", "⬆️ **이 단계 실행** 을 눌러 인덱스를 만드세요. (Stage 3 먼저)",
                 stage4_store_lab.render, kb)

# --- Stage 5~8: 인덱스가 준비되면 각 탭에서 대화형으로 실행(검색어 입력·채점 버튼 등) ---
_NEED_INDEX = "먼저 Stage 1~4 를 실행해 인덱스를 만든 뒤 사용하세요."
with tabs[4]: gated_render("index", _NEED_INDEX, stage5_search_lab.render, kb, k)
with tabs[5]: gated_render("index", _NEED_INDEX, stage6_generate_lab.render, kb, k)
with tabs[6]: gated_render("index", _NEED_INDEX, stage7_chat_lab.render, kb, k)
with tabs[7]: gated_render("index", _NEED_INDEX, stage8_eval_lab.render, kb, k)
