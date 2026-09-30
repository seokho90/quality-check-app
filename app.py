import streamlit as st
import pdfplumber
import re
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes

# --- 1. [별표 5] 법정 시설 및 인력 기준 산출 ---
def check_facility_and_personnel(cost, area):
    if cost >= 1000 or area >= 50000:
        return "특급 품질관리", 50, ["특급 1명(경력 3년 이상)", "중급 1명 이상", "초급 1명 이상"]
    elif cost >= 500 or area >= 30000:
        return "고급 품질관리", 50, ["고급 1명(경력 2년 이상)", "중급 1명 이상", "초급 1명 이상"]
    elif cost >= 100 or area >= 5000:
        return "중급 품질관리", 18, ["중급 1명(경력 1년 이상)", "초급 1명 이상"]
    else:
        return "초급 품질관리", 18, ["초급 1명 이상"]

# --- 2. 종합 법령/지침 기반 키워드 룰셋 ---
qm_10_rules = {
    "1. 일반사항": ["작성근거", "개정현황", "문서번호"],
    "2. 적용범위 및 인용표준": ["적용범위", "인용표준", "ISO"],
    "3. 용어 정의": ["용어", "정의"],
    "4. 조직 상황": ["정보", "이해관계자", "프로세스", "요구사항"],
    "5. 리더십": ["품질방침", "책임", "권한", "조직"],
    "6. 기획": ["리스크", "기회", "품질목표", "추진계획"],
    "7. 지원": ["자원관리", "모니터링", "역량", "적격성", "교육훈련", "의사소통", "문서화된정보"],
    "8. 운용": ["설계관리", "기자재구매", "하도급", "중점품질관리", "식별및추적", "검사및시험", "부적합공사"],
    "9. 성과관리": ["고객만족", "분석및평가", "내부심사", "경영검토"],
    "10. 개선": ["부적합", "시정조치", "지속적개선"]
}

qt_basic_rules = {
    "1. 공사 개요": ["공사명", "시공자", "현장대리인"],
    "2. 시험 계획": ["공종", "시험종목", "계획물량", "시험빈도", "시험횟수"],
    "3. 시험 시설": ["장비명", "규격", "단위", "수량", "배치평면도"],
    "4. 품질관리 인력": ["성명", "등급", "배치계획", "자격", "경력"]
}

approval_rules = {
    "승인 절차 명시": ["검토", "승인", "적정", "조건부적정", "부적정", "시정요구", "조치확인"]
}

qt_test_items_detailed = {
    "토공사(성토용 흙)": ["함수비", "입도", "밀도", "다짐", "액성한계", "소성한계", "노상토지지력비"],
    "기초공사(말뚝)": ["동재하", "정재하", "압축강도"],
    "콘크리트용 골재": ["밀도", "흡수율", "조립률", "0.08밀리미터체", "안정성", "마모율"],
    "굳지 않은 콘크리트": ["슬럼프", "공기량", "염화물", "단위수량", "온도"],
    "굳은 콘크리트": ["압축강도", "휨강도"],
    "철근(콘크리트용 봉강)": ["항복점", "항복강도", "인장강도", "연신율", "치수"],
    "철강구조물(강재/용접)": ["내부결함", "초음파탐상", "자분탐상", "항복점", "인장강도", "연신율"],
    "아스팔트 혼합물": ["밀도", "안정성", "마샬안정도", "역청함유량", "코어"],
    "가설기자재(강관/파이프)": ["압축하중", "인장하중", "휨하중"]
}

equipment_rules_detailed = {
    "공통/일반(인장·압축)": ["만능시험기", "압축시험기"],
    "토질/골재 장비": ["건조로", "저울", "체가름시험기", "현장밀도시험기", "자동다짐기", "안정성시험용기구"],
    "콘크리트 장비": ["모르타르혼합기", "항온수조", "슬럼프", "공기량시험기", "압축강도", "공시체"],
    "아스팔트 장비": ["마샬안정도시험기", "아스팔트함량시험기", "코어채취기"]
}

# --- 3. 텍스트 스캔 및 판정 엔진 (상세 피드백용) ---
def analyze_detailed_checklist(text, rules, threshold=0.5):
    results = []
    text_clean = text.replace(" ", "")
    for category, keywords in rules.items():
        found = []
        missing = []
        for kw in keywords:
            kw_clean = kw.replace(" ", "")
            if kw_clean in text_clean:
                found.append(kw)
            else:
                missing.append(kw)
        
        score = len(found) / len(keywords) if keywords else 0
        status = "✅ 적정" if score >= threshold else "🚨 보완필요"
        
        if missing:
            detail = f"[확인됨] {', '.join(found)}\n[누락됨] {', '.join(missing)}\n👉 보완조치: 별표 기준에 따라 '{', '.join(missing)}' 항목을 계획서에 추가 기재 요망."
        else:
            detail = f"[확인됨] {', '.join(found)}\n👉 보완조치: 해당 공종의 법정 필수항목이 모두 명시됨."
            
        results.append({"종별(항목)": category, "판정": status, "세부 점검내역 및 수정권고": detail})
    return pd.DataFrame(results)

