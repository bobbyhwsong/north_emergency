import streamlit as st
import pandas as pd
import time
import os
from datetime import datetime

# --- 처음 세팅 ---
if 'page' not in st.session_state:
    st.session_state.page = 'intro'  # 처음에는 들어가기 쪽 (intro 페이지)으로 시작
if 'trust' not in st.session_state:
    st.session_state.trust = {}
if 'selected_action' not in st.session_state:
    st.session_state.selected_action = []
if 'task' not in st.session_state:
    st.session_state.task = None
if 'timer_start_time' not in st.session_state:
    st.session_state.timer_start_time = None

# --- 일거리별 자료 (Task별 데이터) ---
tasks = {
    'Task 1: 쉬운 정보 알아보기 (단순 정보 이해)': {
        'situation': '여름철 바깥나들이 중 기운이 빠진 사람을 보았습니다. (여름철 야외 활동 중 탈진한 사람을 발견했습니다.)',
        'timer': 30,
        'cards': {
            '급한 손질 안내글 (응급 처치 가이드)': {
                'summary': '탈수 기운이 보이면, 바로 그늘진 곳으로 옮기고 물을 마시게 해야 합니다. (탈수 증상이 보이면, 즉시 그늘진 곳으로 옮기고 수분을 보충해야 합니다.)',
                'source': '대한급손학회 (대한응급의학회)'
            }
        },
        'question': '탈수 환자는 그늘로 옮기고 물을 마시게 해야 합니다. (탈수 환자는 그늘로 옮기고 수분을 보충해야 한다.)',
        'correct_answer': 'O',
        'explanation': {
            'correct': "잘하셨습니다! 탈수 환자는 체온을 낮추고 물을 천천히 마시는 것이 중요합니다. (정확합니다! 탈수 환자의 경우 체온을 낮추고 수분을 보충하는 것이 가장 중요합니다.)",
            'incorrect': "아쉽습니다. 탈수 환자는 반드시 그늘로 옮겨 체온을 낮추고 물을 마셔야 합니다. (틀렸습니다. 탈수 환자는 반드시 그늘로 옮겨 체온을 낮추고 수분을 보충해야 합니다.)"
        },
        'actions': []
    },

    'Task 2: 다른 정보 가운데 바른 것 찾기 (정보 충돌 판단)': {
        'situation': '길에서 열로 지친 듯한 사람을 보았습니다. (길거리에서 사람이 열사병으로 의심되는 증상을 보입니다.)',
        'timer': 30,
        'cards': {
            '급한 손질 공식책 (응급처치 공식 매뉴얼)': {
                'summary': '환자를 시원한 곳으로 옮기고, 몸을 적셔서 체온을 내려야 합니다. (환자를 시원한 곳으로 옮기고, 몸을 적셔 체온을 낮춰야 합니다.)',
                'source': '급손 공식 책자 (응급처치 공식 매뉴얼)'
            },
            '건강 글모음 조언 (건강 블로그 조언)': {
                'summary': '따뜻한 차를 마시게 하면 좋습니다. (뜨거운 음료(따뜻한 차)를 마시게 하면 회복에 좋다.)',
                'source': '건강 기록글 (건강 블로그)'
            },
            '소방청 급손 안내 (소방청 응급처치 가이드)': {
                'summary': '의식이 없으면 억지로 물을 먹이면 안 됩니다. (의식이 없으면 물을 억지로 먹이면 안 된다.)',
                'source': '소방청 안내 (소방청 가이드)'
            }
        },
        'actions': [
            '시원한 곳으로 옮기고 체온 낮추기',
            '따뜻한 차를 마시게 하기',
            '물을 억지로 먹이기'
        ],
        'correct_action': '시원한 곳으로 옮기고 체온 낮추기',
        'feedback': {
            '시원한 곳으로 옮기고 체온 낮추기': {
                'type': 'success',
                'message': '✅ 잘하셨습니다! 열로 지친 사람은 즉시 몸을 식히는 것이 가장 중요합니다. (✅ 정답입니다! 열사병 환자의 경우 즉시 체온을 낮추는 것이 가장 중요합니다.)'
            },
            '따뜻한 차를 마시게 하기': {
                'type': 'error',
                'message': '❌ 아쉽습니다. 뜨거운 음료는 몸을 더 덥게 할 수 있어 위험합니다. (❌ 틀렸습니다. 뜨거운 음료는 체온을 더 높일 수 있어 위험합니다.)'
            },
            '물을 억지로 먹이기': {
                'type': 'error',
                'message': '❌ 아쉽습니다. 정신을 잃은 사람에게 억지로 물을 먹이면 기도가 막힐 수 있어 아주 위험합니다. (❌ 틀렸습니다. 의식이 없는 상태에서 물을 억지로 먹이면 기도가 막힐 수 있어 매우 위험합니다.)'
            }
        }
    },

    'Task 3: 복잡한 상황에서 올바른 길 찾기 (복합적 해석과 대응)': {
        'situation': '큰 가게 안에서 사람이 쓰러져 정신이 없습니다. 주변에 자동 심장 충격기(AED)가 있습니다. 상황을 아는 사람은 없습니다. (쇼핑몰에서 사람이 쓰러져 의식이 없습니다. 주변에는 AED 장비가 있고, 상황을 아는 사람이 없습니다.)',
        'timer': 30,
        'cards': {
            '급손 안내 누리집 (응급의료포털 지침)': {
                'summary': '바로 119에 전화하고 자동 심장 충격기를 가져와야 합니다. (즉시 119에 신고하고 AED를 가져와야 합니다.)',
                'source': '급손 누리집 (응급의료포털)'
            },
            '자동 심장 충격기 쓰는 법 (AED 사용 가이드)': {
                'summary': '자동 심장 충격기는 안내 소리를 따라하면 누구나 쓸 수 있습니다. (AED는 음성 안내를 따라 사용하면 누구나 쉽게 쓸 수 있습니다.)',
                'source': '의료기관 안내 (의료기관 가이드)'
            },
            '손발 데우기 요법 (온열 요법)': {
                'summary': '손과 발을 따뜻하게 하면 회복됩니다. (손발을 따뜻하게 해주면 금방 회복된다.)',
                'source': '집안요법 기록글 (민간요법 블로그)'
            },
            '귀를 세게 치기 (귀 자극법)': {
                'summary': '귀를 세게 때리면 정신을 차립니다. (귀를 세게 때리면 정신이 돌아온다.)',
                'source': '미확인 모임터 (미확인 커뮤니티)'
            },
            '가슴 숨쉬기 손질 (심폐소생술 지침)': {
                'summary': '심장이 멈춘 것 같으면 의식과 숨 쉬는지 먼저 확인하고 가슴 눌러 숨쉬기(심폐소생술)를 해야 합니다. (심장마비 의심 시, 의식과 호흡을 먼저 확인한 후 심폐소생술을 시작해야 한다.)',
                'source': '대한심장학회 (대한심장학회)'
            }
        },
        'actions': [
            '119에 전화하기 (119에 신고하기)',
            '자동 심장 충격기 가져오기 (AED 가져오기)',
            '손발을 따뜻하게 하기',
            '귀를 세게 치기',
            '의식과 숨 쉬기 확인하기 (의식과 호흡 확인하기)'
        ],
        'correct_actions': ['119에 전화하기 (119에 신고하기)', '자동 심장 충격기 가져오기 (AED 가져오기)'],
        'feedback': {
            '119에 전화하기 (119에 신고하기)': '✅ 잘하셨습니다! 급할 때는 전문가 도움을 빨리 받아야 합니다. (✅ 정확한 판단입니다. 응급 상황에서는 전문가의 도움이 필수적입니다.)',
            '자동 심장 충격기 가져오기 (AED 가져오기)': '✅ 잘하셨습니다! 자동 심장 충격기는 생명을 살리는 데 꼭 필요합니다. (✅ 정확한 판단입니다. AED는 심장마비 환자의 생존율을 크게 높입니다.)',
            '손발을 따뜻하게 하기': '❌ 손발을 따뜻하게 하는 민간요법은 도움이 되지 않습니다. (❌ 효과 없는 민간요법입니다. 귀중한 시간만 낭비하게 됩니다.)',
            '귀를 세게 치기': '❌ 매우 위험한 행동입니다. 머리에 큰 해를 줄 수 있습니다. (❌ 매우 위험한 행동입니다. 두부 손상을 일으킬 수 있습니다.)',
            '의식과 숨 쉬기 확인하기 (의식과 호흡 확인하기)': '⚠️ 중요한 절차이지만, 우선 119에 전화하고 자동 심장 충격기를 준비해야 합니다. (⚠️ 중요한 절차이지만, 119 신고와 AED 준비가 더 시급합니다.)'
        }
    }
}

