"""AI Rx Live Demo Studio entry point with task-based navigation."""

import streamlit as st


pages = {
    "Start": [
        st.Page("pages/01_Home.py", title="Home", icon="🏠", default=True),
        st.Page("pages/02_Find_A_Tool.py", title="Guided start", icon="🧭"),
    ],
    "Workshop": [
        st.Page("pages/10_Prompt_Library.py", title="Prompt library", icon="📋"),
        st.Page("pages/11_Synthetic_Cases.py", title="AI vs Doctor cases", icon="⚖️"),
        st.Page("pages/04_Live_Demos.py", title="Live demonstrations", icon="▶️"),
        st.Page("pages/17_Decision_Support.py", title="Decision support", icon="🧠"),
        st.Page("pages/12_Assessment.py", title="Assessment", icon="✅"),
    ],
    "Practice labs": [
        st.Page("pages/06_Documentation_Lab.py", title="Documentation", icon="📝"),
        st.Page("pages/05_Research_Lab.py", title="Research and evidence", icon="📚"),
        st.Page("pages/09_Workflow_Lab.py", title="Workflow design", icon="🗂️"),
        st.Page("pages/07_Social_Media_Lab.py", title="Professional communication", icon="📣"),
        st.Page("pages/08_Precision_Diagnostics.py", title="Diagnostic AI awareness", icon="🩻"),
    ],
    "Explore and download": [
        st.Page("pages/03_Tool_Directory.py", title="Tool directory", icon="🧰"),
        st.Page("pages/13_Ethics_and_Safety.py", title="Ethics and safety", icon="🛡️"),
        st.Page("pages/18_Publicity_and_PPTs.py", title="Resource centre", icon="⬇️"),
    ],
    "Faculty": [
        st.Page("pages/14_Facilitator_Mode.py", title="Facilitator mode", icon="🎙️"),
        st.Page("pages/16_Catalogue_Admin.py", title="Catalogue admin", icon="⚙️"),
        st.Page("pages/15_About.py", title="Developer expertise", icon="👤"),
    ],
    "Finish": [
        st.Page("pages/19_Session_Feedback.py", title="Session feedback", icon="💬"),
    ],
}


navigation = st.navigation(pages, position="sidebar", expanded=True)
navigation.run()
