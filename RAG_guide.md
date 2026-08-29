# RAG 단계별 실습 가이드 (120분)

**AI VIBE CODING WORKSHOP · RAG**

파이프라인을 눈으로 보며 만드는 문서 챗봇

적재/파싱 → 청킹 → 임베딩 → 저장 → 검색 → 생성 → 챗봇 → 평가. 각 단계의 ‘중간 데이터’를 UI 탭(또는 노트북 셀)에서 직접 확인하며, 제공된 기본 코드를 직접 이해하고 확장합니다.

> 소요 약 120분 · 난이도 초급~중급 · 준비물: 노트북 + Google(Gmail) 계정 + GitHub 계정 · 데이터: 가상·공개 문서만
>
> 이 가이드는 학생 배포판(`my-rag-lab`)의 **현재 기본 코드(`rag_lab/stages/`) 기준**으로 동기화되어 있습니다.

---

## 목차

1. 이 실습에 대하여
   - 진행 방식
   - RAG 파이프라인 8단계
2. 사전 준비 & 기본 코드 실행
   - 필요한 것 (모두 무료)
   - 패키지
   - LLM 키 (선택)
   - 탭 UI 투어
   - 이번 실습용 빈 레포 & 폴더 준비
3. Stage 1 · 적재 / 파싱
4. Stage 2 · 청킹
5. Stage 3 · 임베딩
6. Stage 4 · 저장
7. Stage 5 · 검색
8. Stage 6 · 생성
9. Stage 7 · 챗봇 구현
10. Stage 8 · Q&A 테스트표 작성 및 결과 검수
11. 확장 과제 모음
12. 완료 체크리스트 & 트러블슈팅
13. 부록 · 기본 코드 구조

---

## 이 실습에 대하여

RAG(Retrieval-Augmented Generation)는 LLM이 답하기 전에 우리 문서를 검색해 그 내용을 근거로 답하게 만드는 기법입니다. 이 실습은 RAG 파이프라인을 8단계로 쪼개, 각 단계의 결과를 화면 탭에서 직접 보면서 만듭니다. ‘무엇이 어떻게 변환되는지’를 눈으로 확인하므로 개념이 빠르게 잡힙니다.

### 진행 방식

- **기본 코드 제공** — 8단계가 모두 연결된 탭형 모니터링 앱(`app_lab.py`)을 먼저 실행합니다.
- **단계별 확인** — 각 탭에서 적재 텍스트·청크·임베딩(PCA)·인덱스·검색 결과·생성·대화·평가를 관찰합니다.
- **직접 구현·확장** — 각 단계의 ‘확장 과제’를 직접 구현하며 동작 원리를 익힙니다.

### RAG 파이프라인 8단계

| 단계        | 변환                        | 이번 실습 도구                       |
| ----------- | --------------------------- | ------------------------------------ |
| 1 적재/파싱 | 파일 → 순수 텍스트          | pypdf / 파일 읽기                    |
| 2 청킹      | 긴 텍스트 → 조각(메타 포함) | 분할 함수                            |
| 3 임베딩    | 조각 → 의미 벡터            | sentence-transformers                |
| 4 저장      | 벡터 → 인덱스               | FAISS                                |
| 5 검색      | 질문 → top-k 조각           | FAISS 검색                           |
| 6 생성      | 근거 → 답변                 | **Claude · Gemini API 또는 로컬 Ollama** |
| 7 챗봇      | 단발 → 멀티턴 대화          | Streamlit chat                       |
| 8 평가/검수 | 답변 → 정량 지표            | 테스트표 채점                        |

---

## 사전 준비 & 기본 코드 실행

### 필요한 것 (모두 무료)

| 항목                      | 용도                             | 비고                        |
| ------------------------- | -------------------------------- | --------------------------- |
| Google(Gmail) 계정        | Antigravity 로그인 + Gemini 사용 | 개인 Gmail 기준 무료 프리뷰 |
| Anthropic 계정            | Claude API 키 발급 (선택)        | console.anthropic.com · 종량제 |
| GitHub 계정               | 코드 저장 + 배포 연동            | Lab 4 배포에 필요           |
| Streamlit Community Cloud | 앱 무료 호스팅                   | GitHub 계정으로 로그인      |
| Visual Studio Code        | 코드 편집기(IDE)                 | 무료 · AI 코딩 확장 지원    |
| pip (+ venv)              | 파이썬 가상환경·패키지 관리      | Python 설치 시 기본 포함    |
| Ollama                    | 로컬 LLM 실행                    | 무료 · 오프라인(선택)       |

### 패키지

```bash
# rag_lab/requirements.txt
streamlit>=1.31
sentence-transformers>=2.6
torch>=2.2              # 임베딩 백엔드(CPU 휠) — 명시적 고정
torchvision>=0.17       # transformers 이미지 모델 import 로그 노이즈 제거용
faiss-cpu>=1.8
google-generativeai>=0.7
pypdf>=4.2
pandas>=2.0
python-docx>=1.1        # Stage 1 확장(.docx 적재)
matplotlib>=3.8         # 시각화/스타일링 보조
jupyter>=1.0            # 노트북(rag_pipeline_steps.ipynb) 실행
ipykernel>=6.0          # Jupyter/VS Code 커널
```

