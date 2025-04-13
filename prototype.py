import streamlit as st
import pandas as pd
import time
import os
from datetime import datetime

# --- 초기 세팅 ---
if 'page' not in st.session_state:
    st.session_state.page = 'intro'  # 처음에는 intro 페이지로 시작
if 'trust' not in st.session_state:
    st.session_state.trust = {}
if 'selected_action' not in st.session_state:
    st.session_state.selected_action = []
if 'task' not in st.session_state:
    st.session_state.task = None
if 'timer_start_time' not in st.session_state:
    st.session_state.timer_start_time = None

# --- Task별 데이터 ---
tasks = {
    'Task 1: 기본 대응': {
        'situation': '길거리에서 한 사람이 쓰러졌습니다!',
        'timer': 30,  # 45초에서 30초로 수정
        'cards': {
            '119 신고 매뉴얼': {'summary': '긴급 상황 발생 시, 즉시 119에 전화하여 상황을 설명하고 안내를 받으세요.', 'source': '소방청 공식 매뉴얼'},
            '물 뿌리기 요령': {'summary': '더운 날에는 쓰러진 사람에게 물을 뿌리면 회복될 수 있다는 방법입니다.', 'source': '출처 불명 블로그'},
            '응급처치 매뉴얼 (심폐소생술)': {'summary': '호흡과 맥박이 없으면 즉시 심폐소생술을 시행해야 합니다.', 'source': '응급의료포털'}
        },
        'actions': ['119 신고', '물 뿌리기', '그냥 두기'],
        'correct_info': ['119 신고 매뉴얼', '응급처치 매뉴얼 (심폐소생술)']  # 피드백용 정답 정보
    },
    'Task 2: 정보 충돌 대처': {
        'situation': '교통사고 현장에서 운전자가 차량 안에 갇혀있습니다.',
        'timer': 30,  # 45초에서 30초로 수정
        'cards': {
            '도로교통공단 사고 대응 가이드': {'summary': '부상자가 있을 경우, 차량 이동 없이 119를 기다려야 합니다.', 'source': '도로교통공단'},
            '유튜브 사고 처리 영상': {'summary': '사고 현장에서는 차량을 빠르게 치워야 한다고 주장합니다.', 'source': '개인 유튜브 채널'},
            '목격자 발언': {'summary': '"차를 옮겨야 합니다!"라는 현장 목격자의 조언입니다.', 'source': '현장 목격자'},
            '보험사 매뉴얼 발췌': {'summary': '부상자가 있을 경우 차량을 옮기면 법적 문제가 될 수 있습니다.', 'source': '보험사 공식 가이드'}
        },
        'actions': ['차량 이동', '부상자 상태 확인 후 대기', '그냥 기다리기'],
        'correct_info': ['차량 이동', '부상자 상태 확인 후 대기']  # 피드백용 정답 정보
    },
    'Task 3: 복합 상황 대응': {
        'situation': '마트 안에서 한 사람이 쓰러졌습니다. (심장마비인지 저혈당인지 알 수 없음)',
        'timer': 30,  # 45초에서 30초로 수정
        'cards': {
            'AED 사용법 (공식 의료 매뉴얼)': {'summary': '심장마비 의심 시 즉시 AED를 적용하고, 지침에 따라 사용하세요.', 'source': '의료기관 매뉴얼'},
            '심장마비 응급처치 요령': {'summary': '의식과 호흡이 없으면 즉시 심폐소생술과 AED 사용이 필요합니다.', 'source': '응급의료포털'},
            '저혈당 대처법': {'summary': '의식이 있는 저혈당 환자에게는 당분을 섭취시켜야 합니다.', 'source': '대한당뇨병학회'},
            'SNS 루머': {'summary': 'AED를 잘못 사용하면 더 큰 사고가 난다는 주장이 퍼지고 있습니다.', 'source': 'SNS 게시글 (출처 불명)'},
            '마트 직원 발언': {'summary': '"AED는 위험할 수 있으니 사용하지 마세요!"라고 주장합니다.', 'source': '마트 직원 발언'},
            '응급의료포털 링크': {'summary': '심장마비 상황에서 AED를 사용하면 생존 확률이 크게 올라갑니다.', 'source': '응급의료포털'}
        },
        'actions': ['119 신고', 'AED 사용', '물 마시게 하기', '아무것도 하지 않기'],
        'correct_info': ['119 신고', 'AED 사용']  # 피드백용 정답 정보
    }
}

# --- 데이터 저장 함수 수정 ---
def save_data():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 세션 스토리지에 저장
    if 'saved_responses' not in st.session_state:
        st.session_state.saved_responses = []
    
    data = {
        'Timestamp': timestamp,
        'Task': st.session_state.task,
        'Trust_Responses': st.session_state.trust,
        'Selected_Action': st.session_state.selected_action
    }
    
    # 세션에 데이터 저장
    st.session_state.saved_responses.append(data)
    
    # 선택적: 데이터 다운로드 버튼 제공
    if st.session_state.page == 'feedback':
        if len(st.session_state.saved_responses) > 0:
            df = pd.DataFrame(st.session_state.saved_responses)
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 학습 기록 다운로드",
                data=csv,
                file_name=f"emergency_responses_{timestamp}.csv",
                mime="text/csv"
            )