# --- 배운 내용 저장하는 곳 (데이터 저장 함수 수정) ---
def save_data():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if 'saved_responses' not in st.session_state:
        st.session_state.saved_responses = []
    
    data = {
        '배운 때 (Timestamp)': timestamp,
        '배운 일 (Task)': st.session_state.task,
        '믿은 글들 (Trust_Responses)': st.session_state.trust,
        '고른 행동들 (Selected_Action)': st.session_state.selected_action
    }
    
    st.session_state.saved_responses.append(data)
    
    if st.session_state.page == 'feedback':
        if len(st.session_state.saved_responses) > 0:
            df = pd.DataFrame(st.session_state.saved_responses)
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 배운 내용 내려받기 (학습 기록 다운로드)",
                data=csv,
                file_name=f"emergency_responses_{timestamp}.csv",
                mime="text/csv"
            )

def show_intro():
    st.title("🚑 급한 때 살리는 배움터 (응급 상황 대응 학습 프로그램)")
    
    st.markdown("""
    ## 급할 때, 당신이 살리는 힘이 됩니다 (응급 상황, 당신의 판단이 생명을 좌우합니다)
    
    이 배움터는 급할 때 빠르게 올바른 판단을 할 수 있도록 돕습니다. (이 프로그램은 응급 상황에서의 올바른 의사결정 능력을 향상시키기 위한 학습 도구입니다.)
    
    ### 📝 할 일
    
    1. **배울 일 고르기 (응급 상황 고르기)**

       ➡️ 배우고 싶은 상황을 고르세요.
       ➡️ '배움 시작하기' 단추를 누르세요.
    
    2. **글 읽고 행동 고르기 (정보 확인과 대응 결정하기)**

       ➡️ 글카드를 눌러 내용을 읽어보세요.
       ➡️ 믿을 수 있는지 생각하세요.
       ➡️ 어떻게 행동할지도 함께 생각하세요.
       ➡️ 30초 안에 선택을 마치세요.
    
    3. **돌아보기하고 다시 도전하기 (결과 보고 다시 도전하기)**

       ➡️ 돌려보기(피드백)를 살펴보세요.
       ➡️ 다시 도전하거나 다른 상황을 고르세요.
    """)
    
    st.markdown("---")
    st.markdown("### 🎯 배울 일 고르기 (학습할 태스크 선택)")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_task = st.radio(
            "배우고 싶은 상황을 고르세요: (응급 상황을 선택하세요:)",
            list(tasks.keys()),
            format_func=lambda x: f"{x.split(':')[0]}\n{x.split(':')[1]}"
        )
    
    st.markdown("#### 선택한 상황")
    st.info(tasks[selected_task]['situation'])
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("배움 시작하기 👉 (학습 시작하기 👉)", use_container_width=True):
            st.session_state.task = selected_task
            st.session_state.page = 'task'
            st.session_state.timer_start_time = time.time()
            st.rerun()

    st.markdown("---")
    st.caption("© 2024 급한 때 살리는 배움터 (응급 상황 대응 학습 프로그램) | 문의: emergency@example.com")