### LLM (선택)

생성 단계는 **Claude → Gemini → 로컬 Ollama** 순으로 자동 선택합니다.

- **Claude**: console.anthropic.com 에서 키 발급 → `.streamlit/secrets.toml` 의 `CLAUDE_API_KEY` 에 저장. 모델은 `claude-haiku-4-5`.
- **Gemini**: ai.google.dev 에서 키 발급 → 같은 파일의 `GEMINI_API_KEY` 에 저장. 모델은 `gemini-2.5-flash`.
- **로컬 Ollama**: `ollama serve` 실행 + `ollama pull qwen2.5:14b`. **키가 없으면 자동으로 Ollama 를 사용**합니다.
- 키도 Ollama도 없으면 6단계까지(검색 근거 표시) 실습 가능합니다.
- 6.생성 탭의 **LLM 제공자** 라디오에서 직접 고를 수도 있습니다.

### 탭 UI 투어

기본 코드는 8개 탭(1.적재/파싱 ~ 8.평가/검수)으로 구성됩니다. 사이드바에서 문서 업로드·모델·청크·top-k를 설정하고 ‘파이프라인 실행’을 누르면, 각 탭에 해당 단계의 데이터가 채워집니다.

> **데이터 원칙 (필독)** — 무료 LLM API는 입력이 모델 학습에 사용될 수 있습니다. 실제 작전·부대 식별 정보·개인정보·기밀 문서는 절대 넣지 마세요. 가상·공개 문서만 사용합니다.

> **한국어 문서** — 기본 임베딩 모델은 영어 중심입니다. 한국어 문서는 사이드바에서 ‘다국어/한국어’ 모델을 선택하고 ’파이프라인 실행’을 다시 누르세요.

### 이번 실습용 빈 레포 & 폴더 준비

이번 RAG 실습은 전용 새 저장소에서 진행합니다. GitHub에서 레포를 클론해 두면, Stage 1에서 File ▸ Open Folder로 그 폴더만 열어 바로 시작할 수 있습니다.

**PowerShell 실행**

```powershell
# 1) 작업 폴더(C:\my-projects)를 만들고 그 아래로 이동
mkdir C:\my-projects
cd C:\my-projects

# 2) 레포를 클론하고 폴더로 이동
git clone https://github.com/beitpe-class/my-rag-lab.git
cd my-rag-lab
```

```
my-rag-app-student/
├── .gitignore
├── README.md
├── RAG_guide.md
├── rag_answer.zip              # 기본 실습 모범 코드 (암호 zip)
├── rag_solution.zip            # 고급 실습 모범 코드 (암호 zip)
└── rag_lab/                    # ← VS Code 에서 File ▸ Open Folder 로 이 폴더를 엽니다
    ├── app_lab.py              # 기본 코드: 사이드바 + st.tabs(8단계) 오케스트레이터
    ├── requirements.txt        # 패키지 목록
    ├── eval_questions.csv      # Stage 8 샘플 테스트표 · 부대 행정(함정 2문항)
    ├── eval_questions_novel.csv   # Stage 8 샘플 테스트표 · 소설(함정 2문항)
    ├── .streamlit/
    │   └── secrets.toml.example   # CLAUDE/GEMINI 키 템플릿 → secrets.toml 로 복사해 사용
    ├── docs/                   # 가상·공개 코퍼스
    │   ├── 운수좋은날_원문.txt      # 현진건 「운수 좋은 날」(1924, 저작권 만료)
    │   ├── 운수좋은날_해설.txt      # 작품 정보·등장인물·주제 정리
    │   ├── 당직근무수칙.txt
    │   ├── 데이터분석용어집.txt
    │   ├── 보급규정.txt
    │   ├── 안전수칙.txt
    │   ├── 차량운행지침.txt
    │   └── 체력검정안내.txt
    └── stages/                 # 단계별 모듈 (한 파일 = 한 단계 함수 + 탭 render)
        ├── __init__.py
        ├── stage1_load_lab.py
        ├── stage2_chunk_lab.py
        ├── stage3_embed_lab.py
        ├── stage4_store_lab.py
        ├── stage5_search_lab.py
        ├── stage6_generate_lab.py
        ├── stage7_chat_lab.py
        └── stage8_eval_lab.py
```

> **LLM 키 설정** — `rag_lab/.streamlit/secrets.toml.example` 를 같은 폴더의 `secrets.toml` 로 복사하고 `CLAUDE_API_KEY` 또는 `GEMINI_API_KEY` 를 채웁니다. 둘 다 없으면 로컬 Ollama 또는 검색 근거만으로 진행할 수 있습니다.

<aside>
💡

