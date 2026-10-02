import streamlit as st
import fitz  # PyMuPDF
import base64
from openai import OpenAI
import os

st.set_page_config(page_title="품질시험계획서 검증 (GPT-4o)", page_icon="🏗️", layout="wide")
st.title("🏗️ AI 기반 품질관리/시험계획서 자동 검증")
st.markdown("강력한 **GPT-4o Vision 엔진**을 탑재하여 스캔된 문서의 표와 문맥까지 완벽하게 대조합니다.")
st.divider()

# OpenAI API 키 안전하게 불러오기
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
except Exception:
    st.error("⚠️ 오류: API 키가 설정되지 않았습니다. Streamlit Secrets 설정을 확인해주세요.")
    st.stop()

uploaded_file = st.file_uploader("검증할 계획서(PDF 스캔본 가능)를 업로드하세요.", type="pdf")

if uploaded_file is not None:
    if st.button("🚀 GPT-4o 교차검증 시작", type="primary", use_container_width=True):
        with st.spinner("GPT-4o가 스캔된 문서를 분석하고 방대한 법령과 대조 중입니다..."):
            try:
                # 1. PDF를 고화질 이미지로 변환 (서버 설정 불필요)
                pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                base64_images = []
                
                for page_num in range(len(pdf_document)):
                    page = pdf_document.load_page(page_num)
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img_bytes = pix.tobytes("png")
                    base64_images.append(base64.b64encode(img_bytes).decode('utf-8'))
                
                # 2. AI 프롬프트 및 이미지 데이터 구성
                messages = [
                    {"role": "system", "content": "당신은 대한민국 건설공사 품질관리 최고 심사관입니다."},
                    {"role": "user", "content": [
                        {"type": "text", "text": """
                        첨부된 품질시험계획서 PDF 문서를 분석하여 다음 기준에 따라 적절성을 검증해 주세요.
                        
                        1. 시행규칙 [별표 5]: 총공사비/연면적 대비 대상 등급, 최소 시험실 규모, 배치 기술인 기준 충족 여부
                        2. 업무지침 [별표 2]: 공종별 필수 시험종목 누락 여부
                        3. 업무지침 [별표 6]: 필수 시험 장비 명시 여부
                        4. [별표 9] 및 [별지 2]: 기타 필수 기재사항 누락 여부
                        
                        결과를 마크다운 표로 깔끔하게 정리하고, 보완이 필요한 부분은 🚨 이모지와 함께 명확히 짚어주세요.
                        """}
                    ]}
                ]
                
                # 변환된 이미지들을 메시지에 추가
                for base64_image in base64_images:
                    messages[1]["content"].append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                    })
                
                # 3. GPT-4o 모델 호출
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=3000
                )
                
                st.success("✅ 검증 완료!")
                st.markdown(response.choices[0].message.content)

            except Exception as e:
                st.error(f"분석 중 오류가 발생했습니다: {e}")