# --- 4. 웹 UI 구성 ---
st.set_page_config(page_title="건설공사 품질시험계획서 통합 검증", page_icon="🏗️", layout="wide")

st.title("🏗️ 품질관리/시험계획서 법령 통합 교차검증 시스템")
st.markdown("**적용 법령 및 지침:** 건설공사 품질관리 업무지침, 건설기술 진흥법 시행령·시행규칙 전체")
st.divider()

uploaded_file = st.file_uploader("검증할 계획서 원본(또는 스캔본 PDF)을 업로드 하세요.", type="pdf")

if uploaded_file is not None:
    with st.spinner("문서를 스캔 중입니다..."):
        text = ""
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            
            if len(text.strip()) < 50:
                st.warning("📷 스캔된 이미지 문서로 인식되었습니다. OCR(광학 문자 인식)을 수행합니다. (시간이 조금 더 걸립니다.)")
                uploaded_file.seek(0)
                images = convert_from_bytes(uploaded_file.read())
                
                progress_bar = st.progress(0)
                for i, img in enumerate(images):
                    text += pytesseract.image_to_string(img, lang='kor+eng') + "\n"
                    progress_bar.progress((i + 1) / len(images))
                progress_bar.empty()
                
        except Exception as e:
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
            st.stop()

        cost_match = re.search(r'총공사비.*?([\d,]+)\s*억', text)
        area_match = re.search(r'연면적.*?([\d,]+)\s*㎡', text)

        extracted_cost = int(cost_match.group(1).replace(',', '')) if cost_match else 0
        extracted_area = int(area_match.group(1).replace(',', '')) if area_match else 0
        
        st.success("✅ 문서 분석 및 법령 대조가 완료되었습니다.")
        
        t1, t2, t3, t4 = st.tabs([
            "1️⃣ 기본 규모 및 시설", 
            "2️⃣ 품질관리계획 적절성", 
            "3️⃣ 공종별 시험/장비 상세검증",
            "4️⃣ 검토/승인 절차"
        ])
        
        def highlight_status(val):
            if '적정' in val: return 'color: #155724; background-color: #d4edda; font-weight: bold'
            elif '보완' in val or '미달' in val: return 'color: #721c24; background-color: #f8d7da; font-weight: bold'
            return ''

        with t1:
            st.subheader("📌 프로젝트 규모 입력 및 법정 배치기준 확인")
            st.markdown("문서에서 추출된 초기값이 자동 입력되어 있습니다. 실제 계획과 다를 경우 직접 수정하면 기준이 즉시 재계산됩니다.")
            
            # 입력 폼 배치
            col_input1, col_input2 = st.columns(2)
            with col_input1:
                input_cost = st.number_input("총공사비 (단위: 억원)", min_value=0, value=extracted_cost, step=10)
            with col_input2:
                input_area = st.number_input("연면적 (단위: ㎡)", min_value=0, value=extracted_area, step=100)
            
            # 실시간 법정 기준 계산
            level, req_lab_size, req_personnel = check_facility_and_personnel(input_cost, input_area)
            
            st.info("⚖️ **건설기술 진흥법 시행규칙 [별표 5] 기준 자동 산출 결과**")
            st.write(f"- **대상공사 구분:** {level}")
            st.write(f"- **최소 시험실 규모:** {req_lab_size} ㎡ 이상")
            st.write(f"- **최소 배치 인력:** {', '.join(req_personnel)}")
            
            st.divider()
                
            st.markdown("#### [별표 9] 품질시험계획 필수항목 점검")
            df_basic = analyze_detailed_checklist(text, qt_basic_rules, 0.7)
            st.dataframe(df_basic.style.map(highlight_status, subset=['판정']), use_container_width=True)

        with t2:
            st.subheader("📋 품질관리계획 적절성 확인 (10대 핵심항목)")
            df_qm = analyze_detailed_checklist(text, qm_10_rules, 0.5)
            st.dataframe(df_qm.style.map(highlight_status, subset=['판정']), use_container_width=True)

        with t3:
            st.subheader("🔬 공종별 품질시험 기준 및 장비 보유 상세점검")
            st.markdown("**(안내) 본 프로젝트에 해당하는 공종만 확인하시면 됩니다.**")
            
            st.write("##### 1. 공종별 주요 시험종목 누락 점검 ([별표 2] 기준)")
            df_test = analyze_detailed_checklist(text, qt_test_items_detailed, 0.3)
            st.table(df_test) 
            
            st.write("##### 2. 필수 시험장비 보유 점검 ([별표 6] 기준)")
            df_equip = analyze_detailed_checklist(text, equipment_rules_detailed, 0.4)
            st.table(df_equip)

        with t4:
            st.subheader("📝 검토 및 승인 절차 ([별지 1] 기준)")
            df_approval = analyze_detailed_checklist(text, approval_rules, 0.6)
            st.dataframe(df_approval.style.map(highlight_status, subset=['판정']), use_container_width=True)
