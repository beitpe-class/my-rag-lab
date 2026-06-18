"""[실습] Stage 8 · 평가/검수 — 정답 아는 질문으로 RAG 품질을 측정한다.
LLM 제공자(Gemini/Ollama) 선택 코드는 제공되며, run_eval(채점 루프)을 직접 구현한다."""
import pandas as pd
import streamlit as st

from stages.stage5_search_lab import retrieve
from stages.stage6_generate_lab import build_prompt, generate, llm_controls

EVAL_COLS = ["id", "question", "expected_answer", "expected_source", "trap"]


def _is_trap(v):
    """[제공] 함정 여부 판별('1','true','y','yes' → True)."""
    return str(v).strip().lower() in ("1", "true", "y", "yes")


def run_eval(test_df, k, provider="auto", model=None):
    """[목표] 테스트표의 각 질문을 검색+생성(선택한 LLM)하고 자동 채점한다.
    출력: pd.DataFrame — 질문별 결과(actual_answer, retrieved_sources, source_hit, refused, verdict ...)

    [제공] provider, model 은 화면에서 고른 LLM(아래 render 참고)이 넘어온다.
           생성할 때 generate(prompt, ctx, provider, model) 처럼 넘기면 Gemini/Ollama 모두 동작.

    [구현 단계] test_df 의 각 행 r 에 대해:
      1) q = 질문. 비었으면 건너뜀
      2) hits = retrieve(q, k);  srcs = 검색된 출처 집합
      3) prompt, ctx = build_prompt(q, hits)
         ans = generate(prompt, ctx, provider, model)      # ← 선택한 LLM 사용
      4) refused = ("찾을 수 없습니다" in ans)
      5) exp_src = 기대 출처, trap = _is_trap(r["trap"])
      6) source_hit = (exp_src in srcs) if exp_src else None
      7) verdict = "정답" if (trap and refused) else ("오답" if (trap and not refused) else "미검수")
      8) 위 값들을 dict 로 rows 에 append → pd.DataFrame(rows) 반환

    [예제] 한 행 처리:
        hits = retrieve(q, k)
        srcs = sorted({h["source"] for h in hits})
        ans = generate(*build_prompt(q, hits), provider, model)
        refused = "찾을 수 없습니다" in ans
    """
    rows = []
    # ✏️ TODO: 각 질문을 검색·생성(provider/model)·채점해 rows 를 채우고 DataFrame 으로 반환하세요.
    raise NotImplementedError("run_eval 을 구현하세요 (Stage 8)")


def eval_metrics(df):
    """[제공] 채점표에서 지표 4종 계산: (정답률, 출처적중률, 환각률, 평균 top유사도)."""
    judged = df[df["verdict"].isin(["정답", "부분", "오답"])]
    acc = ((df["verdict"] == "정답").sum() + 0.5 * (df["verdict"] == "부분").sum())
    acc = acc / len(judged) if len(judged) else None
    nontrap = df[~df["trap"]]
    srcrows = nontrap[nontrap["source_hit"].notna()]
    src_rate = srcrows["source_hit"].mean() if len(srcrows) else None
    traps = df[df["trap"]]
    halluc = (~traps["refused"]).mean() if len(traps) else None
    top = df["top_score"].dropna().mean() if df["top_score"].notna().any() else None
    return acc, src_rate, halluc, top


def render(kb, k):
    """[제공] '8.평가/검수' 탭 — 제공자 선택 + 테스트표 → 채점 → 지표.
    (run_eval 이 완성되면 '전체 실행 & 채점' 이 동작합니다.)"""
    st.subheader("Stage 8 · Q&A 테스트표 & 결과 검수  ✏️실습")
    if not kb:
        st.info("먼저 사이드바에서 **파이프라인 실행**으로 인덱스를 만드세요.")
        return

    # [제공] 채점에 쓸 LLM 선택 (Gemini / 로컬 Ollama)
    provider, model = llm_controls("lab8_")
    st.caption("선택한 LLM 으로 모든 질문을 채점합니다. 로컬 모델은 문항 수만큼 시간이 걸립니다.")

    cset1, cset2 = st.columns(2)
    if cset1.button("📋 샘플 테스트표 불러오기", width='stretch'):
        try:
            st.session_state.lab_test_df = pd.read_csv("eval_questions.csv")
        except Exception:  # noqa: BLE001
            st.session_state.lab_test_df = pd.DataFrame(columns=EVAL_COLS)
    up = cset2.file_uploader("또는 테스트표 CSV 업로드", type=["csv"], key="lab_eval_csv")
    if up is not None:
        st.session_state.lab_test_df = pd.read_csv(up)
    st.session_state.setdefault(
        "lab_test_df", pd.DataFrame([{"id": 1, "question": "", "expected_answer": "",
                                      "expected_source": "", "trap": 0}]))
    st.markdown("**① 테스트표 작성/수정**")
    test_df = st.data_editor(st.session_state.lab_test_df, num_rows="dynamic",
                             width='stretch', height=240, key="lab_test_editor")
    if st.button("▶ 전체 실행 & 채점", width='stretch'):
        with st.spinner(f"{provider} 로 채점 중..."):
            st.session_state.lab_eval_res = run_eval(test_df, k, provider, model)
    if "lab_eval_res" in st.session_state:
        res = st.session_state.lab_eval_res
        if res.empty:
            st.warning("채점할 질문이 없습니다 — 테스트표에 질문을 입력하세요.")
            return
        st.markdown("**② 결과 검수** — verdict 를 정답/부분/오답으로 판정")
        edited = st.data_editor(res, width='stretch', height=320, key="lab_eval_review")
        acc, src_rate, halluc, top = eval_metrics(edited)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("검수 정답률", f"{acc*100:.0f}%" if acc is not None else "-")
        m2.metric("출처 적중률", f"{src_rate*100:.0f}%" if src_rate is not None else "-")
        m3.metric("환각률", f"{halluc*100:.0f}%" if halluc is not None else "-")
        m4.metric("평균 top 유사도", f"{top:.2f}" if top is not None else "-")