# --- 화면 표시 함수 ---
def show_intro():
    st.title("🚑 응급 상황 대응 학습 프로그램")
    
    # 헤더 이미지
    st.image("images/image.jpg", use_container_width=True)
    
    # 프로그램 소개
    st.markdown("""
    ## 응급 상황, 당신의 판단이 생명을 좌우합니다
    
    이 프로그램은 응급 상황에서의 올바른 의사결정 능력을 향상시키기 위한 학습 도구입니다.
    
    ### 📝 여러분이 할 일
    
    1. **응급 상황 고르기**

       ➡️ 아래에서 학습하고 싶은 응급 상황을 선택하세요
       ➡️ '학습 시작하기' 버튼을 눌러 시작하세요
    
    2. **정보 확인과 대응 결정하기 (30초)**

       ➡️ 각 정보 카드를 클릭해서 내용을 읽으세요
       ➡️ 정보가 신뢰할만한지 판단하세요
       ➡️ 읽으면서 대응 방법도 함께 고민하세요
       ➡️ 30초 안에 선택을 완료하세요 (Task 3에서는 여러 개의 대응을 선택할 수 있어요)
    
    3. **결과 보고 다시 도전하기**

       ➡️ 피드백을 확인하세요
       ➡️ 같은 상황을 다시 연습할지 선택하세요
       ➡️ 다른 상황도 도전해보세요
    """)

    # 태스크 선택 섹션
    st.markdown("---")
    st.markdown("### 🎯 학습할 태스크 선택")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_task = st.radio(
            "응급 상황을 선택하세요:",
            list(tasks.keys()),
            format_func=lambda x: f"{x.split(':')[0]}\n{x.split(':')[1]}"
        )
    
    # 선택된 태스크 설명
    st.markdown("#### 선택한 상황 설명")
    st.info(tasks[selected_task]['situation'])
    
    # 시작하기 버튼
    st.markdown("---")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("학습 시작하기 👉", use_container_width=True):
            st.session_state.task = selected_task
            st.session_state.page = 'task'
            st.session_state.timer_start_time = time.time()
            st.rerun()

    # 하단 설명
    st.markdown("---")
    st.caption("© 2024 응급 상황 대응 학습 프로그램 | 문의: emergency@example.com")

