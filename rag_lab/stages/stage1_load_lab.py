"""[실습] Stage 1 · 적재/파싱 — 파일에서 순수 텍스트를 뽑아낸다.

수강생이 직접 채우는 실습용 파일입니다. 각 함수의 설명과 예제를 읽고
✏️TODO 를 구현하세요. 완성하면 app_lab.py 의 '1.적재/파싱' 탭에 결과가 나타납니다.
정답이 궁금하면 stages/stage1_load.py (기본 코드)를 참고하세요.
"""
import io
from glob import glob
from pathlib import Path

import streamlit as st
from pypdf import PdfReader


def read_pdf(data: bytes) -> str:
    """[목표] PDF 바이트에서 모든 페이지 텍스트를 이어붙여 반환.
    입력: data(bytes) PDF raw 바이트 / 출력: str 전체 텍스트(페이지 사이 줄바꿈)

    [구현 단계]
      1) io.BytesIO(data) 로 바이트를 파일처럼 감싼다
      2) PdfReader(...).pages 를 순회한다
      3) page.extract_text() 결과를 "\n" 으로 join (None 방어: 'or ""')

    [예제] 첫 페이지만 읽기:
        reader = PdfReader(io.BytesIO(data))
        first = reader.pages[0].extract_text() or ""
    """
    # ✏️ TODO: 전체 페이지 텍스트를 합쳐 반환하세요.
    raise NotImplementedError("read_pdf 를 구현하세요 (Stage 1)")


def load_documents(files, include_folder):
    """[목표] 업로드 파일 + docs/ 폴더를 읽어 문서 리스트를 만든다.
    출력: list[dict] — {"source": 문서명, "text": 본문}

    [구현 단계]
      1) files 순회: 확장자 Path(f.name).suffix.lower(), 바이트 f.getvalue()
         - .pdf 면 read_pdf(data), 아니면 data.decode("utf-8","ignore")
         - docs.append({"source": Path(f.name).stem, "text": 본문})
      2) include_folder 가 True 면 sorted(glob("docs/*")) 도 같은 형식으로 추가
         - 본문: Path(path).read_text(encoding="utf-8", errors="ignore")

    [예제] 업로드 파일 하나 처리:
        data = f.getvalue()
        ext = Path(f.name).suffix.lower()
        text = read_pdf(data) if ext == ".pdf" else data.decode("utf-8", "ignore")
    """
    docs = []
    # ✏️ TODO: 업로드 파일과 docs/ 폴더를 읽어 docs 를 채우고 반환하세요.
    raise NotImplementedError("load_documents 를 구현하세요 (Stage 1)")


def render(kb):
    """[제공] '1.적재/파싱' 탭 — 문서별 글자수 + 원문 미리보기.
    (그대로 두세요. load_documents 가 완성되면 결과가 보입니다.)"""
    st.subheader("Stage 1 · 적재 / 파싱  ✏️실습")
    if not kb:
        st.info("← 사이드바에서 문서를 넣고 **파이프라인 실행**을 누르세요.")
        return
    for d in kb["docs"]:
        with st.expander(f"📄 {d['source']} · {len(d['text']):,}자"):
            st.text(d["text"][:1500] + ("..." if len(d["text"]) > 1500 else ""))
