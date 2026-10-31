"""[실습] Stage 6 · 생성 — 검색 근거로 LLM이 '근거 기반' 답을 만든다.
LLM은 Claude·Gemini(클라우드) 또는 로컬 Ollama 를 쓸 수 있다.
(generate/_get_api_key/_get_claude_key/_gen_claude/_gen_ollama 는 base 와 동일 로직
 — lab 은 자체 완결로 복제)"""
import json
import os
import urllib.error
import urllib.request

import streamlit as st

from stages.stage5_search_lab import retrieve

try:
    from google import genai              # google-genai (신 SDK) — 구 google-generativeai 아님
    _HAS_GENAI = True
except ImportError:
    _HAS_GENAI = False

try:
    import anthropic
    _HAS_ANTHROPIC = True
except ImportError:
    _HAS_ANTHROPIC = False

# anthropic 미설치 시 except 절에서 아무것도 매칭하지 않는 빈 튜플
_ANTHROPIC_ERRORS = (anthropic.AnthropicError,) if _HAS_ANTHROPIC else ()

GEN_MODEL = "gemini-3.6-flash"      # 2.5-flash 는 신규 사용 중단(404)
CLAUDE_MODEL = "claude-haiku-4-5"
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:14b"
_KEY_PLACEHOLDER = "여기에"   # secrets.toml.example 의 예시 키 접두사


def _read_key(*names):
    """secrets.toml → 환경변수 순으로 첫 번째로 찾은 키를 돌려준다.
    - secrets.toml 이 아예 없으면(StreamlitSecretNotFoundError) 환경변수로 폴백
    - 비어있거나 예시 placeholder('여기에...')면 '키 없음'(빈 문자열)으로 취급
    """
    for name in names:
        key = ""
        try:
            key = st.secrets.get(name, "")
        except Exception:  # noqa: BLE001  (secrets 파일 자체가 없을 때)
            key = ""
        if not key:
            key = os.environ.get(name, "")
        if key and not key.startswith(_KEY_PLACEHOLDER):
            return key
    return ""


def _get_api_key():
    """GEMINI_API_KEY 조회."""
    return _read_key("GEMINI_API_KEY")


def _get_claude_key():
    """CLAUDE_API_KEY 조회(없으면 표준 이름인 ANTHROPIC_API_KEY 로 폴백)."""
    return _read_key("CLAUDE_API_KEY", "ANTHROPIC_API_KEY")


def active_provider():
    """provider='auto' 일 때 실제로 쓰이는 생성기: Claude → Gemini → Ollama."""
    if _HAS_ANTHROPIC and _get_claude_key():
        return "claude"
    if _HAS_GENAI and _get_api_key():
        return "gemini"
    return "ollama"


def _ollama_models():
    """[제공] 로컬 Ollama 에 설치된 모델 목록(연결 안 되면 빈 리스트)."""
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2) as resp:
            return [m["name"] for m in json.loads(resp.read()).get("models", [])]
    except Exception:  # noqa: BLE001
        return []


def _gen_claude(prompt, model, max_tokens=1024):
    """[제공] Claude(Anthropic)로 생성.
    anthropic SDK 1.x 부터 temperature 등 샘플링 파라미터는 제거됨 → 프롬프트로 제어.
    조직/워크스페이스 연동 키는 ANTHROPIC_WORKSPACE_ID 도 필요(개인 키는 불필요).
    """
    ws = _read_key("ANTHROPIC_WORKSPACE_ID")
    client = anthropic.Anthropic(
        api_key=_get_claude_key(),
        default_headers={"anthropic-workspace-id": ws} if ws else None,
    )
    resp = client.messages.create(
        model=model or CLAUDE_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    # content 는 블록 리스트 — 텍스트 블록만 이어붙인다
    return "".join(b.text for b in resp.content if b.type == "text").strip()


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
    """[제공] provider='auto' → Claude 키 있으면 Claude, 없고 Gemini 키 있으면 Gemini,
    둘 다 없으면 로컬 Ollama. ('claude'/'gemini'/'ollama' 직접 지정 가능, model 로 모델명 변경)
    ※ temperature 는 Gemini/Ollama 전용 — Claude 는 SDK 1.x 에서 미지원."""
    if provider == "auto":
        provider = active_provider()
    try:
        if provider == "claude":
            if not _HAS_ANTHROPIC:
                return "_(anthropic 미설치 — `pipenv install anthropic`)_\n\n" + context
            if not _get_claude_key():
                return "_(CLAUDE_API_KEY 미설정 — 검색 근거만 표시)_\n\n" + context
            return _gen_claude(prompt, model)
        if provider == "ollama":
            return _gen_ollama(prompt, model or OLLAMA_MODEL, temperature)
        if not (_HAS_GENAI and _get_api_key()):
            return "_(LLM 키 없음 — 검색 근거만 표시)_\n\n" + context
        client = genai.Client(api_key=_get_api_key())
        cfg = genai.types.GenerateContentConfig(temperature=temperature)
        resp = client.models.generate_content(
            model=model or GEN_MODEL, contents=prompt, config=cfg)
        return (resp.text or "").strip()
    except _ANTHROPIC_ERRORS as e:                 # 인증 실패·한도 초과·요청 오류 등
        return f"_(Claude 호출 실패 · {e.__class__.__name__}: {e})_\n\n" + context
    except urllib.error.HTTPError as e:           # 서버는 떴는데 응답 오류(예: 모델 미설치 404)
        return (f"_(Ollama 응답 오류 {e.code} — 모델을 받았는지 확인하세요: "
                f"`ollama pull {model or OLLAMA_MODEL}`)_\n\n" + context)
    except urllib.error.URLError:                 # 서버 연결 자체 실패
        return ("_(Ollama 서버 연결 실패 — 터미널에서 `ollama serve` 실행)_\n\n" + context)
    except Exception as e:  # noqa: BLE001
        return f"생성 오류: {e}"


def llm_controls(prefix=""):
    """[제공] Claude/Gemini/Ollama 제공자·모델 선택 위젯 → (provider, model) 반환.
    Ollama 선택 시 설치된 모델을 드롭다운으로 표시(미연결이면 입력 + 안내).
    Stage 6·7·8 공용 — generate(prompt, ctx, provider, model) 에 그대로 넘겨 쓰면 된다."""
    labels = {"자동": "auto", "Claude(클라우드)": "claude",
              "Gemini(클라우드)": "gemini", "Ollama(로컬)": "ollama"}
    label = st.radio("LLM 제공자", list(labels), horizontal=True, key=f"{prefix}provider")
    provider = labels[label]
    model = None
    if provider == "ollama":
        models = _ollama_models()
        if models:
            model = st.selectbox("Ollama 모델", models, key=f"{prefix}model_o")
        else:
            model = st.text_input("Ollama 모델", OLLAMA_MODEL, key=f"{prefix}model_ot")
            st.caption("⚠️ Ollama 미연결 — `ollama serve` 후 `ollama pull` 필요")
    elif provider == "claude" and not (_HAS_ANTHROPIC and _get_claude_key()):
        st.caption("⚠️ Claude 사용 불가 — `pipenv install anthropic` + CLAUDE_API_KEY 설정 필요")
    elif provider == "gemini" and not (_HAS_GENAI and _get_api_key()):
        st.caption("⚠️ Gemini 사용 불가 — `pipenv install google-genai` + GEMINI_API_KEY 설정 필요")
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
