import streamlit as st
import io
import sys
import threading
import time

from agents import (
    researcher_agent,
    writer_agent,
    reviewer_agent,
    manager_agent
)

from tasks import create_tasks
from crew import create_crew

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="AI Research Command Center",
    page_icon="🤖",
    layout="wide"
)

# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.agent-box {
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #333;
    margin-bottom: 10px;
    background-color: #111111;
}

.metric-box {
    padding: 10px;
    border-radius: 10px;
    border: 1px solid #444;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# HEADER
# ==================================================

st.title("🤖 AI Research Command Center")

st.caption(
    "CrewAI Hierarchical Multi-Agent System | Gemini Manager | Ollama Workers | Internet Research"
)

st.divider()

# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.header("⚙️ Agent Architecture")

    st.success("🧠 Manager\nGemini 2.5 Flash")

    st.info("🔎 Researcher\nMistral + Serper")

    st.info("✍ Writer\nMistral")

    st.info("✅ Reviewer\nMistral")

    st.divider()

    st.markdown("""
### Workflow

User Request

⬇

Manager

⬇

Researcher

⬇

Writer

⬇

Reviewer

⬇

Final Report
""")

# ==================================================
# TOP INPUT AREA
# ==================================================

topic = st.text_input(
    "Enter Research Topic",
    placeholder="Example: CrewAI vs LangGraph in 2026"
)

# ==================================================
# STATUS AREA
# ==================================================

st.subheader("📊 Agent Status")

c1, c2, c3, c4 = st.columns(4)

manager_card = c1.empty()
research_card = c2.empty()
writer_card = c3.empty()
review_card = c4.empty()

manager_card.info("🧠 Manager\nWaiting")
research_card.info("🔎 Researcher\nWaiting")
writer_card.info("✍ Writer\nWaiting")
review_card.info("✅ Reviewer\nWaiting")

# ==================================================
# EXECUTION METRICS
# ==================================================

metric_col1, metric_col2 = st.columns(2)

timer_metric = metric_col1.empty()
status_metric = metric_col2.empty()

timer_metric.metric(
    "Execution Time",
    "0 sec"
)

status_metric.metric(
    "Crew Status",
    "Idle"
)

st.divider()

# ==================================================
# MAIN PANELS
# ==================================================

left_col, right_col = st.columns([1, 2])

with left_col:

    st.subheader("📡 Live Activity")

    activity_box = st.empty()

with right_col:

    st.subheader("📄 Final Report")

    result_box = st.empty()

# ==================================================
# RUN BUTTON
# ==================================================

if st.button("🚀 Run Research Crew", use_container_width=True):

    if not topic.strip():

        st.warning("Please enter a topic.")

    else:

        start_time = time.time()

        status_metric.metric(
            "Crew Status",
            "Running"
        )

        log_stream = io.StringIO()

        old_stdout = sys.stdout

        sys.stdout = log_stream

        result_container = {}

        manager_card.warning("🧠 Manager\nRunning")

        def run_crew():

            try:

                tasks = create_tasks(topic)

                crew = create_crew(
                    researcher_agent,
                    writer_agent,
                    reviewer_agent,
                    manager_agent,
                    tasks
                )

                result = crew.kickoff()

                result_container["result"] = result

            except Exception as e:

                result_container["result"] = str(e)

        thread = threading.Thread(target=run_crew)

        thread.start()

        previous_logs = ""

        while thread.is_alive():

            logs = log_stream.getvalue()

            elapsed = int(time.time() - start_time)

            timer_metric.metric(
                "Execution Time",
                f"{elapsed} sec"
            )

            # --------------------------------------
            # STATUS DETECTION
            # --------------------------------------

            lower_logs = logs.lower()

            if "manager" in lower_logs:
                manager_card.success("🧠 Manager\nActive")

            if "research" in lower_logs:
                research_card.success("🔎 Researcher\nActive")

            if "writer" in lower_logs:
                writer_card.success("✍ Writer\nActive")

            if "review" in lower_logs:
                review_card.success("✅ Reviewer\nActive")

            if logs != previous_logs:

                activity_box.code(
                    logs[-8000:],
                    language="text"
                )

                previous_logs = logs

            time.sleep(1)

        thread.join()

        sys.stdout = old_stdout

        final_logs = log_stream.getvalue()

        activity_box.code(
            final_logs[-10000:],
            language="text"
        )

        manager_card.success("🧠 Manager\nCompleted")
        research_card.success("🔎 Researcher\nCompleted")
        writer_card.success("✍ Writer\nCompleted")
        review_card.success("✅ Reviewer\nCompleted")

        elapsed = int(time.time() - start_time)

        timer_metric.metric(
            "Execution Time",
            f"{elapsed} sec"
        )

        status_metric.metric(
            "Crew Status",
            "Completed"
        )

        result_box.markdown(
            result_container.get(
                "result",
                "No result returned."
            )
        )

        st.success("Research Crew Completed Successfully")