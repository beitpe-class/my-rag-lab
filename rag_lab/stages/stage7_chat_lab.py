"""[실습] Stage 7 · 챗봇 — 단발 질의를 멀티턴 대화로 확장한다.
LLM 제공자(Gemini/Ollama) 선택 코드는 제공되며, '대화 루프'를 직접 구현한다."""
import streamlit as st

from stages.stage5_search_lab import retrieve
from stages.stage6_generate_lab import build_prompt, generate, llm_controls


def render(kb, k):
    """[목표] 대화형 챗봇: 입력 → 검색 → 생성(선택한 LLM) → 말풍선 + 대화 기록.

    [제공] 아래 llm_controls 로 provider/model 을 고르는 '기본 코드'는 이미 들어있다.
           생성할 때 generate(prompt, ctx, provider, model) 처럼 넘겨 쓰면
           Gemini 든 로컬 Ollama 든 그대로 동작한다.

    [구현 단계] (TODO)
      1) st.session_state.setdefault("lab_msgs", []) 로 대화 기록 준비
      2) 기존 기록 다시 그림: for m in lab_msgs: st.chat_message(m["role"]).write(m["content"])
      3) if q := st.chat_input("질문하세요"):
           - st.chat_message("user").write(q)
           - hits = retrieve(q, k)
           - prompt, ctx = build_prompt(q, hits)
           - ans = generate(prompt, ctx, provider, model)      # ← 선택한 LLM 사용
           - st.chat_message("assistant").write(ans)
           - lab_msgs 에 user / assistant 메시지를 append

    [예제]
        if q := st.chat_input("문서 내용을 질문하세요"):
            st.chat_message("user").write(q)
            hits = retrieve(q, k)
            ans = generate(*build_prompt(q, hits), provider, model)
            st.chat_message("assistant").write(ans)

    [확장 아이디어] 대화 초기화 버튼 / 이전 맥락 반영 후속 질문 재검색 / 👍👎 평가.
    """
    st.subheader("Stage 7 · 챗봇  ✏️실습")
    if not kb:
        st.info("← 먼저 파이프라인을 실행하세요.")
        return

    # [제공] LLM 제공자 선택 (Gemini / 로컬 Ollama) — generate 에 그대로 넘기면 됨
    provider, model = llm_controls("lab_chat_")

    # ✏️ TODO: 위 provider, model 을 generate 에 넘기는 멀티턴 대화 루프를 구현하세요.
    raise NotImplementedError("Stage 7 챗봇 대화 루프를 구현하세요 (provider, model 을 generate 에 전달)")
