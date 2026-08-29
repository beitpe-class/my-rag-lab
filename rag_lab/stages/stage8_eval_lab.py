"""[실습] Stage 8 · 평가/검수 — 정답 아는 질문으로 RAG 품질을 측정한다.
LLM 제공자(Claude/Gemini/Ollama) 선택과 샘플 테스트표 로딩은 제공되며,
run_eval(채점 루프)을 직접 구현한다.
샘플 테스트표는 '부대 행정' · '소설 「운수 좋은 날」' · '통합' 중에서 고른다."""
import pandas as pd
import streamlit as st

from stages.stage5_search_lab import retrieve
from stages.stage6_generate_lab import build_prompt, generate, llm_controls

EVAL_COLS = ["id", "question", "expected_answer", "expected_source", "trap", "category"]

# 샘플 CSV → 구분 라벨. 성격이 다른 질문을 섞어 채점할 때 지표를 나눠 보기 위한 값.
CATEGORY_OF = {
    "eval_questions.csv": "행정",
    "eval_questions_novel.csv": "소설",
}


SAMPLE_SETS = {
    "부대 행정": ["eval_questions.csv"],
    "소설 「운수 좋은 날」": ["eval_questions_novel.csv"],
    "통합 (행정 + 소설)": ["eval_questions.csv", "eval_questions_novel.csv"],
}


def load_sample(name):
    """[제공] 샘플 테스트표를 불러온다. '통합'이면 두 CSV 를 이어 붙이고 id 를 1부터 다시 매긴다.
    (엑셀이 붙이는 BOM 때문에 encoding='utf-8-sig' 로 읽어야 열 이름이 어긋나지 않는다.)"""
    frames = []
    for path in SAMPLE_SETS.get(name, []):
        try:
            df = pd.read_csv(path, encoding="utf-8-sig")
        except Exception:  # noqa: BLE001  (파일이 없으면 건너뜀)
            continue
        df["category"] = CATEGORY_OF.get(path, "기타")   # 어느 세트에서 왔는지 표시
        frames.append(df)
    if not frames:
        return pd.DataFrame(columns=EVAL_COLS)
    df = pd.concat(frames, ignore_index=True)
    df["id"] = range(1, len(df) + 1)
    return df[[c for c in EVAL_COLS if c in df.columns]]


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
      8) 구분 표시: category = str(r.get("category", "") or "").strip() or "전체"
         (행정/소설처럼 성격이 다른 질문을 나눠서 채점 결과를 보기 위한 열)
      9) 위 값들을 dict 로 rows 에 append → pd.DataFrame(rows) 반환

    [예제] 한 행 처리:
        hits = retrieve(q, k)
        srcs = sorted({h["source"] for h in hits})
        ans = generate(*build_prompt(q, hits), provider, model)
        refused = "찾을 수 없습니다" in ans
        category = str(r.get("category", "") or "").strip() or "전체"
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


def eval_metrics_by_category(df):
    """[제공] 구분(category)별 지표 표를 만든다. 구분 열이 없거나 한 종류뿐이면 None.
    성격이 다른 질문(행정/소설)을 한 표로 합쳐 채점하면 전체 평균이 차이를 가려버린다."""
    if "category" not in df.columns:
        return None
    cats = [c for c in df["category"].dropna().unique() if str(c).strip()]
    if len(cats) < 2:
        return None

    def pct(v):
        return "-" if v is None else f"{v*100:.0f}%"

    rows = []
    for cat in cats:
        g = df[df["category"] == cat]
        acc, src_rate, halluc, top = eval_metrics(g)
        rows.append({"구분": cat, "문항": len(g), "함정": int(g["trap"].sum()),
                     "검수 정답률": pct(acc), "출처 적중률": pct(src_rate),
                     "환각률": pct(halluc),
                     "평균 top 유사도": "-" if top is None else f"{top:.2f}"})
    return pd.DataFrame(rows)


def render(kb, k):
    """[제공] '8.평가/검수' 탭 — 제공자 선택 + 테스트표 → 채점 → 지표.
    (run_eval 이 완성되면 '전체 실행 & 채점' 이 동작합니다.)"""
    st.subheader("Stage 8 · Q&A 테스트표 & 결과 검수  ✏️실습")
    if not kb:
        st.info("먼저 사이드바에서 **파이프라인 실행**으로 인덱스를 만드세요.")
        return

    # [제공] 채점에 쓸 LLM 선택 (Claude / Gemini / 로컬 Ollama)
    provider, model = llm_controls("lab8_")
    st.caption("선택한 LLM 으로 모든 질문을 채점합니다. 로컬 모델은 문항 수만큼 시간이 걸립니다.")

    cset1, cset2 = st.columns(2)
    sample = cset1.selectbox("샘플 테스트표", list(SAMPLE_SETS), key="lab_eval_sample")
    if cset1.button("📋 샘플 테스트표 불러오기", width='stretch'):
        st.session_state.lab_test_df = load_sample(sample)
    up = cset2.file_uploader("또는 테스트표 CSV 업로드", type=["csv"], key="lab_eval_csv")
    if up is not None:
        st.session_state.lab_test_df = pd.read_csv(up)
    st.session_state.setdefault(
        "lab_test_df", pd.DataFrame([{"id": 1, "question": "", "expected_answer": "",
                                      "expected_source": "", "trap": 0,
                                      "category": ""}]))
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
        by_cat = eval_metrics_by_category(edited)
        if by_cat is not None:
            st.markdown("**③ 구분별 지표** — 성격이 다른 질문은 나눠 봐야 차이가 보입니다")
            st.dataframe(by_cat, width='stretch', hide_index=True)
