import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 스타일 (UI/UX)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="건진법 감리 착수단계 법정업무 관제 시스템",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 1.7rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .law-box {
        background-color: #F8FAFC;
        border-left: 5px solid #3B82F6;
        padding: 12px 16px;
        border-radius: 4px;
        margin-top: 8px;
        font-size: 0.9rem;
    }
    .audit-box {
        background-color: #FFFBEB;
        border-left: 5px solid #F59E0B;
        padding: 12px 16px;
        border-radius: 4px;
        margin-top: 8px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 건진법 및 수행지침 제50조~제66조 기반 착수단계 20대 법정업무 마스터 DB
# -----------------------------------------------------------------------------
def get_initial_tasks():
    return [
        # [1. 행정/조직]
        {
            "id": "ADM-01",
            "domain": "1. 행정/조직",
            "phase": "Phase 1. 용역착수 즉시",
            "task": "용역 착수신고서 및 건설사업관리기술인 배치계획 제출",
            "law_short": "수행지침 제50조 제1항 / 규칙 제35조",
            "law_detail": "건설사업관리용역사업자는 계약 체결 즉시 상주 및 기술지원 기술인 투입기간·업무내용이 포함된 배치계획서, 과업수행계획서, 경력확인서를 첨부하여 발주청에 착수신고서를 제출해야 한다.",
            "owner": "책임감리원 / 본사",
            "anchor": "contract",
            "offset_days": 7,
            "due_desc": "용역착수 후 7일 이내",
            "hold_point": False,
            "audit_risk": "배치계획서상의 투입일자와 실제 현장 투입(CEMS 등재) 일자 불일치 지적 주의",
            "checklist": [
                "상주기술인 및 기술지원기술인 법정 자격·등급 적정성 확인",
                "감리원 경력확인서, 예정공정표, 산출내역서 첨부 여부",
                "건설사업관리정보시스템(CEMS) 배치 신고 연동 확인"
            ],
            "deliverable": "감리용역 착수신고서, 기술인 배치계획서",
            "status": "완료",
            "doc_no": "감리 제2026-001호"
        },
        {
            "id": "ADM-02",
            "domain": "1. 행정/조직",
            "phase": "Phase 1. 용역착수 즉시",
            "task": "감리원 개인별 업무분장 및 직무권한 명시·통보",
            "law_short": "수행지침 제50조 제9항",
            "law_detail": "책임건설사업관리기술인은 현장에 배치된 각 기술인의 개인별 업무를 분담하고, 분담 내용에 따라 권한을 명시하여 발주청에 보고하고 시공자에게 통보하여야 한다.",
            "owner": "책임감리원",
            "anchor": "contract",
            "offset_days": 7,
            "due_desc": "현장 투입 즉시 (7일 이내)",
            "hold_point": False,
            "audit_risk": "업무분장 공문 미발송 상태에서 분야별 감리원이 단독 검측 승인 시 절차 위반 지적",
            "checklist": [
                "공종별(건축/토목/기계/전기/안전 등) 주담당·부담당 지정",
                "검측 및 서류 검토 시 대결·전결 권한 명확화",
                "발주청 보고 및 시공사 서면 통보 완료 여부"
            ],
            "deliverable": "업무분장표, 직무권한 통보 공문",
            "status": "완료",
            "doc_no": "감리 제2026-002호"
        },
        {
            "id": "ADM-03",
            "domain": "1. 행정/조직",
            "phase": "Phase 1. 용역착수 즉시",
            "task": "건설사업관리 업무수행계획서 작성 및 제출",
            "law_short": "수행지침 제50조 제1항",
            "law_detail": "공사 특성 및 과업내용서를 반영하여 검측절차, 품질·안전·공정·환경관리 방법 및 기술지원기술인의 세부 수행계획이 포함된 업무수행계획서를 수립하여 발주청에 제출한다.",
            "owner": "책임감리원 / 기술지원",
            "anchor": "contract",
            "offset_days": 14,
            "due_desc": "용역착수 후 14일 이내",
            "hold_point": False,
            "audit_risk": "타 현장 계획서를 단순 복사하여 해당 현장 고유 공종이 누락되는 사례 빈번",
            "checklist": [
                "당해 현장 특수공종 및 중점품질·안전관리 대상 설정 여부",
                "기술지원기술인(비상주) 월별·공종별 현장점검 및 기술검토 일정 반영",
                "발주청 과업지시서 요구사항 100% 반영 여부"
            ],
            "deliverable": "건설사업관리 업무수행계획서",
            "status": "검토중",
            "doc_no": ""
        },
        {
            "id": "ADM-04",
            "domain": "1. 행정/조직",
            "phase": "Phase 3. 실착공 전 필수",
            "task": "시공사 착공신고서 적정성 검토 및 발주청 보고",
            "law_short": "수행지침 제50조 제2항",
            "law_detail": "시공자가 제출하는 착공신고서에 대하여 현장기술인 지정신고서, 공사공정예정표, 안전·환경·품질관리계획서, 착공전 사진, 손해보험증서 등의 구비 및 계약내용 부합 여부를 검토하여 발주청에 보고한다.",
            "owner": "책임감리원",
            "anchor": "start",
            "offset_days": -3,
            "due_desc": "실착공 전 (접수 후 즉시)",
            "hold_point": True,
            "audit_risk": "현장대리인·안전관리자·품질관리자 법정 자격 미달 또는 겸직 여부 미확인 상태에서 착공 수리",
            "checklist": [
                "현장대리인, 안전관리자, 품질관리자 선임계 및 법정 자격·경력 적정성",
                "노무비 구분관리 및 지급확인제 합의서, 건설근로자 퇴직공제 가입 확인",
                "착공 전 현장 사진, 직접시공계획서, 손해보험증서 구비 확인"
            ],
            "deliverable": "착공신고서 검토보고서",
            "status": "검토중",
            "doc_no": ""
        },
        {
            "id": "ADM-05",
            "domain": "1. 행정/조직",
            "phase": "Phase 1. 용역착수 즉시",
            "task": "감리사무실 설치 및 법정 비치장부·문서체계 세팅",
            "law_short": "수행지침 제50조 제4항~제8항",
            "law_detail": "현장 상주 사무실을 설치하고 문서접수/발송대장, 근무상황부, 건설사업관리일지, 품질시험계획 및 실적대장, 검측대장, 발생품정리부 등 법정 장부를 비치·관리한다.",
            "owner": "분야별감리원",
            "anchor": "contract",
            "offset_days": 10,
            "due_desc": "현장 투입 후 10일 이내",
            "hold_point": False,
            "audit_risk": "근무상황부 미작성 또는 기술지원기술인 현지방문 기록 누락 지적",
            "checklist": [
                "법정 필수 비치문서(검측대장, 시험대장, 민원처리부 등) 인덱스 구축",
                "감리원 근무상황부 비치 및 일일 서명 체계 확립",
                "설계도서 및 중요 문서 보관함 잠금장치·보안체계 확보"
            ],
            "deliverable": "현장 법정 비치서류 일체",
            "status": "완료",
            "doc_no": "내부비치 완료"
        },

        # [2. 설계/기술]
        {
            "id": "TEC-01",
            "domain": "2. 설계/기술",
            "phase": "Phase 2. 착수 직후 설계검토",
            "task": "설계도서(도면·시방서·내역서·계산서) 상호모순 및 오류 검토",
            "law_short": "시행령 제59조 제3항 / 수행지침 제51조 제1항",
            "law_detail": "설계도면, 시방서, 구조계산서, 산출내역서 등의 계약내용과 당해 공사의 조사설계보고서 등이 서로 일치하는지 여부와 누락·오류 등 불명확한 부분을 검토하여 발주청에 보고해야 한다.",
            "owner": "전 감리원 + 기술지원기술인",
            "anchor": "contract",
            "offset_days": 30,
            "due_desc": "착수 후 30일 이내 (본공종 전)",
            "hold_point": False,
            "audit_risk": "설계도서 검토 시 '기술지원기술인(비상주)'의 서명 및 세부 검토의견 누락 시 감사 필수 지적",
            "checklist": [
                "도면 치수/규격과 산출내역서 물량·단가 항목 상호 일치 여부",
                "일반시방서와 특기시방서 간 상충 조항 발췌",
                "분야별 기술지원기술인의 서명이 포함된 검토의견서 징구"
            ],
            "deliverable": "설계도서 검토보고서 (모순·누락 리스트)",
            "status": "검토중",
            "doc_no": ""
        },
        {
            "id": "TEC-02",
            "domain": "2. 설계/기술",
            "phase": "Phase 2. 착수 직후 설계검토",
            "task": "실제 현장여건 부합성 및 시공성(Constructability) 검토",
            "law_short": "시행령 제59조 제3항 / 수행지침 제51조 제1항",
            "law_detail": "설계도서가 현장 조건(지형, 지질, 지하수위, 인접 구조물, 진입도로 등)에 부합하는지 여부와 실제 시공 가능 여부(시공성)를 사전 검토하여 문제점을 발주청에 보고한다.",
            "owner": "책임/분야별 + 기술지원",
            "anchor": "contract",
            "offset_days": 30,
            "due_desc": "착수 후 30일 이내",
            "hold_point": False,
            "audit_risk": "지반조사보고서와 실제 굴착 조건 불일치 가능성을 사전에 검토하지 않아 공기 지연 초래",
            "checklist": [
                "토질·지반조사보고서상의 지하수위 및 암반선과 가시설 공법 적정성",
                "대형 장비(크레인, 항타기 등) 진입 동선 및 작업반경 확보 가능 여부",
                "인접 건축물·도로 이격거리 및 민원 유발 공법 변경 필요성 검토"
            ],
            "deliverable": "시공성 및 현장여건 검토보고서",
            "status": "미착수",
            "doc_no": ""
        },
        {
            "id": "TEC-03",
            "domain": "2. 설계/기술",
            "phase": "Phase 2. 착수 직후 설계검토",
            "task": "최신 설계기준(KDS)·표준시방서(KCS) 및 구조계산 적정성 검토",
            "law_short": "수행지침 제51조 제1항 제4호",
            "law_detail": "구조물의 규격 및 가설구조물 등이 최신 설계기준 및 표준시방서에 부합하는지 여부와 구조계산서의 적정성을 기술지원기술인과 합동으로 검토한다.",
            "owner": "기술지원기술인 / 분야별감리원",
            "anchor": "contract",
            "offset_days": 30,
            "due_desc": "착수 후 30일 이내",
            "hold_point": False,
            "audit_risk": "설계 시점 이후 개정된 내진설계기준·화재안전기준 미반영 상태로 시공 진행",
            "checklist": [
                "설계 완료 이후 개정된 최신 KDS/KCS 기준 대조",
                "주요 구조부 배근 상세 및 정착·이음 길이 적정성 확인",
                "흙막이·동바리 등 주요 가설구조물 구조계산 누락 여부 확인"
            ],
            "deliverable": "최신 기준 대조표 및 구조검토 의견서",
            "status": "미착수",
            "doc_no": ""
        },
        {
            "id": "TEC-04",
            "domain": "2. 설계/기술",
            "phase": "Phase 2. 착수 직후 설계검토",
            "task": "인허가 조건 및 각종 영향평가 협의내용 설계반영 확인",
            "law_short": "수행지침 제51조 제2항",
            "law_detail": "건축허가·사업승인 조건, 환경·교통·재해영향평가 협의내용, 유관기관 협의조건 등이 설계도서 및 내역서에 누락 없이 반영되었는지 확인한다.",
            "owner": "책임감리원 / 분야별감리원",
            "anchor": "contract",
            "offset_days": 20,
            "due_desc": "착수 후 20일 이내",
            "hold_point": False,
            "audit_risk": "인허가 조건(예: 착공 전 문화재 입회, 방음벽 선시공 조건 등) 누락으로 행정처분 발생",
            "checklist": [
                "사업승인/건축허가서 부관(조건) 사항 전수 리스트업",
                "착공 전 이행 조건, 시공 중 이행 조건, 준공 전 이행 조건 분류",
                "미반영 항목 발견 시 발주청 실정보고 및 설계변경 리스트 등록"
            ],
            "deliverable": "인허가 조건 이행관리 마스터표",
            "status": "검토중",
            "doc_no": ""
        },

        # [3. 현장/측량]
        {
            "id": "SIT-01",
            "domain": "3. 현장/측량",
            "phase": "Phase 2. 착수 직후 설계검토",
            "task": "측량기준점(도근점·수준점) 인수 및 보호조치 지시",
            "law_short": "수행지침 제52조 제1항",
            "law_detail": "발주청이 설치한 측량기준점을 시공자와 합동으로 현장 확인 후 인수하고, 공사 준공 시까지 훼손되지 않도록 보호조치를 지시하여야 한다.",
            "owner": "분야별감리원(토목/건축)",
            "anchor": "start",
            "offset_days": -5,
            "due_desc": "확인측량 착수 전",
            "hold_point": False,
            "audit_risk": "기준점 망실 및 이동에도 인계인수 기록이 없어 구조물 좌표 오차 책임 소재 불분명",
            "checklist": [
                "설계 시 설치된 도근점(CP) 및 수준점(BM) 현장 위치 합동 확인",
                "기준점 주위 보호울타리 및 식별 표지판 설치 지시",
                "공사 구역 내 훼손 우려 기준점의 안전지대 인출(이설) 측량 실시"
            ],
            "deliverable": "측량기준점 인계인수서 및 현황사진",
            "status": "완료",
            "doc_no": "감리 제2026-005호"
        },
        {
            "id": "SIT-02",
            "domain": "3. 현장/측량",
            "phase": "Phase 3. 실착공 전 필수",
            "task": "착공 확인측량 입회 및 측량성과도 적정성 검토·보고",
            "law_short": "수행지침 제52조 제2항~제5항",
            "law_detail": "시공자로 하여금 공사착수 전 확인측량(용지경계, 원지반고, 종·횡단 등)을 실시하게 하고 입회하며, 설계도서와 상이할 경우 측량성과도를 검토하여 발주청에 보고해야 한다.",
            "owner": "분야별감리원(토목/건축)",
            "anchor": "start",
            "offset_days": -1,
            "due_desc": "실착공(굴착) 전 완료",
            "hold_point": True,
            "audit_risk": "원지반 확인측량 없이 굴착 착수 후 사후에 토공량(절·성토량) 정산 분쟁 발생 시 감리 문책",
            "checklist": [
                "대지경계선(경계복원측량) 및 인접 대지 침범 여부 확인",
                "원지반 종·횡단 측량 입회 및 설계 지반고(GL)와의 차이 물량 산출",
                "확인측량 결과보고서 접수 후 7일 이내 적정성 검토 및 발주청 보고"
            ],
            "deliverable": "확인측량 성과 검토보고서",
            "status": "검토중",
            "doc_no": ""
        },
        {
            "id": "SIT-03",
            "domain": "3. 현장/측량",
            "phase": "Phase 4. 착공 초기 현장셋업",
            "task": "공사가설시설물 설치계획서 검토 및 승인",
            "law_short": "수행지침 제54조",
            "law_detail": "공사착공과 동시에 시공자로부터 가설시설물(현장사무소, 시험실, 창고, 가설울타리, 세륜시설, 안내표지판 등) 면적 및 위치 평면도를 제출받아 검토·승인하고 발주청에 보고한다.",
            "owner": "분야별감리원",
            "anchor": "start",
            "offset_days": 5,
            "due_desc": "착공 직후 (설치 전)",
            "hold_point": False,
            "audit_risk": "가설울타리·세륜기 도로점용 허가 미취득 또는 가설건축물 축조신고 누락 상태로 설치",
            "checklist": [
                "가설건축물 축조신고 및 도로점용 허가 완료 여부 확인",
                "공사안내표지판(발주청, 시공사, 감리자, 공사기간 명시) 규격 확인",
                "세륜·세차시설 및 가설울타리(방음벽) 설치 위치 적정성 검토"
            ],
            "deliverable": "가설시설물 설치계획 승인서",
            "status": "보완지시",
            "doc_no": "감리 제2026-008호"
        },
        {
            "id": "SIT-04",
            "domain": "3. 현장/측량",
            "phase": "Phase 3. 실착공 전 필수",
            "task": "착공 전 현장 원본 사진 및 영상 촬영·보관 확인",
            "law_short": "수행지침 제55조 제2항",
            "law_detail": "전 공구 및 인접 구조물에 대하여 착공 전 원상태의 사진 및 동영상을 촬영하여 보관하도록 시공자에게 지시하고 이를 확인하여야 한다.",
            "owner": "분야별감리원",
            "anchor": "start",
            "offset_days": -2,
            "due_desc": "실착공(부지정리) 전",
            "hold_point": True,
            "audit_risk": "착공 전 인접 건물 균열·도로 파손 원본 사진 미확보로 공사 중 민원 손해배상 분쟁 시 대응 불가",
            "checklist": [
                "부지 전체 전경(동·서·남·북 방향 및 항공/고소 촬영) 원본 확보",
                "인접 건축물 외벽 균열·담장·주변 도로 포장 상태 사전 촬영(날짜 표시)",
                "지장물 및 수목 현황 촬영 데이터 백업 보관"
            ],
            "deliverable": "착공 전 현황 사진첩 및 동영상 원본",
            "status": "완료",
            "doc_no": "감리 제2026-004호"
        },

        # [4. 품질관리]
        {
            "id": "QMS-01",
            "domain": "4. 품질관리",
            "phase": "Phase 3. 실착공 전 필수",
            "task": "품질관리(또는 품질시험)계획서 적정성 검토 및 발주청 보고",
            "law_short": "건진법 제55조 / 시행령 제89조·제90조 / 지침 제60조",
            "law_detail": "시공자는 건설공사를 착공하기 전에 품질관리계획 또는 품질시험계획을 수립하여 건설사업관리용역사업자의 검토·확인을 받아 발주청에 제출하여 승인을 받아야 한다.",
            "owner": "책임감리원 / 품질담당",
            "anchor": "start",
            "offset_days": -5,
            "due_desc": "실착공 전 발주청 승인 필수",
            "hold_point": True,
            "audit_risk": "품질관리계획서 발주청 미승인 상태에서 레미콘 타설·토공 다짐 등 본공사 착수 시 형사처벌·벌점 대상",
            "checklist": [
                "대상 공사 규모에 따른 품질관리계획(KS Q ISO 9001 기반) 적정 수립 여부",
                "공종별·자재별 법정 품질시험 종목·빈도·방법 누락 여부 대조",
                "부적합품(NCR) 관리절차 및 시정조치 프로세스 적정성 심사"
            ],
            "deliverable": "품질관리계획서 검토의견서 및 승인문서",
            "status": "검토중",
            "doc_no": ""
        },
        {
            "id": "QMS-02",
            "domain": "4. 품질관리",
            "phase": "Phase 3. 실착공 전 필수",
            "task": "법정 품질관리자 적정 배치(겸직금지) 및 현장 시험실·교정 점검",
            "law_short": "시행령 제91조 / 규칙 제50조 별표5",
            "law_detail": "공사 규모에 맞는 등급·인원의 건설기술인을 품질관리자로 배치하였는지 확인하고, 품질관리자가 타 업무(공사·공무·안전 등)를 겸직하지 않도록 통제하며 시험장비 교정 상태를 확인한다.",
            "owner": "품질담당 감리원",
            "anchor": "start",
            "offset_days": -2,
            "due_desc": "실착공 전",
            "hold_point": True,
            "audit_risk": "국토부 점검 1순위: 품질관리자를 공사팀·공무팀 업무에 겸직시키거나 시험장비 교정기한 도과 방치",
            "checklist": [
                "공사규모별 법정 품질관리자 인원수 및 등급(특급/고급/중급) 충족 확인",
                "시공사 조직도상 품질관리자의 독립성 및 타 업무 겸직 금지 서약 확인",
                "현장 시험실 규격 확보 및 계측·시험장비 국가교정성적서 유효기간 확인"
            ],
            "deliverable": "품질관리자 자격·배치 및 시험실 점검표",
            "status": "검토중",
            "doc_no": ""
        },
        {
            "id": "QMS-03",
            "domain": "4. 품질관리",
            "phase": "Phase 4. 착공 초기 현장셋업",
            "task": "현장 맞춤형 검측절차서 및 공종별 검측체크리스트 수립·확정",
            "law_short": "수행지침 제10조, 제56조",
            "law_detail": "본격적인 시공에 앞서 시공자와 협의하여 공종별 검측업무 수행기준, 필수 검측점(Hold Point), 검측체크리스트 및 주요 자재 공급원 승인 대상 목록을 확정한다.",
            "owner": "전 분야별 감리원",
            "anchor": "start",
            "offset_days": 7,
            "due_desc": "본 공종 착수 전",
            "hold_point": False,
            "audit_risk": "표준 체크리스트를 현장 설계수치로 변환하지 않고 '적정/부적정'만 표기하여 형식적 검측 지적",
            "checklist": [
                "당해 현장 도면·시방서 기준치가 기입된 공종별 검측체크리스트 확정",
                "주요 자재(레미콘, 철근, 아스콘 등) 공급원 승인 요청 기한(사용 15일 전 등) 고지",
                "매몰 부위(기초, 지하외벽 방수 등) 필수 Hold Point 지정"
            ],
            "deliverable": "공종별 검측체크리스트 및 자재승인 대상 목록",
            "status": "미착수",
            "doc_no": ""
        },

        # [5. 안전/환경]
        {
            "id": "SAF-01",
            "domain": "5. 안전/환경",
            "phase": "Phase 3. 실착공 전 필수",
            "task": "건진법 안전관리계획서 검토·확인 및 발주청 승인 확인",
            "law_short": "건진법 제62조 / 시행령 제98조 / 지침 제65조",
            "law_detail": "시공자는 안전관리계획을 수립하여 건설사업관리기술인의 검토·확인을 받아 착공 전에 발주청에 제출·승인받아야 한다. (국토안전관리원 등 검토기관 적정 판정 필수)",
            "owner": "책임감리원 / 안전담당",
            "anchor": "start",
            "offset_days": -7,
            "due_desc": "실착공 전 절대 필수",
            "hold_point": True,
            "audit_risk": "안전관리계획서 미승인 또는 '조건부 적정' 보완 미이행 상태에서 실착공 시 즉각 고발·벌점 부과",
            "checklist": [
                "총괄안전관리계획서 및 대상 공종별 세부안전관리계획 포함 여부",
                "국토안전관리원(1·2종 시설물) 또는 안전진단전문기관 검토결과 '적정/조건부적정' 확인",
                "안전관리비(건진법 안전관리비 + 산안법 산업안전보건관리비) 계상 및 사용계획 검토"
            ],
            "deliverable": "안전관리계획서 검토의견서 및 발주청 승인서",
            "status": "보완지시",
            "doc_no": "감리 제2026-006호"
        },
        {
            "id": "SAF-02",
            "domain": "5. 안전/환경",
            "phase": "Phase 4. 착공 초기 현장셋업",
            "task": "가설구조물 구조적 안전성(관계전문가 확인) 대상 공종 분류",
            "law_short": "건진법 제62조의2 / 시행령 제101조의2",
            "law_detail": "높이 31m 이상 비계, 5m 이상 거푸집·동바리, 터널 지보공, 높이 2m 이상 흙막이 지보공 등 관계전문가(구조기술사 등)의 구조적 안전성 확인이 필요한 가설구조물을 사전 분류하여 관리한다.",
            "owner": "안전담당 / 분야별감리원",
            "anchor": "start",
            "offset_days": 10,
            "due_desc": "착공 초기 리스트업 (시공 전 확인)",
            "hold_point": False,
            "audit_risk": "시행령 제101조의2 대상 가설구조물을 관계전문가 서명날인 없이 시공 승인 시 중대 처벌",
            "checklist": [
                "현장 내 시행령 제101조의2 해당 가설구조물(비계, 동바리, 흙막이, 브라켓 등) 전수 추출",
                "공종별 시공 전 관계전문가(해당 분야 기술사) 구조검토서 제출 일정 확정",
                "가설기자재 안전인증(KCs) 및 품질시험 대상 품목 리스트업"
            ],
            "deliverable": "가설구조물 구조안전성 확인 대상 관리대장",
            "status": "완료",
            "doc_no": "감리 제2026-007호"
        },
        {
            "id": "SAF-03",
            "domain": "5. 안전/환경",
            "phase": "Phase 3. 실착공 전 필수",
            "task": "환경관리 법정 인허가(비산먼지·특정공사·폐기물) 신고 이행 확인",
            "law_short": "시행령 제59조 제3항 / 수행지침 제66조",
            "law_detail": "실착공 전 대기환경보전법(비산먼지 발생사업 신고), 소음·진동관리법(특정공사 사전신고), 건설폐기물 처리계획 신고 등이 적법하게 완료되었는지 확인한다.",
            "owner": "환경/분야별 감리원",
            "anchor": "start",
            "offset_days": -3,
            "due_desc": "실착공 3일 전까지",
            "hold_point": True,
            "audit_risk": "비산먼지 및 특정공사 사전신고 필증 교부 전 장비 투입·철거·굴착 시 지자체 고발 및 과태료",
            "checklist": [
                "비산먼지 발생사업 신고필증 및 특정공사 사전신고필증 사본 징구",
                "건설폐기물 배출자 신고 및 올바로(Allbaro) 시스템 등록 확인",
                "환경보전비 산출 및 사용계획서 적정성 검토"
            ],
            "deliverable": "환경 법정신고 필증 확인서",
            "status": "완료",
            "doc_no": "감리 제2026-003호"
        },

        # [6. 공정/하도급/대외]
        {
            "id": "PRC-01",
            "domain": "6. 공정/하도급",
            "phase": "Phase 4. 착공 초기 현장셋업",
            "task": "공사예정공정표(CP 명시) 및 종합시공계획서 검토·승인",
            "law_short": "시행령 제59조 제3항 / 수행지침 제61조·제64조",
            "law_detail": "시공자로부터 전체 공사예정공정표(주공정선 표시)와 종합시공계획서를 제출받아 공기의 적정성, 인력·장비·자재 동원계획을 검토하여 승인한다.",
            "owner": "책임감리원 / 공정담당",
            "anchor": "start",
            "offset_days": 14,
            "due_desc": "착공 후 14일 이내 (공종 30일 전)",
            "hold_point": False,
            "audit_risk": "주공정선(Critical Path)이 없는 단순 막대그래프 공정표를 승인하여 추후 공기연장 간접비 산정 불가",
            "checklist": [
                "네트워크 공정표 상 주공정선(Critical Path) 및 주요 마일스톤 명확성 확인",
                "동절기·혹서기·장마철 등 공사불능일수 반영 적정성 검토",
                "월별 기성 산정 기준선(Baseline)과의 일치성 확인"
            ],
            "deliverable": "공사예정공정표 및 종합시공계획 승인서",
            "status": "검토중",
            "doc_no": ""
        },
        {
            "id": "PRC-02",
            "domain": "6. 공정/하도급",
            "phase": "Phase 4. 착공 초기 현장셋업",
            "task": "초기 공종(토공·가시설 등) 하도급 계약 적정성 검토 및 보고",
            "law_short": "시행령 제59조 제3항 / 수행지침 제53조",
            "law_detail": "시공자가 하도급 계약 통지 또는 승인 요청 시 하수급인의 자격, 저가하도급(하도급률 82% 미만 등) 여부, 하도급대금 지급보증서 교부 여부 등을 검토하여 7일 이내에 발주청에 보고한다.",
            "owner": "책임감리원 / 공무담당",
            "anchor": "start",
            "offset_days": 15,
            "due_desc": "하도급 통지 접수 후 7일 이내",
            "hold_point": False,
            "audit_risk": "하도급 통지 전 하수급인의 현장 선투입(불법 사전시공) 방치 또는 대금지급보증서 미확인",
            "checklist": [
                "하수급인 전문건설업 등록증 및 시공능력평가액 적정성 확인",
                "하도급률(82% 미만 및 발주청 예정가격 대비 60%/64% 미만 여부) 적정성 심사",
                "하도급대금 지급보증서 발급 및 건설기계대여대금 지급보증 확인"
            ],
            "deliverable": "하도급 적정성 검토보고서 (KISCON 확인)",
            "status": "미착수",
            "doc_no": ""
        },
        {
            "id": "PRC-03",
            "domain": "6. 공정/하도급",
            "phase": "Phase 3. 실착공 전 필수",
            "task": "유관기관(지하매설물) 합동회의 개최 및 지장물 이설 협의",
            "law_short": "수행지침 제55조 제1항",
            "law_detail": "발주청 및 시공자와 협조하여 지하매설물(가스, 상하수도, 전력, 통신 등) 관리기관과 합동회의를 개최하고 미철거 지장물 이설 일정을 확정한다.",
            "owner": "책임감리원 / 토목담당",
            "anchor": "start",
            "offset_days": -2,
            "due_desc": "굴착 착수 전 필수",
            "hold_point": True,
            "audit_risk": "유관기관 입회 및 줄파기(인력 시험굴착) 없이 장비 굴착을 허용하여 가스관·통신선 파손 사고 발생",
            "checklist": [
                "상하수도, 도시가스, 한전, 통신사 등 유관기관 담당자 합동회의 개최",
                "지하매설물 위치 표시 및 기계굴착 전 인력 줄파기(시험굴착) 계획 수립",
                "지장물 이설 지연 우려 구간 공정표 반영 및 발주청 보고"
            ],
            "deliverable": "유관기관 합동회의록 및 지장물 관리대장",
            "status": "완료",
            "doc_no": "감리 제2026-009호"
        }
    ]

if "tasks_df" not in st.session_state:
    st.session_state.tasks_df = pd.DataFrame(get_initial_tasks())

# -----------------------------------------------------------------------------
# 3. 사이드바: 현장 기본정보 및 기준일(D-Day) 설정
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🏗️ 감리단 착수 설정")
    st.caption("건진법 감독권한대행 건설사업관리 기준")
    
    project_name = st.text_input("사업명 (현장명)", value="OO지구 공공건축물 건립공사 건설사업관리")
    client_name = st.text_input("발주청", value="OO시청 건설본부")
    cm_company = st.text_input("건설사업관리용역사업자", value="PEMCO 엔지니어링")
    
    st.divider()
    st.markdown("### 📅 기준 일자 입력 (자동 기한 산정)")
    contract_date = st.date_input("1. 감리용역 착수일 (투입일)", value=datetime.today() - timedelta(days=10))
    start_date = st.date_input("2. 공사 실착공(굴착) 예정일", value=datetime.today() + timedelta(days=5))
    
    st.divider()
    st.markdown("### 🔍 필터 설정")
    domains = ["전체"] + sorted(st.session_state.tasks_df["domain"].unique().tolist())
    selected_domain = st.selectbox("업무 도메인 필터", domains)
    
    status_options = ["전체", "미착수", "검토중", "보완지시", "완료"]
    selected_status = st.selectbox("진행상태 필터", status_options)
    
    only_hold = st.checkbox("🚨 실착공 전 필수(Hold Point)만 보기", value=False)
    
    st.divider()
    if st.button("🔄 초기 데이터로 리셋", use_container_width=True):
        st.session_state.tasks_df = pd.DataFrame(get_initial_tasks())
        st.rerun()

# -----------------------------------------------------------------------------
# 4. 날짜 계산 및 D-Day 산출 엔진
# -----------------------------------------------------------------------------
df = st.session_state.tasks_df.copy()

def calc_due_date(row):
    base = contract_date if row["anchor"] == "contract" else start_date
    return base + timedelta(days=int(row["offset_days"]))

df["법정마감일"] = df.apply(calc_due_date, axis=1)
df["D_Day_Num"] = df["법정마감일"].apply(lambda d: (d - datetime.today().date()).days)

def format_dday(row):
    if row["status"] == "완료":
        return "✅ 완료"
    d = row["D_Day_Num"]
    if d < 0:
        return f"🔥 지연 (D+{abs(d)})"
    elif d == 0:
        return "⚠️ 오늘마감 (D-Day)"
    else:
        return f"⏳ D-{d}"

df["기한상태"] = df.apply(format_dday, axis=1)

# -----------------------------------------------------------------------------
# 5. 메인 대시보드 화면 구성
# -----------------------------------------------------------------------------
st.markdown('<div class="main-header">🏗️ 건진법 감독권한대행 감리자 최초투입(착수단계) 관제 시스템</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sub-header"><b>현장명:</b> {project_name} &nbsp;|&nbsp; <b>발주청:</b> {client_name} &nbsp;|&nbsp; <b>감리사:</b> {cm_company}</div>',
    unsafe_allow_html=True
)

total_cnt = len(df)
done_cnt = len(df[df["status"] == "완료"])
progress_pct = int((done_cnt / total_cnt) * 100)

hold_df = df[df["hold_point"] == True]
hold_unfinished = len(hold_df[hold_df["status"] != "완료"])

overdue_cnt = len(df[(df["status"] != "완료") & (df["D_Day_Num"] < 0)])
urgent_cnt = len(df[(df["status"] != "완료") & (df["D_Day_Num"] >= 0) & (df["D_Day_Num"] <= 3)])

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("착수단계 전체 법정업무", f"{done_cnt} / {total_cnt} 건", f"이행률 {progress_pct}%")
with col2:
    st.metric(
        "🚨 실착공 전 필수(Hold Point) 미결",
        f"{hold_unfinished} 건",
        "실착공 승인 가능" if hold_unfinished == 0 else "미승인 시 실착공 절대불가",
        delta_color="normal" if hold_unfinished == 0 else "inverse"
    )
with col3:
    st.metric(
        "⏰ 기한 지연 / 임박(3일내)",
        f"지연 {overdue_cnt}건 / 임박 {urgent_cnt}건",
        "일정 정상" if (overdue_cnt + urgent_cnt) == 0 else "즉시 독촉 필요",
        delta_color="normal" if (overdue_cnt + urgent_cnt) == 0 else "inverse"
    )
with col4:
    days_to_start = (start_date - datetime.today().date()).days
    start_str = f"D-{days_to_start}" if days_to_start >= 0 else f"착공 후 +{abs(days_to_start)}일"
    st.metric("실착공(굴착) 예정일", start_date.strftime("%Y-%m-%d"), start_str)

if hold_unfinished > 0:
    unfinished_names = ", ".join(hold_df[hold_df["status"] != "완료"]["id"].tolist())
    st.error(
        f"**[법정 Hold Point 경고]** 현재 실착공 전 필수 승인·확인 사항 중 **{hold_unfinished}건({unfinished_names})**이 미완료 상태입니다. "
        f"건진법 제55조(품질관리계획) 및 제62조(안전관리계획) 등에 따라 해당 업무 완료 전에는 물리적 실착공(굴착 등)을 지시하거나 승인할 수 없습니다."
    )
else:
    st.success("**[실착공 조건 충족]** 모든 실착공 전 필수 법정업무(Hold Point)가 완료되었습니다.")

st.progress(progress_pct / 100)

# 필터 적용
filtered_df = df.copy()
if selected_domain != "전체":
    filtered_df = filtered_df[filtered_df["domain"] == selected_domain]
if selected_status != "전체":
    filtered_df = filtered_df[filtered_df["status"] == selected_status]
if only_hold:
    filtered_df = filtered_df[filtered_df["hold_point"] == True]

# -----------------------------------------------------------------------------
# 6. 탭 구성 (관제보드, 상세체크리스트, 법령체계, 보고서 다운로드)
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 1. 통합 법정업무 관제 보드 (실시간 편집)",
    "🔍 2. 조문별 상세 체크리스트 & 감사 리스크",
    "🏛️ 3. 법령 체계 및 시점별 프로세스 맵",
    "📥 4. 점검 보고서 및 데이터 내보내기"
])

