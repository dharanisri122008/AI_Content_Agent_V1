import streamlit as st
import json
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from docx import Document
from datetime import datetime

from agents.research_agent import research_content
from agents.content_agent import create_content
from agents.review_agent import review_content
from agents.schedule_agent import create_schedule
from agents.strategy_agent import create_strategy

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Content Command Center",
    page_icon="🤖",
    layout="wide"
)

# Initialize Session State variables safely
if "generated_content" not in st.session_state:
    history = []
    try:
        with open("history.json", "r") as f:
            history = json.load(f)
    except:
        history = []

    if history:
        st.session_state.generated_content = history[-1]["content"]
    else:
        st.session_state.generated_content = ""

if "agent_status" not in st.session_state:
    st.session_state.agent_status = {
        "Research Agent": "Waiting",
        "Strategy Agent": "Waiting",
        "Content Agent": "Waiting",
        "Review Agent": "Waiting",
        "Schedule Agent": "Waiting"
    }    

# FIX 1: Initialize agent_output to prevent KeyErrors during content generation
if "agent_output" not in st.session_state:
    st.session_state.agent_output = {
        "Research Agent": "No output yet",
        "Strategy Agent": "No output yet",
        "Content Agent": "No output yet",
        "Review Agent": "No output yet",
        "Schedule Agent": "No output yet"
    }

# ---------------- PREMIUM STYLE ----------------

st.markdown("""
<style>
.main {
    background-color:#0b1220;
}
h1, h2, h3 {
    color:white;
}
.card {
    background: rgba(255,255,255,0.08);
    padding:25px;
    border-radius:20px;
    border:1px solid rgba(255,255,255,0.15);
    box-shadow:0 10px 30px rgba(0,0,0,0.35);
    margin-bottom:20px;
}
.stButton button {
    width:100%;
    border-radius:12px;
    height:45px;
}
.stMetric {
    background:rgba(255,255,255,0.08);
    padding:15px;
    border-radius:15px;
}
[data-testid="stSidebar"] {
    background:#070d18;
}
</style>
""", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------

def analyze_content(text):
    words = len(text.split())
    sentences = text.count(".")
    score = 50

    if words > 100:
        score += 20
    if words > 300:
        score += 10
    if sentences > 5:
        score += 10
    if words / max(sentences, 1) < 20:
        score += 10

    return min(score, 100)

def create_pdf(content):
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(content, styles["Normal"]))
    pdf.build(story)
    buffer.seek(0)
    return buffer

def create_docx(content):
    doc = Document()
    doc.add_paragraph(content)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer    

def load_history():
    try:
        with open("history.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_history(topic, audience, content, schedule):
    history = load_history()
    history.append({
        "id": len(history) + 1,
        "time": str(datetime.now()),
        "topic": topic,
        "audience": audience,
        "word_count": len(content.split()),
        "quality": analyze_content(content),
        "content": content,
        "schedule": schedule
    })
    with open("history.json", "w") as f:
        json.dump(history, f, indent=4)

# ---------------- SIDEBAR ----------------

st.sidebar.title("🤖 AI Command Center")
page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Create Content",
        "Agent Workflow",
        "History",
        "Analytics",
        "Settings"
    ]
)
st.sidebar.success("● Agents Active")

# ---------------- DASHBOARD ----------------

if page == "Dashboard":
    st.title("🤖 AI Content Command Center")
    history = load_history()
    total = len(history)

    if total > 0:
        avg_quality = sum(x.get("quality", 0) for x in history) / total
    else:
        avg_quality = 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Contents Generated", total)
    col2.metric("Average Quality", f"{avg_quality:.1f}%")
    col3.metric("Time Saved", f"{total*2} hrs")
    col4.metric("Agents", "5 Active")

    st.divider()
    st.subheader("⚡ Agent Status")
    agents = [
        "🔍 Research Agent",
        "🧠 Strategy Agent",
        "✍️ Content Agent",
        "🧐 Review Agent",
        "📅 Schedule Agent"
    ]

    for agent in agents:
        st.success(agent + "  • Active")

    st.divider()
    st.subheader("📈 Recent Content")
    if history:
        for item in history[-3:]:
            st.write("•", item.get("topic", "Untitled"))
    else:
        st.info("Generate content to see analytics")

# ---------------- CREATE CONTENT ----------------

