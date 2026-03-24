import time

import streamlit as st
import streamlit.components.v1 as components

from analyser import (
    analyze_sentiment,
    detect_filler_words,
    evaluate_structure,
    generate_ai_feedback,
    generate_score,
    keyword_match,
)


st.set_page_config(
    page_title="Interview Insight",
    page_icon="AI",
    layout="wide",
)


QUESTION_BANK = {
    "Tell me about yourself": ["student", "skills", "experience", "projects", "goals"],
    "Why should we hire you?": ["skills", "team", "value", "contribution", "growth"],
    "What are your strengths?": ["strengths", "example", "results", "team", "impact"],
    "What is your biggest weakness?": ["weakness", "improving", "learning", "feedback", "growth"],
    "Describe a challenge you faced and how you handled it.": ["challenge", "action", "solution", "result", "learning"],
    "Tell me about a time you worked in a team.": ["team", "role", "communication", "contribution", "outcome"],
    "Why do you want this role?": ["role", "company", "skills", "motivation", "growth"],
    "Where do you see yourself in 5 years?": ["goals", "growth", "learning", "responsibility", "impact"],
    "Tell me about a project you are proud of.": ["project", "problem", "solution", "impact", "skills"],
    "How do you handle pressure or tight deadlines?": ["pressure", "prioritize", "focus", "deadline", "result"],
}


if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "end_time" not in st.session_state:
    st.session_state.end_time = None

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "answer_text" not in st.session_state:
    st.session_state.answer_text = ""

if "analysis_started_at" not in st.session_state:
    st.session_state.analysis_started_at = None