with tab1:
    st.markdown("#### 📌 착수단계 20대 필수 법정업무 현황판")
    st.caption("표 안의 **'진행상태'**와 **'근거문서번호'** 셀을 더블클릭하여 현장에서 즉시 수정할 수 있습니다.")
    
    display_cols = [
        "id", "domain", "phase", "task", "law_short",
        "hold_point", "due_desc", "법정마감일", "기한상태", "status", "doc_no", "owner"
    ]
    
    edited_df = st.data_editor(
        filtered_df[display_cols],
        column_config={
            "id": st.column_config.TextColumn("코드", width="small", disabled=True),
            "domain": st.column_config.TextColumn("도메인", width="small", disabled=True),
            "phase": st.column_config.TextColumn("수행 시점", width="medium", disabled=True),
            "task": st.column_config.TextColumn("법정 필수 업무명", width="large", disabled=True),
            "law_short": st.column_config.TextColumn("법령/지침 근거", width="medium", disabled=True),
            "hold_point": st.column_config.CheckboxColumn("실착공 필수(Hold)", width="small", disabled=True),
            "due_desc": st.column_config.TextColumn("기한 기준", width="medium", disabled=True),
            "법정마감일": st.column_config.DateColumn("목표 마감일", width="small", disabled=True),
            "기한상태": st.column_config.TextColumn("D-Day 상태", width="small", disabled=True),
            "status": st.column_config.SelectboxColumn(
                "진행상태 (수정가능)",
                options=["미착수", "검토중", "보완지시", "완료"],
                required=True,
                width="small"
            ),
            "doc_no": st.column_config.TextColumn("근거문서번호 (수정가능)", width="medium"),
            "owner": st.column_config.TextColumn("담당자", width="medium", disabled=True),
        },
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key="main_editor"
    )
    
    if not edited_df[["id", "status", "doc_no"]].equals(filtered_df[["id", "status", "doc_no"]]):
        for _, row in edited_df.iterrows():
            idx = st.session_state.tasks_df.index[st.session_state.tasks_df["id"] == row["id"]].tolist()[0]
            st.session_state.tasks_df.at[idx, "status"] = row["status"]
            st.session_state.tasks_df.at[idx, "doc_no"] = row["doc_no"]
        st.rerun()

    st.markdown("---")
    st.markdown("##### 📊 6대 도메인별 이행 현황 요약")
    summary_df = df.groupby(["domain", "status"]).size().unstack(fill_value=0)
    for s in ["완료", "검토중", "보완지시", "미착수"]:
        if s not in summary_df.columns:
            summary_df[s] = 0
    summary_df = summary_df[["완료", "검토중", "보완지시", "미착수"]]
    st.bar_chart(summary_df)

with tab2:
    st.markdown("#### 🔍 업무별 법령 조문 원문 · 실무 체크리스트 · 감사 지적 포인트")
    for _, row in filtered_df.iterrows():
        badge = "🚨 [실착공 Hold Point]" if row["hold_point"] else "📌 [일반 법정업무]"