elif page == "Create Content":
    st.title("✍️ Create Content")
    topic = st.text_input("What content do you want to create?")
    audience = st.text_input("Target Audience")

    if st.button("🚀 Generate Content"):
        progress = st.progress(0)

        research_status = st.empty()
        strategy_status = st.empty()
        content_status = st.empty()
        review_status = st.empty()
        schedule_status = st.empty()

        # Research Agent
        st.session_state.agent_status["Research Agent"] = "Working..."
        research_status.info("🔍 Research Agent: Working...")
        research = research_content(topic, audience)
        st.session_state.agent_output["Research Agent"] = str(research)[:200]
        research_status.success("🔍 Research Agent: Completed ✅")
        st.session_state.agent_status["Research Agent"] = "Completed ✅"
        progress.progress(20)

        # Strategy Agent
        st.session_state.agent_status["Strategy Agent"] = "Working..."
        strategy_status.info("🧠 Strategy Agent: Working...")
        strategy = create_strategy(research)
        st.session_state.agent_output["Strategy Agent"] = str(strategy)[:200]
        strategy_status.success("🧠 Strategy Agent: Completed ✅")
        st.session_state.agent_status["Strategy Agent"] = "Completed ✅"
        progress.progress(40)

        # Content Agent
        st.session_state.agent_status["Content Agent"] = "Working..."
        content_status.info("✍️ Content Agent: Working...")
        content = create_content(strategy)
        st.session_state.agent_output["Content Agent"] = str(content)[:200] 
        content_status.success("✍️ Content Agent: Completed ✅")
        st.session_state.agent_status["Content Agent"] = "Completed ✅"
        progress.progress(60)

        # Review Agent
        st.session_state.agent_status["Review Agent"] = "Working..."        
        review_status.info("🧐 Review Agent: Working...")
        reviewed = review_content(content)
        st.session_state.agent_output["Review Agent"] = str(reviewed)[:200]
        review_status.success("🧐 Review Agent: Completed ✅")
        st.session_state.agent_status["Review Agent"] = "Completed ✅"
        progress.progress(80)

        # Schedule Agent
        st.session_state.agent_status["Schedule Agent"] = "Working..." 
        schedule_status.info("📅 Schedule Agent: Working...")
        schedule = create_schedule(reviewed)
        st.session_state.agent_output["Schedule Agent"] = str(schedule)[:200]
        schedule_status.success("📅 Schedule Agent: Completed ✅")
        st.session_state.agent_status["Schedule Agent"] = "Completed ✅"
        progress.progress(100)

        save_history(topic, audience, reviewed, schedule)
        st.divider()

        st.session_state.generated_content = reviewed
        st.subheader("📝 Content Workspace")

        edited_content = st.text_area(
              "Edit your content",
               st.session_state.generated_content,
               height=350
        )

        if st.button("🔄 Re-review Edited Content"):
            updated_review = review_content(edited_content)
            st.session_state.generated_content = updated_review
            st.success("Content improved")

        st.subheader("Final Version")
        st.write(st.session_state.generated_content)

        st.subheader("Publishing Schedule")
        st.write(schedule)

        score = analyze_content(st.session_state.generated_content)
        words = len(st.session_state.generated_content.split())
        seo_score = min(60 + (words // 10), 100)

        col1, col2, col3 = st.columns(3)
        col1.metric("Quality Score", f"{score}%")
        col2.metric("SEO Score", f"{seo_score}%")
        col3.metric("Word Count", words)

        st.download_button("⬇ Download TXT", st.session_state.generated_content, "content.txt")
        st.download_button("📄 Download PDF", create_pdf(st.session_state.generated_content), "content.pdf")
        st.download_button("📝 Download DOCX", create_docx(st.session_state.generated_content), "content.docx")

# ---------------- AGENT WORKFLOW ----------------

elif page == "Agent Workflow":
    st.title("🤖 Agent Workflow Pipeline")

    agents = [
        {"name":"🔍 Research Agent", "role":"Collects trends, data and references", "status":"Completed"},
        {"name":"🧠 Strategy Agent", "role":"Creates content structure and plan", "status":"Completed"},
        {"name":"✍️ Content Agent", "role":"Generates professional content", "status":"Completed"},
        {"name":"🧐 Review Agent", "role":"Improves quality and SEO", "status":"Completed"},
        {"name":"📅 Schedule Agent", "role":"Prepares publishing schedule", "status":"Completed"}
    ]

    # FIX 2: Fixed indentation for the workflow layout block
    for index, agent in enumerate(agents):
        agent_name = (
            agent["name"]
            .replace("🔍 ","")
            .replace("🧠 ","")
            .replace("✍️ ","")
            .replace("🧐 ","")
            .replace("📅 ","")
        )

        status = st.session_state.agent_status.get(agent_name, "Waiting")
        output = st.session_state.agent_output.get(agent_name, "No output yet")

        st.markdown(
            f"""
            <div class="card">
            <h3>{agent['name']}</h3>
            <p>{agent['role']}</p>
            <b>Status:</b> {status}
            <br><br>
            <b>Output Preview:</b>
            <p>{output[:200]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if index < len(agents) - 1:
            st.markdown("<h2 style='text-align:center'>↓</h2>", unsafe_allow_html=True)

# ---------------- HISTORY ----------------

elif page == "History":
    st.title("📜 Content History")
    history = load_history()

    if not history:
        st.info("No content generated yet.")
    else:
        total_items = len(history)
        for i, item in enumerate(reversed(history)):
            topic = item.get("topic", "Untitled")
            actual_number = total_items - i 
            
            with st.expander(f"📦 Content #{actual_number} — {topic}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"📅 **Generated:** {item.get('time', 'Unknown')}")
                    st.caption(f"👥 **Audience:** {item.get('audience', 'Unknown')}")
                with col2:
                    content = item.get("content", "")
                    st.caption(f"⏱️ **Word Count:** {item.get('word_count', len(content.split()))}")
                    st.caption(f"🎯 **Quality Score:** {item.get('quality', 0)}%")
                
                st.divider()
                st.write(content)

# ---------------- ANALYTICS ----------------

elif page == "Analytics":
    st.title("📊 Analytics")
    history = load_history()
    total = len(history)

    if total > 0:
        avg = sum(x.get("quality", 0) for x in history) / total
        st.metric("Average Quality", f"{avg:.1f}%")
    else:
        st.info("No analytics available")

# ---------------- SETTINGS ----------------

elif page == "Settings":
    st.title("⚙️ Settings")
    st.info("AI model and configuration settings")