def show_task():
    if st.session_state.task is None:
        st.warning("옆에 있는 메뉴에서 배울 일을 먼저 골라주세요. (사이드바에서 Task를 먼저 선택해주세요.)")
        st.stop()

    st.title("글 읽고 행동 고르기 (정보 탐색 및 행동 결정)")
    
    timer_container = st.empty()
    
    st.subheader(tasks[st.session_state.task]['situation'])

    if st.session_state.task == 'Task 1: 쉬운 정보 알아보기 (단순 정보 이해)':
        for title, content in tasks[st.session_state.task]['cards'].items():
            st.markdown("### 📋 급한 손질 정보 (응급 처치 정보)")
            st.info(f"**{content['summary']}**")
            st.caption(f"출처: {content['source']}")
        
        st.divider()
        st.markdown("### ❓ 문제")
        st.markdown(f"**{tasks[st.session_state.task]['question']}**")
        
        user_answer = st.radio(
            "답을 고르세요: (답을 선택하세요:)",
            options=['O', 'X'],
            horizontal=True
        )
        
        if st.button("답 제출하기 (정답 제출)", use_container_width=True):
            st.session_state.selected_action = [user_answer]
            st.session_state.page = 'feedback'
            st.rerun()

    else:
        cards = tasks[st.session_state.task]['cards']
        for title, content in cards.items():
            with st.expander(f"📄 {title}"):
                st.write(f"**요약:** {content['summary']}")
                st.caption(f"출처: {content['source']}")
                trust = st.radio(
                    f"이 글을 믿겠습니까? ('{title}' 정보를 신뢰합니까?)",
                    ('고르지 않음 (선택하지 않음)', '믿는다 (신뢰한다)', '믿지 않는다 (신뢰하지 않는다)'),
                    index=0,
                    key=f"trust_{title}"
                )
                st.session_state.trust[title] = trust
        
        st.divider()
        actions = tasks[st.session_state.task]['actions']
        if st.session_state.task == 'Task 3: 복잡한 상황에서 올바른 길 찾기 (복합적 해석과 대응)':
            st.markdown("**⚠️ 여러 행동을 함께 고를 수 있습니다 (여러 행동을 동시에 선택할 수 있습니다)**")
            action = st.multiselect("당신의 선택:", actions)
        else:
            action = [st.radio("당신의 선택:", actions)]

        if st.button("선택 완료하기 (선택 완료)", use_container_width=True):
            st.session_state.selected_action = action
            st.session_state.page = 'feedback'
            st.rerun()

    # 타이머
    total_time = tasks[st.session_state.task]['timer']
    while True:
        elapsed_time = int(time.time() - st.session_state.timer_start_time)
        remaining_time = max(0, total_time - elapsed_time)
        progress = remaining_time / total_time

        with timer_container:
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(
                    f"<h1 style='text-align: center; color: red; font-size: 40px;'>{remaining_time}</h1>",
                    unsafe_allow_html=True
                )
            with col2:
                st.progress(progress)

        if remaining_time <= 0:
            with timer_container:
                st.warning("시간이 다 됐습니다! (시간이 종료되었습니다!)")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("30초 더 배우기 (30초 더 학습하기)", use_container_width=True):
                        st.session_state.timer_start_time = time.time()
                        st.rerun()
                with col2:
                    if st.button("지금까지 한 걸로 넘어가기 (현재 상태로 제출하기)", use_container_width=True):
                        st.session_state.page = 'feedback'
                        save_data()
                        st.rerun()
            break

        time.sleep(0.1)