`rag_answer.zip`(기본)·`rag_solution.zip`(고급)은 각 단계 확장 과제를 적용한 **모범 코드**입니다. 막힐 때 비교용으로 풀어 보세요.

AI 도구로 고급 기능을 추가하려면, 바이브 코딩에서 쓰던 `AGENTS.md` / `project.md`(규칙서)를 `rag_lab/` 에 만들어 현 프로젝트에 맞게 작성하면 위임 결과가 일관됩니다.

</aside>

이렇게 레포를 준비해 두면 패키지 설치부터 Stage 1~8까지 같은 폴더(`rag_lab/`)에서 그대로 이어집니다.

---

## 환경 확인 & 패키지 설치

`rag_lab/` 폴더를 VS Code 에서 연 뒤, 터미널을 열고 **이 폴더 안에서** 아래를 진행합니다.

### 1) 도구 설치 확인

먼저 파이썬·pip 가 설치돼 있는지 버전으로 확인합니다. 버전이 출력되면 정상, `command not found` 면 미설치입니다.

```bash
python --version       # 파이썬 확인 (예: Python 3.11.x) — 안 되면 'python3 --version'
pip --version          # pip(패키지 설치 도구) 확인 — 안 되면 'python -m pip --version'
ollama --version       # (선택) 로컬 LLM — 클라우드 키 없이 Stage 6 생성 시 사용
```

