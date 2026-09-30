import streamlit as st
import pdfplumber
import re
import pandas as pd

# --- 1. 법적 기준 판별 로직 ---
def check_facility_and_personnel(cost, area):
    """건설기술 진흥법 시행규칙 [별표 5] 기준"""
    if cost >= 1000 or area >= 50000:
        return "특급 품질관리", 50, ["특급 1명(경력 3년↑)", "중급 1명↑", "초급 1명↑"]
    elif cost >= 500 or area >= 30000: 
        return "고급 품질관리", 50, ["고급 1명(경력 2년↑)", "중급 1명↑", "초급 1명↑"]
    elif cost >= 100 or area >= 5000:
        return "중급 품질관리", 18, ["중급 1명(경력 1년↑)", "초급 1명↑"]
    else:
        return "초급 품질관리", 18, ["초급 1명↑"]

# --- 2. 웹사이트 화면 구성 ---
st.set_page_config(page_title="품질시험계획서 검증 시스템", page_icon="🏗️", layout="wide")

st.title("🏗️ 품질시험계획서 교차검증 시스템")
st.markdown("""
누구나 건설공사 품질시험계획서(PDF)를 업로드하면, **건설기술 진흥법 법령 기준([별표 5], [별표 9])**을 바탕으로 누락된 항목이 없는지, 기준을 충족하는지 교차 검증해 줍니다.
""")

st.divider()

# 파일 업로드 컴포넌트
uploaded_file = st.file_uploader("검증할 품질시험계획서 PDF 파일을 이곳에 드래그 앤 드롭 하세요.", type="pdf")

if uploaded_file is not None:
    with st.spinner("문서를 분석하고 법적 기준과 교차 검증 중입니다..."):
        text = ""
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e:
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
            st.stop()

        # --- 3. 데이터 추출 (정규표현식) ---
        cost_match = re.search(r'총공사비\s*[:]\s*([\d,]+)\s*억', text)
        area_match = re.search(r'연면적\s*[:]\s*([\d,]+)\s*㎡', text)
        lab_size_match = re.search(r'시험실\s*규모\s*[:]\s*([\d.]+)\s*㎡', text)

        cost = int(cost_match.group(1).replace(',', '')) if cost_match else 0
        area = int(area_match.group(1).replace(',', '')) if area_match else 0
        lab_size = float(lab_size_match.group(1)) if lab_size_match else 0.0

        # 기준 도출
        level, req_lab_size, req_personnel = check_facility_and_personnel(cost, area)
        
        # --- 4. 결과 출력 화면 ---
        st.success("✅ 문서 분석 및 교차검증이 완료되었습니다!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("### 📄 계획서 추출 정보")
            st.write(f"- **입력된 총공사비:** {cost} 억원")
            st.write(f"- **입력된 연면적:** {area} ㎡")
            st.write(f"- **계획된 시험실 규모:** {lab_size} ㎡")
            
        with col2:
            st.warning("### ⚖️ 법적 요구 기준 ([별표 5])")
            st.write(f"- **요구 등급:** {level} 대상")
            st.write(f"- **최소 시험실 면적:** {req_lab_size} ㎡ 이상")
            st.write(f"- **필수 배치인력:** {', '.join(req_personnel)}")

        st.subheader("📋 필수 기재항목 점검 결과 ([별표 9] 기준)")
        
        # 키워드 점검 로직
        check_items = {
            "항목": [
                "개요 (공사명, 시공자 등 기재)", 
                "시험계획 (공종, 종목, 빈도 명시)", 
                "시험시설 (장비명, 평면도 등 기재)",
                "건설기술인 배치계획 명시",
                "시험실 면적 기준 충족 여부"
            ],
            "검증 결과": [
                "적정" if "공사명" in text and "시공자" in text else "부적정(누락 의심)",
                "적정" if "시험 종목" in text and "시험 빈도" in text else "부적정(누락 의심)",
                "적정" if "장비명" in text else "부적정(누락 의심)",
                "적정" if "건설기술인" in text and "등급" in text else "부적정(누락 의심)",
                "적정" if lab_size >= req_lab_size else "부적정(면적 미달)"
            ]
        }
        
        df_result = pd.DataFrame(check_items)
        
        # 결과에 따른 색상 지정
        def highlight_result(val):
            if "적정" in val and "부적정" not in val:
                return 'color: green; font-weight: bold'
            elif "부적정" in val:
                return 'color: red; font-weight: bold'
            return ''
        
        st.dataframe(df_result.style.map(highlight_result, subset=['검증 결과']), use_container_width=True)

        if "부적정" in df_result['검증 결과'].to_string():
            st.error("🚨 부적정(누락) 항목이 발견되었습니다. 계획서를 수정하여 다시 확인해주세요.")
        else:
            st.balloons()
            st.success("🎉 완벽합니다! 법적 필수 항목과 기준을 모두 충족하는 것으로 확인됩니다.")