st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(200, 232, 220, 0.7), transparent 28%),
            radial-gradient(circle at top right, rgba(245, 230, 204, 0.7), transparent 24%),
            linear-gradient(180deg, #f8f6f1 0%, #f1ede4 100%);
        color: #182019;
    }
    .block-container {
        max-width: 1080px;
        padding-top: 4.2rem;
        padding-bottom: 3rem;
    }
    .hero {
        padding: 0.4rem 0 0.8rem;
        margin-bottom: 0.6rem;
    }
    .hero h1 {
        margin: 0;
        font-size: 1.9rem;
        line-height: 1.08;
        color: #142117;
    }
    .hero p {
        margin: 0.35rem 0 0;
        font-size: 0.95rem;
        color: #4f5d51;
        max-width: 460px;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.78);
        border: 1px solid rgba(24, 32, 25, 0.08);
        border-radius: 20px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 30px rgba(48, 56, 48, 0.06);
    }
    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #657264;
    }
    .metric-value {
        margin-top: 0.35rem;
        font-size: 1.7rem;
        font-weight: 700;
        color: #152118;
    }
    .section-card {
        background: rgba(255, 255, 255, 0.76);
        border: 1px solid rgba(24, 32, 25, 0.08);
        border-radius: 22px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 10px 28px rgba(48, 56, 48, 0.06);
        margin-top: 0.8rem;
    }
    .stButton > button {
        border-radius: 999px;
        border: 1px solid #1d2c1f;
        background: #1d2c1f;
        color: #f8f6f1;
        font-weight: 600;
        padding: 0.6rem 1.1rem;
    }
    .stButton > button:hover {
        border-color: #243927;
        background: #243927;
        color: #f8f6f1;
    }
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    .stTextArea textarea {
        border-radius: 18px !important;
        background: rgba(255,255,255,0.78) !important;
    }
    div[data-baseweb="select"] * {
        cursor: pointer !important;
    }
    .timer-shell {
        background: rgba(20, 33, 23, 0.94);
        color: #f8f6f1;
        border-radius: 22px;
        padding: 1rem 1.2rem;
        margin: 0.2rem 0 1rem;
        box-shadow: 0 14px 30px rgba(20, 33, 23, 0.18);
    }
    .timer-label {
        font-size: 0.76rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        opacity: 0.72;
    }
    .timer-value {
        font-size: 2rem;
        font-weight: 700;
        margin-top: 0.15rem;
    }
    </style>
    <div class="hero">
        <h1>Interview Insight</h1>
        <p>AI-Powered Interview Coaching</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def render_metric(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_countdown(end_time):
    if not end_time:
        return

    end_ms = int(end_time * 1000)
    html = f"""
    <div class="timer-shell">
        <div class="timer-label">Timer</div>
        <div class="timer-value" id="timer">--:--</div>
    </div>
    <script>
    const endTime = {end_ms};
    const el = document.getElementById("timer");
    function updateTimer() {{
        const diff = endTime - Date.now();
        if (diff <= 0) {{
            el.textContent = "00:00";
            return;
        }}
        const totalSeconds = Math.floor(diff / 1000);
        const mins = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
        const secs = String(totalSeconds % 60).padStart(2, "0");
        el.textContent = `${{mins}}:${{secs}}`;
    }}
    updateTimer();
    setInterval(updateTimer, 1000);
    </script>
    """
    components.html(html, height=96)


question_col, duration_col = st.columns([1.7, 1])

with question_col:
    question = st.selectbox("Select a question", list(QUESTION_BANK.keys()))

with duration_col:
    duration = st.slider("Answer time (seconds)", 15, 120, 45, 5)

keywords = QUESTION_BANK[question]

controls_col, _spacer = st.columns([1, 1.7])
with controls_col:
    if st.button("Start Interview", use_container_width=True):
        st.session_state.start_time = time.time()
        st.session_state.end_time = st.session_state.start_time + duration
        st.session_state.submitted = False
        st.session_state.answer_text = ""
        st.session_state.analysis_started_at = None


timer_active = (
    st.session_state.start_time
    and st.session_state.end_time
    and not st.session_state.submitted
)

if st.session_state.start_time:
    if timer_active:
        render_countdown(st.session_state.end_time)
    else:
        remaining = max(0, int(st.session_state.end_time - (st.session_state.analysis_started_at or st.session_state.end_time)))
        minutes = str(remaining // 60).zfill(2)
        seconds = str(remaining % 60).zfill(2)
        components.html(
            f"""
            <div class="timer-shell">
                <div class="timer-label">Timer</div>
                <div class="timer-value">{minutes}:{seconds}</div>
            </div>
            """,
            height=96,
        )

    if timer_active and time.time() >= st.session_state.end_time:
        st.warning("Time is up. You can still submit your answer.")
    elif timer_active:
        st.info("The timer is running. Draft your answer while the countdown updates live.")

    st.text_area(
        "Enter your answer",
        key="answer_text",
        height=220,
        placeholder="Write your interview answer here...",
    )
else:
    st.empty()


if st.button("Analyze", use_container_width=True):
    st.session_state.submitted = True
    st.session_state.analysis_started_at = time.time()


if st.session_state.submitted:
    answer = st.session_state.answer_text.strip()

    if not answer:
        st.warning("Enter an answer before analyzing.")
    else:
        fillers = detect_filler_words(answer)
        sentiment = analyze_sentiment(answer)
        structure = evaluate_structure(answer)
        score = generate_score(fillers, sentiment)
        matched, missing = keyword_match(answer, keywords)

        st.markdown("### Analysis")
        metric_cols = st.columns(4)
        with metric_cols[0]:
            render_metric("Overall score", f"{score}/10")
        with metric_cols[1]:
            render_metric("Filler words", fillers)
        with metric_cols[2]:
            render_metric("Sentiment", sentiment)
        with metric_cols[3]:
            render_metric("Structure", structure)

        insight_col, keyword_col = st.columns([1.4, 1])

        with insight_col:
            with st.container(border=True):
                st.markdown("#### Core Feedback")
                if fillers > 3:
                    st.warning("Too many filler words. Tighten your phrasing and pause instead of filling space.")
                if sentiment < 0:
                    st.warning("Your tone reads a bit uncertain. Use more direct and confident language.")
                if structure == "Too short":
                    st.warning("The answer needs more substance. Add an example, action, or result.")
                elif structure == "Too long":
                    st.warning("The answer is drifting. Cut repetition and prioritize the strongest points.")
                else:
                    st.success("The answer length is in a solid range.")
                if len(missing) > 2:
                    st.warning("You missed several expected talking points for this question.")

        with keyword_col:
            with st.container(border=True):
                st.markdown("#### Keyword Coverage")
                st.write(f"Matched: {', '.join(matched) if matched else 'None'}")
                st.write(f"Missing: {', '.join(missing) if missing else 'None'}")

        st.markdown("### AI Coaching")
        ai_feedback, ai_error = generate_ai_feedback(
            answer,
            question,
            fillers,
            sentiment,
            structure,
            matched,
            missing,
        )

        if ai_feedback:
            with st.container(border=True):
                st.markdown(ai_feedback)
        else:
            st.caption("AI coaching unavailable, showing rule-based guidance only.")
            if ai_error:
                st.error(f"AI error: {ai_error}")
