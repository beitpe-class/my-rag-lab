"""[실습] Stage 2 · 청킹 — 긴 텍스트를 검색 단위 '조각'으로 나눈다."""
import pandas as pd
import streamlit as st


def chunk_text(text: str, size: int, overlap: int):
    """[목표] 텍스트를 size 글자 단위로 자르되 overlap 만큼 겹치게 한다.
    출력: list[str] 조각 리스트

    [구현 단계]
      1) text = text.strip()
      2) i=0 에서 시작해 text[i : i+size] 를 결과에 추가
      3) i 를 max(1, size - overlap) 만큼 전진 (겹침으로 경계 문맥 보존)
      4) i 가 len(text) 이상이면 종료

    [예제] 슬라이딩 윈도우 골격:
        out, i = [], 0
        while i < len(text):
            out.append(text[i:i+size])
            i += max(1, size - overlap)
    """
    # ✏️ TODO: 위 골격을 완성해 조각 리스트를 반환하세요.
    raise NotImplementedError("chunk_text 를 구현하세요 (Stage 2)")


def make_chunks(docs, size, overlap):
    """[목표] 각 문서를 chunk_text 로 자르고 메타데이터(출처·번호)를 붙인다.
    출력: list[dict] — {"source": 출처, "chunk_id": 번호, "text": 조각}

    [구현 단계]
      1) docs 의 각 d 에 대해 chunk_text(d["text"], size, overlap) 호출
      2) enumerate 로 번호(j)를 매기며, 빈 조각(c.strip()==False)은 건너뜀
      3) records.append({"source": d["source"], "chunk_id": j, "text": c})

    [예제]
        for j, c in enumerate(chunk_text(d["text"], size, overlap)):
            if c.strip():
                records.append({"source": d["source"], "chunk_id": j, "text": c})
    """
    records = []
    # ✏️ TODO: 모든 문서를 조각내 메타를 붙인 records 를 채우고 반환하세요.
    raise NotImplementedError("make_chunks 를 구현하세요 (Stage 2)")


def render(kb):
    """[제공] '2.청킹' 탭 — 청크 수·평균 길이·길이 분포·청크 표."""
    st.subheader("Stage 2 · 청킹  ✏️실습")
    if not kb:
        return
    df = pd.DataFrame([{"source": r["source"], "chunk_id": r["chunk_id"],
                        "길이": len(r["text"]), "미리보기": r["text"][:60]}
                       for r in kb["records"]])
    st.write(f"총 청크: **{len(df)}개** · 평균 길이 {df['길이'].mean():.0f}자")
    st.bar_chart(df["길이"])
    st.dataframe(df, use_container_width=True, height=300)
