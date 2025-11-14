import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime


st.set_page_config(page_title="감정 척도 대시보드", layout="wide")

EMOTIONS = ["기쁨", "슬픔", "수치심", "불안", "분노", "당황", "부러움"]
EMOJI = {
    "기쁨": "😄",
    "슬픔": "😢",
    "수치심": "😳",
    "불안": "😰",
    "분노": "😠",
    "당황": "😅",
    "부러움": "😮‍💨",
}
EXAMPLES = {
    "기쁨": "친구를 만났을 때, 좋아하는 음식을 먹을 때",
    "슬픔": "좋아하는 것을 잃었을 때, 마음이 아플 때",
    "수치심": "실수를 했을 때, 누군가 앞에서 창피를 당했을 때",
    "불안": "시험을 볼 때, 새로운 곳에 갈 때",
    "분노": "불공평한 일이 있을 때, 화가 날 때",
    "당황": "예상 밖의 일이 생겼을 때, 놀랐을 때",
    "부러움": "친구가 멋진 것을 가졌을 때, 잘하는 것을 봤을 때",
}


def init_state():
    if "records" not in st.session_state:
        st.session_state.records = []


init_state()

st.title("🎈 감정 척도 입력기 & 시각화")
st.write("상황을 입력하고 각 감정에 대해 1~10 점수로 채워 기록하면, 다양한 그래프로 시각화해줍니다.")

with st.form(key="input_form"):
    st.subheader("1) 상황 입력")
    situation = st.text_input("상황을 간단히 적어주세요", placeholder="예: 오늘 발표를 했을 때")

    st.subheader("2) 감정 점수 (1~10)")
    cols = st.columns(len(EMOTIONS))
    scores = {}
    for i, emo in enumerate(EMOTIONS):
        with cols[i]:
            label = f"{EMOJI.get(emo, '')} {emo}"
            scores[emo] = st.slider(label, 1, 10, 5, key=f"s_{emo}")

    submitted = st.form_submit_button("기록 추가")
    if submitted:
        record = {"상황": situation if situation else "(비어있음)", "시간": datetime.now()}
        record.update(scores)
        st.session_state.records.append(record)
        st.success("기록이 추가되었습니다.")

col_left, col_right = st.columns([2, 1])
with col_left:
    st.subheader("저장된 기록")
    if len(st.session_state.records) == 0:
        st.info("아직 기록이 없습니다. 위에서 상황과 감정 점수를 입력해 보세요.")
    else:
        df = pd.DataFrame(st.session_state.records)
        df_display = df.copy()
        df_display["시간"] = df_display["시간"].dt.strftime("%Y-%m-%d %H:%M:%S")
        st.dataframe(df_display.sort_values(by="시간", ascending=False))

        if st.button("기록 초기화"):
            st.session_state.records = []
            st.experimental_rerun()

with col_right:
    st.subheader("감정 이모지 미리보기")
    for emo in EMOTIONS:
        st.write(f"{EMOJI.get(emo, '')}  **{emo}**")
        st.caption(f"예: {EXAMPLES.get(emo, '')}")

st.markdown("---")

st.header("시각화 선택")
plot_type = st.radio("그래프 유형을 선택하세요", ("히스토그램", "막대그래프", "산점도", "상자그림"))

if len(st.session_state.records) == 0:
    st.warning("데이터가 부족합니다. 먼저 하나 이상의 기록을 추가하세요.")
else:
    df = pd.DataFrame(st.session_state.records)

    if plot_type == "히스토그램":
        with st.expander("히스토그램 변수 선택 (클릭하여 선택)"):
            var = st.selectbox("변수 선택", EMOTIONS)
            bins = st.slider("빈 개수", 5, 30, 10)
            if var:
                fig = px.histogram(df, x=var, nbins=bins, title=f"{EMOJI.get(var,'')}{var} 히스토그램")
                st.plotly_chart(fig, use_container_width=True)

    elif plot_type == "막대그래프":
        with st.expander("막대그래프 옵션 (클릭하여 선택)"):
            mode = st.selectbox("모드 선택", ("감정별 평균","상황별 평균(특정 감정)"))
            if mode == "감정별 평균":
                means = df[EMOTIONS].mean().reset_index()
                means.columns = ["감정","평균점수"]
                means["감정_이모지"] = means["감정"].map(lambda x: EMOJI.get(x, ""))
                fig = px.bar(means, x="감정_이모지", y="평균점수", hover_name="감정", title="감정별 평균 점수")
                st.plotly_chart(fig, use_container_width=True)
            else:
                emo = st.selectbox("집계할 감정 선택", EMOTIONS)
                grouped = df.groupby("상황")[emo].mean().reset_index()
                fig = px.bar(grouped, x="상황", y=emo, title=f"상황별 {EMOJI.get(emo,'')}{emo} 평균")
                st.plotly_chart(fig, use_container_width=True)

    elif plot_type == "산점도":
        with st.expander("산점도 변수 선택 (클릭하여 선택)"):
            x_var = st.selectbox("X 변수", EMOTIONS, index=0)
            y_var = st.selectbox("Y 변수", EMOTIONS, index=1)
            color_by = st.selectbox("색상(선택)", ["상황", "없음"])
            if x_var and y_var:
                if color_by == "상황":
                    fig = px.scatter(df, x=x_var, y=y_var, color="상황", hover_data=["시간"], title=f"{x_var} vs {y_var}")
                else:
                    fig = px.scatter(df, x=x_var, y=y_var, hover_data=["상황","시간"], title=f"{x_var} vs {y_var}")
                st.plotly_chart(fig, use_container_width=True)

    elif plot_type == "상자그림":
        with st.expander("상자그림 변수 선택 (클릭하여 선택)"):
            var = st.selectbox("변수 선택", EMOTIONS)
            if var:
                fig = px.box(df, y=var, points="all", title=f"{EMOJI.get(var,'')}{var} 상자그림")
                st.plotly_chart(fig, use_container_width=True)

st.caption("Tip: 그래프를 선택하고, 확장(expander)을 클릭해 변수(또는 모드)를 골라보세요. 아이들을 위해 이모지로 감정을 직관적으로 표시합니다.")