> Windows 에서 `python` 이 Microsoft Store 로 연결되면, [python.org](https://www.python.org/downloads/) 에서 설치하며 **“Add python.exe to PATH”** 를 체크하세요.
>
> **Ollama 는 선택**입니다. `ollama --version` 이 안 되면 미설치이며, Claude/Gemini 키로 진행하거나 [ollama.com/download](https://ollama.com/download) 에서 설치 후 `ollama pull qwen2.5:14b` 로 모델을 받으면 키 없이 로컬 생성이 가능합니다.

### 2) 가상환경 생성 & 패키지 설치 (venv + pip)

프로젝트 전용 가상환경(`.venv`)을 만들고, 활성화한 뒤 `requirements.txt` 를 설치합니다.

```bash
# (1) 가상환경 생성 (rag_lab/ 폴더 안에서)
python -m venv .venv

# (2) 활성화 — OS에 맞게 한 줄만. 성공하면 프롬프트 앞에 (.venv) 가 붙습니다.
.venv\Scripts\activate            # Windows (PowerShell / CMD)
source .venv/bin/activate         # macOS / Linux

# (3) 패키지 설치
pip install -r requirements.txt
```

> **Windows 에서 활성화가 막히면** — PowerShell 에서 "스크립트 실행이 비활성화" 오류가 나면, 활성화 없이 venv 의 파이썬을 직접 써도 됩니다(이 방식이 가장 확실):
>
> ```powershell
> .venv\Scripts\python -m pip install -r requirements.txt
> .venv\Scripts\python -m streamlit run app_lab.py
> ```

### 3) 설치 확인 & 앱 실행

가상환경이 활성화된 상태(프롬프트에 `(.venv)`)에서 실행합니다.

```bash
streamlit --version             # 설치 확인
streamlit run app_lab.py        # 기본 코드(8단계 탭 앱) 실행 → 브라우저 자동 열림
```

> **새 터미널을 열 때마다** 가상환경을 다시 활성화하세요(위 (2)번). 활성화를 안 하면 `No module named ...` 오류가 납니다.

> 첫 실행 때 임베딩 모델을 내려받느라 시간이 걸릴 수 있습니다(이후엔 캐시되어 빨라집니다).

```
OSError: [WinError 126] 지정된 모듈을 찾을 수 없습니다. Error loading "C:\Users\TEST\.virtualenvs\rag_lab-NMvdw5PG\Lib\site-packages\torch\lib\c10.dll" or one of its dependencies.
Traceback:
File "C:\my-projects\my-rag-lab\rag_lab\app_lab.py", line 13, in <module>
    from stages.stage3_embed_lab import get_model, embed
File "C:\my-projects\my-rag-lab\rag_lab\stages\stage3_embed_lab.py", line 5, in <module>
    from sentence_transformers import SentenceTransformer
File "C:\Users\TEST\.virtualenvs\rag_lab-NMvdw5PG\Lib\site-packages\sentence_transformers\__init__.py", line 10, in <module>
    from sentence_transformers.backend import (
File "C:\Users\TEST\.virtualenvs\rag_lab-NMvdw5PG\Lib\site-packages\sentence_transformers\backend\__init__.py", line 3, in <module>
    from .load import load_onnx_model, load_openvino_model
File "C:\Users\TEST\.virtualenvs\rag_lab-NMvdw5PG\Lib\site-packages\sentence_transformers\backend\load.py", line 7, in <module>
    from transformers.configuration_utils import PretrainedConfig
File "C:\Users\TEST\.virtualenvs\rag_lab-NMvdw5PG\Lib\site-packages\transformers\configuration_utils.py", line 32, in <module>
    from .generation.configuration_utils import GenerationConfig
File "C:\Users\TEST\.virtualenvs\rag_lab-NMvdw5PG\Lib\site-packages\transformers\generation\configuration_utils.py", line 61, in <module>
    from .logits_process import SynthIDTextWatermarkLogitsProcessor, WatermarkLogitsProcessor
File "C:\Users\TEST\.virtualenvs\rag_lab-NMvdw5PG\Lib\site-packages\transformers\generation\logits_process.py", line 21, in <module>
    import torch
File "C:\Users\TEST\.virtualenvs\rag_lab-NMvdw5PG\Lib\site-packages\torch\__init__.py", line 287, in <module>
    _load_dll_libraries()
File "C:\Users\TEST\.virtualenvs\rag_lab-NMvdw5PG\Lib\site-packages\torch\__init__.py", line 283, in _load_dll_libraries
    raise err



C:\my-projects\my-rag-lab\rag_lab>python -c "import torch; print(torch.__version__)"
Microsoft Visual C++ Redistributable is not installed, this may lead to the DLL load failure.
It can be downloaded at https://aka.ms/vs/17/release/vc_redist.x64.exe
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "C:\Users\TEST\.virtualenvs\rag_lab-NMvdw5PG\Lib\site-packages\torch\__init__.py", line 287, in <module>
    _load_dll_libraries()
  File "C:\Users\TEST\.virtualenvs\rag_lab-NMvdw5PG\Lib\site-packages\torch\__init__.py", line 283, in _load_dll_libraries
    raise err
OSError: [WinError 126] 지정된 모듈을 찾을 수 없습니다. Error loading "C:\Users\TEST\.virtualenvs\rag_lab-NMvdw5PG\Lib\site-packages\torch\lib\c10.dll" or one of its dependencies.
```

#### 원인 — Visual C++ 재배포 패키지(VC++ Redistributable) 누락

로그에 직접 원인이 적혀 있습니다:

> **Microsoft Visual C++ Redistributable is not installed, this may lead to the DLL load failure.**
> It can be downloaded at https://aka.ms/vs/17/release/vc_redist.x64.exe

PyTorch(`torch`)의 핵심 파일 `c10.dll` 은 **MSVC 런타임 DLL**(C++ 재배포 패키지)에 의존합니다. 이 런타임이 없는 깨끗한 Windows PC에서는 `c10.dll` 을 불러올 때 "의존 모듈을 찾을 수 없다(`WinError 126`)"는 오류가 나며 `import torch` 자체가 실패합니다. (`torch` 가 설치돼 있어도 발생 — 설치 문제가 아니라 OS 런타임 문제입니다.)

#### 해결 절차

1. 아래 링크에서 **x64** 재배포 패키지를 내려받아 설치합니다.
   - https://aka.ms/vs/17/release/vc_redist.x64.exe
2. 설치 후 **PC를 재부팅**합니다. (DLL 경로가 시스템에 반영되려면 재시작이 안전합니다.)
3. 가상환경을 다시 활성화하고 정상 동작을 확인합니다.

```powershell
python -c "import torch; print(torch.__version__)"   # (.venv 활성화 상태) 버전이 출력되면 해결
streamlit run app_lab.py                             # 앱 재실행
```

> 64-bit Windows 기준 **x64** 버전을 설치하세요(`vc_redist.x86` 아님). 회사·교육장 PC라 관리자 권한이 없으면 IT 담당자에게 위 x64 패키지 설치를 요청하면 됩니다.

---

## Stage 1 · 적재 / 파싱

다양한 형식(PDF·TXT·MD)에서 순수 텍스트를 뽑아냅니다. PDF는 pypdf로 페이지별 텍스트를 추출합니다. 스캔(이미지) PDF는 텍스트가 없어 빈 결과가 나올 수 있으며, 이 경우 OCR이 필요합니다.

### 기본 코드 (제공)

```python
def read_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    return "\n".join((p.extract_text() or "") for p in reader.pages)

def load_documents(files, include_folder):
    docs = []
    for f in files or []:
        suffix = Path(f.name).suffix.lower()
        data = f.getvalue()
        text = read_pdf(data) if suffix == ".pdf" else data.decode("utf-8", "ignore")
        docs.append({"source": Path(f.name).stem, "text": text})
    if include_folder:
        for path in sorted(glob("docs/*")):
            docs.append({"source": Path(path).stem,
                         "text": Path(path).read_text(encoding="utf-8", errors="ignore")})
    return docs

```

> 📺 **UI에서 확인** — 탭 ‘1.적재/파싱’: 파일별 추출 글자 수와 원문 미리보기. 글자 수가 0이면 스캔본(OCR 필요) 신호입니다.

### 확장 과제 (직접 구현)

- 여러 인코딩 자동 감지(UTF-8/CP949) 처리 추가
- 머리말·꼬리말·페이지번호 같은 잡음 제거
- .docx 지원 추가(python-docx)
- 추출 텍스트에 페이지 번호 메타데이터 부착

---

## Stage 2 · 청킹

긴 글을 검색 단위인 ’조각(chunk)’으로 나눕니다. 크기와 오버랩이 검색 품질을 크게 좌우합니다. 각 조각에 출처(source)와 조각 번호(chunk_id)를 메타데이터로 붙여 두면, 나중에 출처 표시와 근거 추적에 씁니다.

### 기본 코드 (제공)

```python
def chunk_text(text: str, size: int, overlap: int):
    text = text.strip()
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i + size])
        i += max(1, size - overlap)   # 경계 문맥 보존
    return out


def make_chunks(docs, size, overlap):
    records = []
    for d in docs:
        for j, c in enumerate(chunk_text(d["text"], size, overlap)):
            if c.strip():
                records.append({"source": d["source"], "chunk_id": j, "text": c})
    return records
```

> 📺 **UI에서 확인** — 탭 ‘2.청킹’: 총 청크 수·평균 길이, 길이 분포 막대그래프, 청크 표(출처·번호·길이·미리보기). 사이드바 슬라이더로 크기/오버랩을 바꿔 ‘파이프라인 실행’ 후 변화를 비교하세요.

### 확장 과제 (직접 구현)

- 문장/문단 단위로 분할(자연스러운 경계)
- 마크다운 헤더(##) 기준 분할
- 너무 짧은 청크는 앞 조각과 병합
- 청크 길이 분포 히스토그램을 더 보기 좋게 개선

---

## Stage 3 · 임베딩

각 청크를 의미를 담은 숫자 벡터로 변환합니다. 정규화하면 벡터 간 내적이 곧 코사인 유사도가 됩니다. 임베딩 행렬의 모양은 (청크 수 × 차원)입니다.

### 기본 코드 (제공)

```python
@st.cache_resource
def get_model(name):
    return SentenceTransformer(name)

def embed(records, model):
    return model.encode([r["text"] for r in records],
                        normalize_embeddings=True).astype("float32")
```

> 📺 **UI에서 확인** — 탭 ‘3.임베딩’: 임베딩 shape, 첫 청크 벡터 미리보기, PCA 2D 산점도(출처별 색). 의미가 비슷한 청크끼리 모이는지 눈으로 확인합니다.

### 확장 과제 (직접 구현)

- 영어/다국어 모델을 바꿔 PCA 군집이 어떻게 달라지는지 비교
- 정규화 on/off의 검색 차이 실험
- 청크 간 코사인 유사도 히트맵 추가
- PCA 대신 t-SNE/UMAP로 투영(선택)

---

## Stage 4 · 저장

벡터를 인덱스(벡터DB)에 적재해 빠르게 검색할 수 있게 합니다. 실습에서는 메모리 인덱스인 FAISS IndexFlatIP(정규화 + 내적 = 코사인)를 사용합니다.

### 기본 코드 (제공)

```python
def build_index(emb):
    index = faiss.IndexFlatIP(emb.shape[1])  # 정규화 + 내적 = 코사인
    index.add(emb)
    return index
```

> 📺 **UI에서 확인** — 탭 ‘4.저장’: 인덱스에 저장된 벡터 수(ntotal)와 차원(d). 청크 수와 ntotal이 같은지 확인하면 적재가 제대로 됐는지 알 수 있습니다.

> **FAISS** = 임베딩 벡터를 담아두고 “가장 비슷한 것 top-k”를 빠르게 찾아주는 벡터 검색 엔진. 이 실습은 가장 단순·정확한 IndexFlatIP에 정규화 벡터를 넣어 코사인 유사도로 검색합니다.

### 확장 과제 (직접 구현)

- 인덱스를 디스크에 저장/로드(faiss.write_index/read_index)
- 청크 메타데이터(JSON)도 함께 저장·복원
- 대용량용 IndexIVFFlat 등 다른 인덱스 비교
- ‘인덱스 다시 만들기 없이 재시작’ 지원

---

## Stage 5 · 검색

질문을 같은 임베딩 모델로 벡터화한 뒤, 인덱스에서 가장 가까운 top-k 청크를 찾습니다. 검색이 틀리면 답도 틀리므로, 이 단계의 품질이 전체를 좌우합니다.

### 기본 코드 (제공)

```python
def retrieve(query, k):
    kb = st.session_state.kb
    model = get_model(kb["model_name"])
    q = model.encode([query], normalize_embeddings=True).astype("float32")
    scores, idx = kb["index"].search(q, k)
    hits = []
    for rank, i in enumerate(idx[0]):
        if i < 0:
            continue
        r = dict(kb["records"][i]); r["score"] = float(scores[0][rank])
        hits.append(r)
    return hits

```

> 📺 **UI에서 확인** — 탭 ‘5.검색’: 검색어를 입력하면 순위·유사도·출처·미리보기 표가 즉시 나옵니다. k와 청크 크기를 바꿔 적중률을 비교하세요.

### 확장 과제 (직접 구현)

- 유사도 임계값을 두어 낮으면 ‘모름’ 처리
- 중복·유사 청크 제거(MMR)로 다양성 확보
- 질의 재작성·동의어 확장으로 검색 실패 회피
- 출처별 필터(특정 문서 안에서만 검색)

---

## Stage 6 · 생성

검색한 근거(컨텍스트)를 프롬프트에 넣어 LLM이 ‘근거 기반’으로 답하게 합니다. 핵심 지시는 ‘컨텍스트만 근거로, 없으면 모른다’입니다.

> ⚠️ **코드 동기화** — 기본 코드는 **Claude · Gemini · 로컬 Ollama를 모두** 지원합니다. `generate(provider="auto")` 는 `active_provider()` 로 Claude → Gemini → Ollama 순으로 고릅니다. 키는 `_get_claude_key()` / `_get_api_key()` 로 안전하게 읽고(파일 없거나 예시 placeholder면 키 없음 취급), Ollama 오류는 연결 실패(`URLError`)와 응답 오류(`HTTPError`, 예: 모델 미설치)로, Claude 오류는 `anthropic.AnthropicError` 로 구분합니다. Claude 는 anthropic SDK 1.x 에서 `temperature` 가 제거되어 온도 인자를 받지 않습니다.

### 기본 코드 (제공)

```python
def build_prompt(query, hits):
    context = "\n\n".join(f"[{h['source']}#{h['chunk_id']}] {h['text']}" for h in hits)
    prompt = ("아래 [컨텍스트]만 근거로 한국어로 간결하게 답하라. "
              "컨텍스트에 없으면 '문서에서 찾을 수 없습니다'라고만 답하라.\n\n"
              f"[컨텍스트]\n{context}\n\n[질문]\n{query}\n\n[답변]")
    return prompt, context

```

> 📺 **UI에서 확인** — 탭 ‘6.생성’: 질문 → 답변 + 출처 + ‘전달된 프롬프트 보기’. 문서에 없는 질문을 넣어 ’모른다’가 나오는지(환각 억제) 확인하세요.

### 확장 과제 (직접 구현)

- 답변에 사용된 청크를 본문에 인용 표시
- 출처 형식 표준화([문서#조각])
- 답변 말투/길이 제어(간결/상세 토글)
- 모델명/온도 등 생성 옵션을 UI로 노출

---

## Stage 7 · 챗봇 구현

단발 질의를 멀티턴 대화로 확장합니다. 대화 기록을 세션에 저장하고, 매 질문마다 검색→생성을 수행합니다. 근거 청크를 펼쳐 볼 수 있게 합니다.

### 기본 코드 (제공)

```python

def render(kb, k):
    st.subheader("Stage 7 · 챗봇")
    if not kb:
        return
    provider, model = llm_controls("chat_")
    st.session_state.setdefault("msgs", [])
    for m in st.session_state.msgs:
        st.chat_message(m["role"]).write(m["content"])
    if q := st.chat_input("문서 내용을 질문하세요"):
        st.chat_message("user").write(q)
        hits = retrieve(q, k)
        prompt, context = build_prompt(q, hits)
        ans = generate(prompt, context, provider, model or None)
        ans += "\n\n**출처:** " + ", ".join(sorted({h["source"] for h in hits}))
        with st.chat_message("assistant"):
            st.write(ans)
            with st.expander("근거 청크"):
                for h in hits:
                    st.markdown(f"**[{h['source']}#{h['chunk_id']}]** "
                                f"(유사도 {h['score']:.2f})\n\n{h['text']}")
        st.session_state.msgs += [{"role": "user", "content": q},
                                  {"role": "assistant", "content": ans}]
```

> 📺 **UI에서 확인** — 탭 ‘7.챗봇’: 대화형 질문·답변 + 근거 청크 expander. 연속 질문을 던지며 사용성을 점검합니다.

### 확장 과제 (직접 구현)

- 이전 대화 맥락을 반영한 후속 질문 재검색
- 대화 초기화 버튼
- 답변 평가 버튼(👍/👎)과 피드백 기록
- 대화 내보내기(저장)

---

## Stage 8 · Q&A 테스트표 작성 및 결과 검수

RAG는 ‘만들면 끝’이 아니라 ’측정하고 검수하는’ 단계가 핵심입니다. 정답을 아는 질문 세트로 자동 채점과 사람 검수를 함께 하여 정확도·출처 적중률·환각률을 숫자로 확인합니다. 챗봇(또는 청크·k·프롬프트)을 손본 전후를 같은 표로 비교하면 개선 효과가 드러납니다.

### ① 테스트표 양식 (CSV)

| 열              | 의미                                        |
| --------------- | ------------------------------------------- |
| id              | 문항 번호                                   |
| question        | 질문                                        |
| expected_answer | 기대 답 (검수 기준)                         |
| expected_source | 기대 출처(문서명) — 출처 적중 채점에 사용   |
| trap            | 함정 여부 (1=문서에 없음 → ’모른다’가 정답) |

### ② 테스트표 예시 (번들 코퍼스 기준)

| id  | question             | expected_answer      | expected_source | trap |
| --- | -------------------- | -------------------- | --------------- | ---- |
| 1   | 물품 신청은 며칠 전? | 최소 3일 전          | 보급규정        | 0    |
| 4   | 체력검정 종목 수는?  | 3종                  | 체력검정안내    | 0    |
| 5   | 당직 근무 시간은?    | 18시~익일 09시       | 당직근무수칙    | 0    |
| 9   | 연차 휴가는 며칠?    | (문서에 없음→모른다) |                 | 1    |

샘플 테스트표는 8.평가/검수 탭의 드롭다운에서 고릅니다.

| 선택 | 파일 | 내용 |
|---|---|---|
| 부대 행정 | `eval_questions.csv` | 규정·수치 위주 10문항(함정 2) |
| 소설 「운수 좋은 날」 | `eval_questions_novel.csv` | 인물·줄거리 10문항(함정 2) |
| 통합 (행정 + 소설) | 두 파일 합침 | 20문항 · 성격별 **구분별 지표**가 함께 표시 |

소설 테스트표는 정답을 아는 사람이 많아 **답이 맞았는지 눈으로 바로 판단**할 수 있습니다.
함정 문항 “아내의 이름은?” 은 원작에도 이름이 나오지 않아 ‘모른다’가 정답입니다.

### ③ 기본 코드 (제공)

```python
def run_eval(test_df, k):
    """테스트표의 각 질문을 검색+생성하고 자동 채점 항목을 채운다."""
    rows = []
    for _, r in test_df.iterrows():
        q = str(r.get("question", "")).strip()
        if not q:
            continue
        hits = retrieve(q, k)
        srcs = sorted({h["source"] for h in hits})
        prompt, ctx = build_prompt(q, hits)
        ans = generate(prompt, ctx)
        refused = "찾을 수 없습니다" in ans
        exp_src = str(r.get("expected_source", "")).strip()
        trap = _is_trap(r.get("trap", 0))
        src_hit = (exp_src in srcs) if exp_src else None
        rows.append({
            "id": r.get("id", ""),
            "question": q,
            "expected_answer": r.get("expected_answer", ""),
            "expected_source": exp_src,
            "trap": trap,
            "actual_answer": ans,
            "retrieved_sources": ", ".join(srcs),
            "top_score": round(hits[0]["score"], 3) if hits else None,
            "source_hit": src_hit,
            "refused": refused,
            "verdict": ("정답" if (trap and refused) else
                        ("오답" if (trap and not refused) else "미검수")),
        })
    return pd.DataFrame(rows)

```

### ④ 평가 지표

| 지표            | 정의                            | 비고                            |
| --------------- | ------------------------------- | ------------------------------- |
| 검수 정답률     | (정답 + 0.5·부분) / 검수 문항   | 사람 판정                       |
| 출처 적중률     | 기대 출처가 top-k에 포함된 비율 | 검색 품질 — 키 없어도 평가 가능 |
| 환각률          | 함정 질문인데 답해버린 비율     | 낮을수록 좋음                   |
| 평균 top 유사도 | 1순위 유사도의 평균             | 검색 신뢰도 참고                |

> 📺 **UI에서 확인** — 탭 ‘8.평가/검수’: 샘플 불러오기 → 테스트표 편집 → ▶ 전체 실행 & 채점 → verdict(정답/부분/오답) 검수 → 지표 4종 + 결과 CSV 다운로드.

### 검수(휴먼 리뷰) 방법

- 자동 채점(출처 적중·‘모름’)과 사람 판정(정답/부분/오답)을 분리한다.
- 부분정답 기준을 팀이 합의한다(예: 핵심 사실은 맞지만 누락·군더더기).
- 출처가 맞아도 답이 틀릴 수 있으니 actual_answer를 함께 본다.
- 정답·환각 평가는 LLM 키가 있을 때 의미가 큼. 키가 없으면 출처 적중률만 신뢰.

### 확장 과제 (직접 구현)

- 같은 표로 청크/k/프롬프트 변경 전후 지표 비교(개선 추적)
- 부분정답 자동 보조(기대 답 키워드 포함 여부 표시)
- 오답·환각 케이스만 필터링해 원인(검색 실패? 생성 무시?) 태깅
- 평가 리포트(지표 + 실패 사례)를 Markdown으로 내보내기

---

## 확장 과제 모음

시간이 남거나 팀별 도전 과제로 활용하세요. 각 과제는 직접 구현하며 개념과 동작 원리를 익히는 것이 목적이며, 필요하면 AI 도구의 도움을 받아도 됩니다.

| 난이도 | 과제                                 | 관련 단계       |
| ------ | ------------------------------------ | --------------- |
| 하     | 유사도 임계값으로 ‘모름’ 처리        | 5 검색 / 6 생성 |
| 하     | 근거 청크 본문 인용·하이라이트       | 6 생성          |
| 중     | 문장/마크다운 헤더 단위 청킹         | 2 청킹          |
| 중     | 인덱스 디스크 저장/로드(persist)     | 4 저장          |
| 중     | 다국어 모델 비교 + 코사인 히트맵     | 3 임베딩        |
| 중상   | MMR 중복 제거 + 질의 재작성          | 5 검색          |
| 중상   | 멀티턴 기억 + 답변 평가 기록         | 7 챗봇          |
| 중     | 평가 리포트 자동 생성(지표+실패사례) | 8 평가/검수     |

> **위임 프롬프트 틀** — “프로젝트 Rules(AGENTS.md)를 따라, [단계] 기능에 [과제]를 추가해줘. 기존 탭 UI에 결과가 보이도록 하고, 변경된 부분만 보여줘.”

---

## 완료 체크리스트 & 트러블슈팅

- [ ] 8개 탭에서 각 단계의 데이터가 보인다(적재 글자수 → 청크 → 임베딩 PCA → 인덱스 → 검색 → 생성 → 대화 → 평가).
- [ ] 한국어 문서는 다국어 모델로 검색이 더 잘 된다.
- [ ] 문서에 없는 질문에 ’모른다’가 나온다.
- [ ] 답변에 출처가 표시된다.
- [ ] 최소 1개 이상의 확장 과제를 직접 구현했다.
- [ ] Q&A 테스트표로 정답률·출처 적중률·환각률을 측정하고 검수했다.
- [ ] 코드/레포에 API 키·민감 데이터가 없다.

| 증상                            | 원인                 | 조치                                                                                                                                          |
| ------------------------------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| 적재 글자수 0                   | 스캔본 PDF           | 텍스트 PDF 사용 또는 OCR 추가                                                                                                                 |
| 한국어 검색 부정확              | 영어 임베딩 모델     | 다국어 모델 선택 후 재실행                                                                                                                    |
| 답이 ’모른다’만                 | 검색 실패/청킹       | k↑, 청크 조정, 질문 재작성                                                                                                                    |
| secrets 없을 때 동작            | 키 미설정            | **자동으로 로컬 Ollama 사용**(또는 검색 근거만)                                                                                               |
| Ollama ‘연결 실패’              | 서버 미실행          | `ollama serve` 실행                                                                                                                           |
| Ollama ‘응답 오류 404’          | 모델 미설치          | `ollama pull qwen2.5:14b`                                                                                                                     |
| `No module named 'torch'`       | venv 미활성화/미설치 | `.venv` 활성화 후 `pip install -r requirements.txt`                                                                                           |
| `WinError 126` (c10.dll)        | VC++ 런타임 없음     | [vc_redist.x64](https://aka.ms/vs/17/release/vc_redist.x64.exe) 설치 후 재부팅 ([상세](#원인--visual-c-재배포-패키지vc-redistributable-누락)) |
| `No module named 'torchvision'` | 미설치(감시자 로그)  | `pip install torchvision` — 앱 동작엔 무해                                                                                                    |
| 첫 실행 느림                    | 모델 다운로드        | @st.cache_resource 캐싱 확인                                                                                                                  |

---

## 부록 · 기본 코드 구조

> ⚠️ **코드 동기화** — 단일 `app.py` 가 아니라 단계별 모듈(`stages/`)로 분리되어 있고,
> 학생 배포판은 워크북(`app_lab.py`) + 단계별 워크북 모듈(`stages/stageN_*_lab.py`)로 구성됩니다.
> 모범답안은 `rag_answer.zip`(기본)·`rag_solution.zip`(고급)으로 함께 배포됩니다.

```
rag_lab/
  app_lab.py             # 기본 코드: 사이드바 + st.tabs(8단계) 오케스트레이터
  stages/                # 단계별 모듈 (한 파일 = 한 단계: 함수 + 탭 render)
    stage1_load_lab.py … stage8_eval_lab.py
  docs/                  # 가상·공개 코퍼스
  eval_questions.csv / eval_questions_novel.csv   # Stage 8 샘플 테스트표 2종
  .streamlit/secrets.toml.example   # CLAUDE/GEMINI 키 템플릿
rag_answer.zip / rag_solution.zip   # 모범답안(확장 과제 적용) — 비교용

# 단계 함수
read_pdf/load_documents(1)  chunk_text/make_chunks(2)  get_model/embed/pca_2d(3)
build_index(4)  retrieve(5)  build_prompt/generate(6, Claude/Gemini/Ollama)  run_eval(8)

# 중간 데이터(docs/records/emb/index)는 st.session_state.kb 에 저장 → 각 탭에서 표시
```

> **연결** — 이 기본 코드는 ‘바이브 코딩’ 흐름과 이어집니다. `AGENTS.md`/Rules 에 단계·UI 규칙을 적어두고, 확장 과제를 AI에 위임하면 일관된 결과를 얻습니다.
