import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- 1. 웹사이트 기본 설정 ---
st.set_page_config(page_title="AI 기반 품질시험계획서 검증", page_icon="🏗️", layout="wide")
st.title("🏗️ AI 기반 품질관리/시험계획서 자동 검증")
st.markdown("""
스캔된 문서도 완벽하게 읽어내는 **Vision AI**를 적용했습니다. 
계획서를 업로드하시면 법령([별표 2, 5, 6, 9], [별지 1, 2])을 바탕으로 누락된 항목을 꼼꼼히 짚어드립니다.
""")
st.divider()

# --- 2. API 키 안전하게 불러오기 (안전장치 추가) ---
try:
    # Streamlit Secrets에서 키를 가져와 시스템 환경변수에 강제 주입
    api_key = st.secrets["GEMINI_API_KEY"]
    os.environ["GEMINI_API_KEY"] = api_key 
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 시스템 오류: API 키가 설정되지 않았습니다. Streamlit Secrets 설정을 확인해주세요.")
    st.stop()

# 최신 시각지능 모델 사용
model = genai.GenerativeModel('gemini-1.5-pro')

# --- 3. 파일 업로드 및 검증 실행 ---
uploaded_file = st.file_uploader("검증할 계획서(PDF)를 이곳에 업로드하세요. (스캔본 가능)", type="pdf")

if uploaded_file is not None:
    if st.button("🚀 AI 교차검증 시작", type="primary", use_container_width=True):
        with st.spinner("AI가 스캔된 표의 문맥을 분석하고 방대한 법령과 대조 중입니다. (약 15~30초 소요)"):
            
            # PDF 파일을 AI 서버로 전송하기 위해 임시 파일로 저장
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            try:
                # 구글 AI 서버로 파일 업로드
                uploaded_pdf = genai.upload_file(path=tmp_file_path)

                # AI에게 내릴 강력한 지시사항(프롬프트)
                prompt = """
                당신은 대한민국 건설공사 품질관리 전문 최고 심사관입니다.
                첨부된 품질시험계획서(또는 품질관리계획서) PDF의 모든 표와 내용을 분석하여 
                다음의 '건설기술 진흥법' 및 '품질관리 업무지침' 기준에 따라 적절성을 검증해 주세요.

                [검증 필수 항목]
                1. 시행규칙 [별표 5]: 총공사비 및 연면적을 찾아내어, 그 규모에 맞는 '품질관리 대상 등급', '최소 시험실 규모(㎡)', '최소 배치 기술인 수와 등급'이 올바르게 계획되었는지 판별.
                2. 업무지침 [별표 2]: 문서에 명시된 공종들을 파악하고, 각 공종에 필수적인 '시험 종목'이 누락 없이 기재되었는지 점검.
                3. 업무지침 [별표 6]: 해당 공종에 반드시 필요한 '시험 장비'가 보유 장비 목록에 명시되어 있는지 점검.
                4. 시행령 [별표 9] 및 업무지침 [별지 2]: 기타 필수 기재사항(공사개요, 시험빈도, 검토/승인 절차 등) 누락 여부.

                [출력 형식]
                결과를 마크다운(Markdown) 표와 글머리 기호를 활용하여 보기 좋고 깔끔하게 정리해 주세요.
                누락되거나 미달된 부분은 🚨 이모지와 함께 '보완 권고 사항'으로 명확히 짚어주세요.
                """

                # 분석 결과 생성
                response = model.generate_content([uploaded_pdf, prompt])
                
                st.success("✅ AI 검증이 완료되었습니다!")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"AI 분석 중 오류가 발생했습니다: {e}")
            finally:
                # 보안 및 용량 관리를 위해 분석이 끝난 임시 파일 즉시 삭제
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
                try:
                    genai.delete_file(uploaded_pdf.name)
                except:
                    pass
