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

(생성 단계는 `GEMINI_API_KEY` 가 있으면 Gemini, 없으면 로컬 Ollama 사용)

## 정답 / 모범답안 열기 (강사용)

```bash
unzip -P <비밀번호> rag_answer.zip      # → rag_answer/   (cd rag_answer && streamlit run app.py)
unzip -P <비밀번호> rag_solution.zip    # → rag_solution/ (cd rag_solution && streamlit run app_solution.py)
```