def show_feedback():
    st.title("결과 돌아보기 (결과 피드백)")

    task = st.session_state.task
    actions = st.session_state.selected_action

    if task == 'Task 1: 쉬운 정보 알아보기 (단순 정보 이해)':
        user_answer = st.session_state.selected_action[0]
        correct_answer = tasks[task]['correct_answer']
        
        st.markdown("### 📝 문제")
        st.markdown(f"**{tasks[task]['question']}**")
        
        st.markdown("### 🎯 결과")
        if user_answer == correct_answer:
            st.success("✅ 맞았습니다! (정답입니다!)")
            st.markdown(tasks[task]['explanation']['correct'])
        else:
            st.error("❌ 틀렸습니다.")
            st.markdown(tasks[task]['explanation']['incorrect'])
        
        st.divider()
        st.markdown("### 💡 더 알기 (추가 설명)")
        st.info("""
        탈수 환자를 발견했을 때 해야 할 일:
        1. 바로 그늘로 옮기기
        2. 시원한 물을 천천히 마시게 하기
        3. 정신이 없거나 심하면 119에 전화하기
        """)

    elif task == 'Task 2: 다른 정보 가운데 바른 것 찾기 (정보 충돌 판단)':
        st.markdown("### 📋 제시된 정보 살펴보기 (제시된 정보 분석)")

        st.info("""
        1. 급손 공식 책자 (응급처치 공식 매뉴얼) – 믿을 수 있습니다.
           - 더운 날에는 몸을 시원하게 식히는 것이 가장 중요합니다.

        2. 건강 글모음 조언 (건강 블로그 조언) – 믿기 어렵습니다.
           - 따뜻한 차는 체온을 더 높일 수 있어 위험합니다.

        3. 소방청 급손 안내 (소방청 가이드) – 믿을 수 있습니다.
           - 정신이 없는 환자에게는 절대 물을 억지로 먹이지 않습니다.
        """)

        st.markdown("### 🎯 당신의 선택 결과 (선택 결과)")
        selected_action = actions[0]
        feedback = tasks[task]['feedback'][selected_action]
        
        if feedback['type'] == 'success':
            st.success(feedback['message'])
        else:
            st.error(feedback['message'])

        st.markdown("### 💡 바른 대처법 (올바른 대처 방법)")
        st.info("""
        열로 쓰러진 사람을 보면 이렇게 하세요:

        1️⃣ 바로 시원한 곳으로 옮기세요.  
        2️⃣ 옷을 느슨하게 풀어주고 몸을 식히세요.  
        3️⃣ 정신이 있으면 시원한 물을 천천히 마시게 하세요.  
        4️⃣ 심각하면 바로 119에 전화하세요.

        ⚠️ 주의할 점:
        - 검증되지 않은 민간요법은 믿지 마세요.
        - 정신이 없는 사람에게 물을 먹이지 마세요.
        """)

    elif task == 'Task 3: 복잡한 상황에서 올바른 길 찾기 (복합적 해석과 대응)':
        st.markdown("### 📋 제시된 정보 살펴보기 (제시된 정보 분석)")

        st.info("""
        믿을 수 있는 정보:
        - 급손 누리집 (응급의료포털): 119에 전화하고 자동 심장 충격기 가져오기
        - 의료기관 안내 (의료기관 가이드): 자동 심장 충격기(AED) 사용 방법
        - 대한심장학회: 가슴 눌러 숨쉬기(심폐소생술) 절차

        믿기 어려운 정보:
        - 집안요법 기록글 (민간요법 블로그): 손발 따뜻하게 하기
        - 미확인 모임터 (미확인 커뮤니티): 귀를 세게 치기
        """)

        st.markdown("### 🎯 당신의 선택 결과 분석 (선택 결과 분석)")

        st.write("당신이 고른 행동:")

        for action in actions:
            if action in tasks[task]['correct_actions']:
                st.success(f"✅ {action}: {tasks[task]['feedback'][action]}")
            else:
                if action == '의식과 숨 쉬기 확인하기 (의식과 호흡 확인하기)':
                    st.warning(f"⚠️ {action}: {tasks[task]['feedback'][action]}")
                else:
                    st.error(f"❌ {action}: {tasks[task]['feedback'][action]}")

        st.markdown("### 💡 바른 대처 순서 (올바른 대처 순서)")
        st.info("""
        1️⃣ 바로 119에 전화하세요.  
        2️⃣ 자동 심장 충격기를 가져오세요.  
        3️⃣ 의식과 숨 쉬는지 확인하세요.  
        4️⃣ 자동 심장 충격기의 안내 소리를 따라 사용하세요.

        ⚠️ 주의:
        - 검증되지 않은 방법은 하지 마세요.
        - 환자에게 물리적 충격을 주지 마세요.
        """)

    st.divider()
    again = st.radio("다시 도전하시겠습니까? (다시 학습하시겠습니까?)", ("예", "아니오"), horizontal=True)

    if st.button("확인"):
        if again == "예":
            st.session_state.page = 'task'
            st.session_state.trust = {}
            st.session_state.selected_action = []
            st.session_state.timer_start_time = time.time()
        else:
            st.session_state.page = 'intro'
            st.session_state.trust = {}
            st.session_state.selected_action = []
            st.session_state.task = None
            st.session_state.timer_start_time = None
        st.rerun()