def show_task():
    if st.session_state.task is None:
        st.warning("사이드바에서 Task를 먼저 선택해주세요.")
        st.stop()

    st.title("정보 탐색 및 행동 결정")

    # 타이머 컨테이너 생성
    timer_container = st.empty()
    
    # 상황 설명
    st.subheader(tasks[st.session_state.task]['situation'])

    # 정보 카드들
    cards = tasks[st.session_state.task]['cards']
    for title, content in cards.items():
        with st.expander(f"📄 {title}"):
            st.write(f"**요약:** {content['summary']}")
            st.caption(f"출처: {content['source']}")
            trust = st.radio(f"'{title}' 정보를 신뢰합니까?", 
                           ('선택하지 않음', '신뢰한다', '신뢰하지 않는다'),  # 순서 변경 및 기본값 설정
                           index=0,  # 첫 번째 옵션('선택하지 않음')을 기본값으로 설정
                           key=f"trust_{title}")
            st.session_state.trust[title] = trust

    st.divider()

    # 행동 선택
    actions = tasks[st.session_state.task]['actions']
    if st.session_state.task == 'Task 3: 복합 상황 대응':
        st.markdown("**:red[여러 행동을 동시에 선택할 수 있습니다]**")
        action = st.multiselect("당신의 선택:", actions)
    else:
        action = [st.radio("당신의 선택:", actions)]

    if st.button("선택 완료", use_container_width=True):
        st.session_state.selected_action = action
        save_data()
        st.session_state.page = 'feedback'
        st.rerun()

    # 타이머 실시간 업데이트
    total_time = tasks[st.session_state.task]['timer']
    while True:
        elapsed_time = int(time.time() - st.session_state.timer_start_time)
        remaining_time = max(0, total_time - elapsed_time)
        progress = remaining_time / total_time

        # 타이머 표시 업데이트
        with timer_container:
            col1, col2 = st.columns([1, 4])
            with col1:
                # 시간을 큰 폰트로 표시
                st.markdown(
                    f"<h1 style='text-align: center; color: red; font-size: 40px;'>{remaining_time}</h1>",
                    unsafe_allow_html=True
                )
            with col2:
                # 프로그레스 바를 빨간색으로 설정
                st.markdown(
                    """
                    <style>
                    .stProgress > div > div {
                        background-color: red;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                st.progress(progress)

        if remaining_time <= 0:
            with timer_container:
                st.warning("시간이 종료되었습니다!")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("30초 더 학습하기", use_container_width=True):
                        st.session_state.timer_start_time = time.time()
                        st.rerun()
                with col2:
                    if st.button("현재 상태로 제출하기", use_container_width=True):
                        st.session_state.page = 'feedback'
                        save_data()
                        st.rerun()
            break

        time.sleep(0.1)

def show_feedback():
    st.title("결과 피드백")

    task = st.session_state.task
    actions = st.session_state.selected_action

    # 정보 신뢰도 평가 피드백 수정
    st.subheader("📊 정보 판단 결과")
    for card, trust in st.session_state.trust.items():
        correct = card in tasks[task]['correct_info']
        if trust == '선택하지 않음':
            if correct:
                st.info(f"ℹ️ '{card}' - 이 정보는 신뢰할 수 있는 정보였습니다.")
            else:
                st.info(f"ℹ️ '{card}' - 이 정보는 신뢰할 수 없는 정보였습니다.")
        elif correct and trust == '신뢰한다':
            st.success(f"✅ '{card}' - 올바른 판단! 이 정보는 신뢰할 수 있는 정보였습니다.")
        elif not correct and trust == '신뢰하지 않는다':
            st.success(f"✅ '{card}' - 올바른 판단! 이 정보는 신뢰할 수 없는 정보였습니다.")
        else:
            st.error(f"❌ '{card}' - 잘못된 판단. 이 정보의 신뢰성을 다시 검토해보세요.")

    st.divider()
    st.subheader("🎯 행동 선택 결과")
    
    # 기존의 행동 선택 피드백 로직
    if task == 'Task 1: 기본 대응':
        if '119 신고' in actions:
            st.success("✅ 정답입니다! 119 신고가 최선의 선택입니다.")
        else:
            st.error("❌ 잘못된 선택입니다. 긴급 상황에서는 즉시 신고가 필요합니다.")

    elif task == 'Task 2: 정보 충돌 대처':
        if '부상자 상태 확인 후 대기' in actions:
            st.success("✅ 정답입니다! 부상자 상태를 확인하고 대기하는 것이 최선입니다.")
        else:
            st.error("❌ 잘못된 선택입니다. 부상자를 이동시키면 2차 피해를 입힐 수 있습니다.")

    elif task == 'Task 3: 복합 상황 대응':
        if '119 신고' in actions and 'AED 사용' in actions and not ('물 마시게 하기' in actions or '아무것도 하지 않기' in actions):
            st.success("✅ 정답입니다! 119 신고와 AED 사용이 생존율을 높이는 최선의 조치입니다.")
        else:
            st.error("❌ 최선의 조치를 취하지 않았습니다. 정확한 응급 대응이 필요합니다.")

    st.divider()
    again = st.radio("다시 학습하시겠습니까?", ("예", "아니오"), horizontal=True)

    if st.button("확인", use_container_width=True):
        if again == "예":
            # 현재 태스크를 유지하고 다시 시작
            st.session_state.page = 'task'
            st.session_state.trust = {}
            st.session_state.selected_action = []
            st.session_state.timer_start_time = time.time()
        else:
            # 첫 화면으로 돌아가기
            st.session_state.page = 'intro'
            st.session_state.trust = {}
            st.session_state.selected_action = []
            st.session_state.task = None
            st.session_state.timer_start_time = None
        st.rerun()

# --- 메인 페이지 흐름 ---
# 사이드바 구성
with st.sidebar:
    st.markdown("### 📋 메뉴")
    
    # 인트로 페이지로 돌아가기 버튼 추가
    if st.button("🏠 처음으로", use_container_width=True):
        st.session_state.page = 'intro'
        st.session_state.trust = {}
        st.session_state.selected_action = []
        st.session_state.task = None
        st.session_state.timer_start_time = None
        st.rerun()
    
    st.markdown("---")  # 구분선 추가
    
    # 할 일 목록 표시
    st.markdown("### 📝 할 일 체크리스트")
    if st.session_state.page == 'intro':
        st.markdown("1. ✨ **응급 상황 고르기**")
        st.markdown("2. 🔍 정보 확인과 대응 결정하기 (30초)")
        st.markdown("3. 📊 결과 보고 다시 도전하기")
    elif st.session_state.page == 'task':
        st.markdown("1. ✓ ~~응급 상황 고르기~~")
        st.markdown("2. ✨ **정보 확인과 대응 결정하기 (30초)**")
        st.markdown("3. 📊 결과 보고 다시 도전하기")
    elif st.session_state.page == 'feedback':
        st.markdown("1. ✓ ~~응급 상황 고르기~~")
        st.markdown("2. ✓ ~~정보 확인과 대응 결정하기~~")
        st.markdown("3. ✨ **결과 보고 다시 도전하기**")
    
    st.markdown("---")  # 구분선 추가
    
    # 현재 태스크 표시
    if st.session_state.page == 'task':
        st.markdown("### 📋 현재 Task")
        st.info(f"**{st.session_state.task}**")

# 메인 페이지 표시
if st.session_state.page == 'intro':
    show_intro()
elif st.session_state.page == 'task':
    show_task()
elif st.session_state.page == 'feedback':
    show_feedback()