"""[실습] Stage 6 · 생성 — 검색 근거로 LLM이 '근거 기반' 답을 만든다.
LLM은 Gemini(클라우드) 또는 로컬 Ollama 를 쓸 수 있다.
(generate/_get_api_key/_gen_ollama 는 base 와 동일 로직 — lab 은 자체 완결로 복제)"""
import json
import os
import urllib.error
import urllib.request

import streamlit as st

from stages.stage5_search_lab import retrieve

try:
    import google.generativeai as genai
    _HAS_GENAI = True
except ImportError:
    _HAS_GENAI = False

GEN_MODEL = "gemini-2.5-flash"
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:14b"
_KEY_PLACEHOLDER = "여기에"


def _get_api_key():
    """GEMINI_API_KEY 안전 조회: secrets 없으면 환경변수, 비었거나 예시 placeholder면 키 없음."""
    key = ""
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:  # noqa: BLE001
        key = ""
    if not key:
        key = os.environ.get("GEMINI_API_KEY", "")
    if not key or key.startswith(_KEY_PLACEHOLDER):
        return ""
    return key


def _ollama_models():
    """[제공] 로컬 Ollama 에 설치된 모델 목록(연결 안 되면 빈 리스트)."""
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2) as resp:
            return [m["name"] for m in json.loads(resp.read()).get("models", [])]
    except Exception:  # noqa: BLE001
        return []


def _gen_ollama(prompt, model, temperature=0.2):
    """[제공] 로컬 Ollama 서버로 생성. API 키 불필요."""
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False,
                          "options": {"temperature": temperature}}).encode("utf-8")
    req = urllib.request.Request(f"{OLLAMA_URL}/api/generate", data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read()).get("response", "").strip()


def build_prompt(query, hits):
    """[목표] 검색된 근거(hits)와 질문으로 LLM 프롬프트를 만든다. (RAG 핵심!)
    출력: (prompt:str, context:str)

    [구현 단계]
      1) context = 각 hit 를 "[출처#번호] 본문" 형식으로 "\n\n" join
      2) prompt = "아래 [컨텍스트]만 근거로 한국어로 간결하게 답하라.
         컨텍스트에 없으면 '문서에서 찾을 수 없습니다'라고만 답하라." + 컨텍스트/질문/답변 섹션
      3) (prompt, context) 반환

    [예제]
        context = "\n\n".join(f"[{h['source']}#{h['chunk_id']}] {h['text']}" for h in hits)
        prompt = ("아래 [컨텍스트]만 근거로 한국어로 간결하게 답하라. "
                  "컨텍스트에 없으면 '문서에서 찾을 수 없습니다'라고만 답하라.\n\n"
                  f"[컨텍스트]\n{context}\n\n[질문]\n{query}\n\n[답변]")
    """
    # ✏️ TODO: 컨텍스트 + 지시문으로 prompt 를 만들고 (prompt, context) 반환.
    raise NotImplementedError("build_prompt 를 구현하세요 (Stage 6)")


def generate(prompt, context, provider="auto", model=None, temperature=0.2):
    """[제공] provider='auto' → 키 있으면 Gemini, 없으면 로컬 Ollama.
    ('gemini' / 'ollama' 직접 지정 가능. model 로 모델명 변경)"""
    key = _get_api_key()
    if provider == "auto":
        provider = "gemini" if (_HAS_GENAI and key) else "ollama"
    try:
        if provider == "ollama":
            return _gen_ollama(prompt, model or OLLAMA_MODEL, temperature)
        if not (_HAS_GENAI and key):
            return "_(LLM 키 없음 — 검색 근거만 표시)_\n\n" + context
        genai.configure(api_key=key)
        cfg = genai.types.GenerationConfig(temperature=temperature)
        return genai.GenerativeModel(model or GEN_MODEL).generate_content(
            prompt, generation_config=cfg).text.strip()
    except urllib.error.HTTPError as e:
        return (f"_(Ollama 응답 오류 {e.code} — `ollama pull {model or OLLAMA_MODEL}`)_\n\n" + context)
    except urllib.error.URLError:
        return ("_(Ollama 서버 연결 실패 — `ollama serve` 실행)_\n\n" + context)
    except Exception as e:  # noqa: BLE001
        return f"생성 오류: {e}"


def llm_controls(prefix=""):
    """[제공] Gemini/Ollama 선택 위젯 → (provider, model) 반환.
    generate(prompt, ctx, provider, model) 에 그대로 넘겨 쓰면 된다."""
    label = st.radio("LLM 제공자", ["자동", "Gemini(클라우드)", "Ollama(로컬)"],
                     horizontal=True, key=f"{prefix}prov")
    provider = {"자동": "auto", "Gemini(클라우드)": "gemini", "Ollama(로컬)": "ollama"}[label]
    model = None
    if provider == "ollama":
        models = _ollama_models()
        if models:
            model = st.selectbox("Ollama 모델", models, key=f"{prefix}model")
        else:
            model = st.text_input("Ollama 모델", OLLAMA_MODEL, key=f"{prefix}model_t")
            st.caption("⚠️ Ollama 미연결 — `ollama serve` 후 `ollama pull` 필요")
    return provider, model


def render(kb, k):
    """[제공] '6.생성' 탭 — 제공자 선택 + 질문 → 답변·출처·프롬프트."""
    st.subheader("Stage 6 · 생성  ✏️실습")
    if not kb:
        return
    provider, model = llm_controls("lab6_")
    gq = st.text_input("질문 → 검색 근거로 LLM이 답합니다", key="lab_gen_q")
    if gq:
        hits = retrieve(gq, k)
        prompt, context = build_prompt(gq, hits)
        ans = generate(prompt, context, provider, model)
        st.markdown("**답변**"); st.write(ans)
        st.markdown("**출처:** " + ", ".join(sorted({h["source"] for h in hits})))
        with st.expander("LLM에 전달된 프롬프트 보기"):
            st.text(prompt)