# --- 메인 페이지 흐름 ---
with st.sidebar:
    st.markdown("### 📋 메뉴")
    
    if st.button("🏠 처음으로 돌아가기 (🏠 처음으로)", use_container_width=True):
        st.session_state.page = 'intro'
        st.session_state.trust = {}
        st.session_state.selected_action = []
        st.session_state.task = None
        st.session_state.timer_start_time = None
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📝 할 일 살펴보기 (할 일 체크리스트)")
    if st.session_state.page == 'intro':
        st.markdown("1. ✨ **배울 일 고르기 (응급 상황 고르기)**")
        st.markdown("2. 🔍 글 읽고 행동 고르기 (정보 확인과 대응 결정하기)")
        st.markdown("3. 📊 돌아보기하고 다시 도전하기 (결과 보고 다시 도전하기)")
    elif st.session_state.page == 'task':
        st.markdown("1. ✓ ~~배울 일 고르기~~")
        st.markdown("2. ✨ **글 읽고 행동 고르기 (정보 확인과 대응 결정하기)**")
        st.markdown("3. 📊 돌아보기하고 다시 도전하기")
    elif st.session_state.page == 'feedback':
        st.markdown("1. ✓ ~~배울 일 고르기~~")
        st.markdown("2. ✓ ~~글 읽고 행동 고르기~~")
        st.markdown("3. ✨ **돌아보기하고 다시 도전하기 (결과 보고 다시 도전하기)**")

    st.markdown("---")
    
    if st.session_state.page == 'task':
        st.markdown("### 📋 지금 배우는 일 (현재 Task)")
        st.info(f"**{st.session_state.task}**")

# 메인 페이지 표시
if st.session_state.page == 'intro':
    show_intro()
elif st.session_state.page == 'task':
    show_task()
elif st.session_state.page == 'feedback':
    show_feedback()