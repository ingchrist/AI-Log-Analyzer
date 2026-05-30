import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from src.agents.log_analyzer import LogAnalyzerAgent
from src.config import Config
from src.memory.chat_store import ChatStore
from src.memory.incident_store import IncidentStore

st.set_page_config(page_title="AI Log Analyzer", page_icon="🔍", layout="wide")

def init_session():
    if "chat_store" not in st.session_state:
        st.session_state.chat_store = ChatStore(Config.MEMORY_DIR)
        st.session_state.incident_store = IncidentStore(Config.MEMORY_DIR)
        st.session_state.messages = st.session_state.chat_store.load()

    if "agent" not in st.session_state:
        recent = st.session_state.incident_store.get_recent(5)
        context = st.session_state.incident_store.format_for_prompt(recent)
        st.session_state.agent = LogAnalyzerAgent(incident_context=context)

init_session()

# Sidebar
with st.sidebar:
    st.title("⚙️ Memory Management")
    st.markdown("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_store.clear()
        st.session_state.messages = []
        st.rerun()

    st.subheader("💾 Save Incident")
    with st.form("save_incident"):
        summary = st.text_input("Summary", placeholder="Brief description of the incident")
        resolution = st.text_input("Resolution", placeholder="How it was resolved")
        severity = st.selectbox("Severity", ["P1", "P2", "P3"])
        if st.form_submit_button("Save Incident") and summary:
            st.session_state.incident_store.add(
                summary=summary,
                resolution=resolution,
                severity=severity
            )
            st.success("Incident saved to memory!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 🔒 Approval-Required Actions")
    st.markdown("- `restart_kubernetes_pod`")
    st.markdown("- `reboot_rds_instance`")
    st.markdown("Type **yes / confirm** to approve blocked actions.")

# Main UI
st.title("🔍 AI Log Analyzer Agent")
st.caption("Production-ready AI logging agent powered by LangChain + Gemini")

# Display chat history
for msg in st.session_state.messages:
    icon = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if prompt := st.chat_input("Ask about logs, incidents, or type 'yes' to confirm an action..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            history = [
                HumanMessage(content=m["content"]) if m["role"] == "user"
                else AIMessage(content=m["content"])
                for m in st.session_state.messages[:-1]
            ]
            response = st.session_state.agent.process_query(prompt, history)
        st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.chat_store.save(st.session_state.messages)
