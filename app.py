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

qt_test_items = {
    "토공사 및 기초공사": ["함수비", "밀도", "다짐", "평판재하", "현장밀도"],
    "철근콘크리트공사": ["슬럼프", "공기량", "압축강도", "염화물", "항복강도", "인장강도"],
    "철강구조물공사": ["내부결함", "초음파탐상", "인장강도", "용접부"],
    "아스팔트 포장공사": ["마샬안정도", "역청함유량", "코어", "두께", "평탄성"]
}

equipment_rules = {
    "필수/기본 장비": ["만능시험기", "건조로", "저울", "체가름시험기", "모르타르혼합기"],
    "토질/골재 장비": ["비중", "현장밀도시험기", "염화물", "안정성"],
    "아스팔트 장비": ["마샬안정도시험기", "항온수조", "아스팔트함량시험기"]
}

approval_rules = {
    "승인 절차 명시": ["검토", "승인", "적정", "조건부적정", "부적정", "시정요구", "조치확인"]
}

# --- 3. 텍스트 스캔 및 판정 엔진 ---
def analyze_checklist(text, rules, threshold=0.6):
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
        
        detail = f"확인({len(found)}): {', '.join(found)}" if found else "확인불가"
        if missing:
            detail += f" / 누락({len(missing)}): {', '.join(missing)}"
            
        results.append({"점검 항목": category, "검증 판정": status, "세부 내역": detail})
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
            # 1차 시도: 일반 텍스트 추출
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            
            # 2차 시도: 글자가 너무 적으면 스캔본으로 간주하여 OCR 수행
            if len(text.strip()) < 50:
                st.warning("📷 스캔된 이미지 문서로 인식되었습니다. OCR(광학 문자 인식)을 수행합니다. (시간이 조금 더 걸립니다.)")
                uploaded_file.seek(0)
                images = convert_from_bytes(uploaded_file.read())
                
                # 프로그레스 바 추가
                progress_bar = st.progress(0)
                for i, img in enumerate(images):
                    text += pytesseract.image_to_string(img, lang='kor+eng') + "\n"
                    progress_bar.progress((i + 1) / len(images))
                progress_bar.empty()
                
        except Exception as e:
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
            st.stop()

        # 프로젝트 규모 추출
        cost_match = re.search(r'총공사비.*?([\d,]+)\s*억', text)
        area_match = re.search(r'연면적.*?([\d,]+)\s*㎡', text)
        lab_size_match = re.search(r'시험실\s*규모.*?([\d.]+)\s*㎡', text)

        cost = int(cost_match.group(1).replace(',', '')) if cost_match else 0
        area = int(area_match.group(1).replace(',', '')) if area_match else 0
        lab_size = float(lab_size_match.group(1)) if lab_size_match else 0.0

        level, req_lab_size, req_personnel = check_facility_and_personnel(cost, area)
        
        st.success("✅ 문서 분석 및 법령 대조가 완료되었습니다.")
        
        t1, t2, t3, t4 = st.tabs([
            "1️⃣ 기본 규모 및 시설(별표5,9)", 
            "2️⃣ 품질관리계획 적절성(별지2, 별표1,3)", 
            "3️⃣ 공종별 시험/장비(별표2,6)",
            "4️⃣ 검토/승인 절차(별지1)"
        ])
        
        def highlight_status(val):
            if '적정' in val: return 'color: #155724; background-color: #d4edda; font-weight: bold'
            elif '보완' in val or '미달' in val: return 'color: #721c24; background-color: #f8d7da; font-weight: bold'
            return ''

        with t1:
            st.subheader("📌 프로젝트 개요 및 법정 배치기준 검증")
            col_a, col_b = st.columns(2)
            with col_a:
                st.info("문서 내 추출 데이터")
                st.write(f"- **총공사비:** {cost} 억원")
                st.write(f"- **연면적:** {area} ㎡")
                st.write(f"- **계획 시험실 면적:** {lab_size} ㎡")
            with col_b:
                st.warning("건설기술 진흥법 시행규칙 [별표 5] 기준")
                st.write(f"- **요구 등급:** {level}")
                st.write(f"- **최소 면적:** {req_lab_size} ㎡ 이상")
                st.write(f"- **최소 인력:** {', '.join(req_personnel)}")
                
            st.markdown("#### [별표 9] 품질시험계획 필수항목 점검")
            df_basic = analyze_checklist(text, qt_basic_rules, 0.7)
            st.dataframe(df_basic.style.map(highlight_status, subset=['검증 판정']), use_container_width=True)

        with t2:
            st.subheader("📋 품질관리계획 적절성 확인 (10대 핵심항목)")
            df_qm = analyze_checklist(text, qm_10_rules, 0.5)
            st.dataframe(df_qm.style.map(highlight_status, subset=['검증 판정']), use_container_width=True)

        with t3:
            st.subheader("🔬 공종별 품질시험 기준 및 장비 보유 점검")
            st.write("##### 1. 공종별 주요 시험종목 누락 점검")
            df_test = analyze_checklist(text, qt_test_items, 0.4) 
            st.dataframe(df_test.style.map(highlight_status, subset=['검증 판정']), use_container_width=True)
            
            st.write("##### 2. 필수 시험장비 보유 점검")
            df_equip = analyze_checklist(text, equipment_rules, 0.5)
            st.dataframe(df_equip.style.map(highlight_status, subset=['검증 판정']), use_container_width=True)

        with t4:
            st.subheader("📝 검토 및 승인 절차 (별지 1 기준)")
            df_approval = analyze_checklist(text, approval_rules, 0.6)
            st.dataframe(df_approval.style.map(highlight_status, subset=['검증 판정']), use_container_width=True)
