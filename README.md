# RAG 파이프라인 실습 (학생 배포본)

8단계 RAG 파이프라인을 직접 구현하며 눈으로 확인하는 실습입니다.

## 폴더 구성

| 항목 | 내용 | 접근 |
|------|------|------|
| `rag_lab/` | 실습 워크북 — `stages/*_lab.py` 의 ✏️TODO 를 채웁니다 | 🟢 공개 |
| `rag_answer.zip` | 각 TODO의 **정답(기본 동작 코드)** | 🔒 비밀번호 |
| `rag_solution.zip` | 확장 과제 **모범답안** | 🔒 비밀번호 |

> 정답/모범답안 zip의 비밀번호는 **강사 안내**에 따라 받으세요.

## 시작하기 (rag_lab)

```bash
cd rag_lab
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app_lab.py
```

브라우저가 열리면 사이드바에서 문서를 넣고 **▶ 파이프라인 실행**.
각 탭(1.적재 … 8.평가)은 해당 `stages/stageN_*_lab.py` 의 TODO를 채우면 결과가 나타납니다.
아직 구현 전 단계는 "✏️ 구현이 필요합니다" 안내만 뜨고 앱은 죽지 않습니다.

### 구현 순서 (의존성)
1. `stage1_load_lab.py` — `read_pdf`, `load_documents`
2. `stage2_chunk_lab.py` — `make_chunks`
3. `stage3_embed_lab.py` — `get_model`, `embed`
4. `stage4_store_lab.py` — `build_index`
5. `stage5_search_lab.py` — `retrieve`
6. `stage6_generate_lab.py` — `build_prompt`, `generate`
7. `stage7_chat_lab.py` / 8. `stage8_eval_lab.py`

### LLM 키 (선택)

`rag_lab/.streamlit/secrets.toml.example` 를 같은 폴더의 `secrets.toml` 로 복사하고 키를 채웁니다.
생성 단계는 **Claude → Gemini → 로컬 Ollama** 순으로 자동 선택합니다.

| 키 | 발급처 | 모델 |
|---|---|---|
| `CLAUDE_API_KEY` | console.anthropic.com | `claude-haiku-4-5` |
| `GEMINI_API_KEY` | ai.google.dev | `gemini-2.5-flash` |

둘 다 없으면 로컬 Ollama(`ollama serve` + `ollama pull qwen2.5:14b`)를 쓰고,
그마저 없으면 검색 근거만 표시되므로 1~5단계 실습은 그대로 진행됩니다.
6.생성 탭의 **LLM 제공자** 라디오에서 직접 고를 수도 있습니다.

### 평가용 테스트표

8.평가/검수 탭의 드롭다운에서 고릅니다.

| 선택 | 내용 |
|---|---|
| 부대 행정 | `eval_questions.csv` — 규정·수치 위주 10문항(함정 2) |
| 소설 「운수 좋은 날」 | `eval_questions_novel.csv` — 인물·줄거리 10문항(함정 2) |
| 통합 (행정 + 소설) | 20문항. 성격별로 나눈 **구분별 지표**가 함께 표시됩니다 |

## 정답 / 모범답안 열기 (강사용)

```bash
unzip -P <비밀번호> rag_answer.zip      # → rag_answer/   (cd rag_answer && streamlit run app.py)
unzip -P <비밀번호> rag_solution.zip    # → rag_solution/ (cd rag_solution && streamlit run app_solution.py)
```
