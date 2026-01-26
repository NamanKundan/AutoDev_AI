import streamlit as st
import time
import os
import zipfile
import io
from agent.graph import agent
from agent.tools import init_project_root

def create_project_zip(project_path):
    """Create a ZIP file containing all project files"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Walk through all files in the project directory
        for root, dirs, files in os.walk(project_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Create archive name (relative path from project root)
                arcname = os.path.relpath(file_path, project_path)
                zip_file.write(file_path, arcname)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

# Page config
st.set_page_config(
    page_title="AutoDev AI - Autonomous Code Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS with glassmorphism and black/white/grey theme
st.markdown("""
<style>
    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
    }
    
    /* Professional gradient background - black to dark grey */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #2a2a2a 100%);
        background-size: 400% 400%;
        animation: subtleGradient 15s ease infinite;
    }
    
    @keyframes subtleGradient {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Glassmorphism container */
    .main .block-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        padding: 3rem 2.5rem !important;
        max-width: 1200px !important;
        margin: 2rem auto !important;
        animation: fadeInUp 0.6s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Professional typography */
    .main-title {
        font-size: 3.8rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        text-align: center;
        letter-spacing: -1px;
        margin-bottom: 0.5rem !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .subtitle {
        font-size: 1.1rem !important;
        color: rgba(255, 255, 255, 0.6) !important;
        letter-spacing: 2px !important;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 3rem !important;
        font-weight: 300;
    }
    
    /* Glassmorphism text area */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(10px);
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        font-size: 15px !important;
        min-height: 150px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    .stTextArea textarea:focus {
        background: rgba(255, 255, 255, 0.12) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.05) !important;
    }
    
    .stTextArea textarea::placeholder {
        color: rgba(255, 255, 255, 0.4) !important;
    }
    
    /* Professional buttons */
    .stButton > button {
        width: 100% !important;
        background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 14px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(255, 255, 255, 0.15) !important;
        background: linear-gradient(135deg, #3a3a3a 0%, #2a2a2a 100%) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Primary button - Generate Project */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%) !important;
        color: #000000 !important;
        border: 2px solid rgba(255, 255, 255, 0.8) !important;
        box-shadow: 0 6px 30px rgba(255, 255, 255, 0.3) !important;
        font-weight: 700 !important;
        padding: 16px 32px !important;
        font-size: 15px !important;
    }
    
    .stButton button[kind="primary"]:hover {
        background: #ffffff !important;
        color: #000000 !important;
        box-shadow: 0 10px 40px rgba(255, 255, 255, 0.5) !important;
        transform: translateY(-3px) scale(1.02) !important;
    }
    
    /* Force primary button text color */
    .stButton button[kind="primary"] p,
    .stButton button[kind="primary"] span,
    .stButton button[kind="primary"] div {
        color: #000000 !important;
    }
    
    /* Glassmorphism metrics cards */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        background: rgba(255, 255, 255, 0.12);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.6) !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 500;
    }
    
    /* Professional alerts */
    .stAlert {
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(10px);
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        padding: 1.2rem 1.5rem !important;
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    .stSuccess {
        border-left: 3px solid #4caf50 !important;
    }
    
    .stInfo {
        border-left: 3px solid #2196f3 !important;
    }
    
    .stWarning {
        border-left: 3px solid #ff9800 !important;
    }
    
    .stError {
        border-left: 3px solid #f44336 !important;
    }
    
    /* Progress bar */
    .stProgress > div {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        overflow: hidden;
        height: 8px !important;
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, #ffffff 0%, #cccccc 100%) !important;
        border-radius: 10px !important;
    }
    
    /* Code blocks */
    code {
        background: rgba(0, 0, 0, 0.4) !important;
        color: #ffffff !important;
        padding: 4px 10px !important;
        border-radius: 6px !important;
        border: 1px solid rgba(255, 255, 255, 0.15);
        font-family: 'Consolas', 'Monaco', monospace !important;
        font-size: 13px !important;
    }
    
    pre {
        background: rgba(0, 0, 0, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 1.2rem !important;
        backdrop-filter: blur(10px);
    }
    
    /* Expander glassmorphism */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        color: rgba(255, 255, 255, 0.9) !important;
        padding: 0.8rem 1rem !important;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.12) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Text colors */
    .stMarkdown, p, span, label, div {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: rgba(255, 255, 255, 0.2) !important;
    }
    
    .stSlider > div > div > div > div {
        background: #ffffff !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    
    /* Remove anchor links */
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a {
        display: none !important;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
        margin: 1.5rem 0 1rem 0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'project_generated' not in st.session_state:
    st.session_state.project_generated = False
if 'generation_time' not in st.session_state:
    st.session_state.generation_time = 0
if 'result' not in st.session_state:
    st.session_state.result = None
if 'prompt_input' not in st.session_state:
    st.session_state.prompt_input = ""
if 'groq_api_key' not in st.session_state:
    st.session_state.groq_api_key = ""


# Header with professional design
st.markdown("""
<div style="text-align: center; margin-bottom: 3.5rem;">
    <div class="main-title">AutoDev AI</div>
    <div class="subtitle">Intelligent Code Generation Platform</div>
</div>
""", unsafe_allow_html=True)

# Main content in professional layout
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    # API Key input - always visible
    api_key_input = st.text_input(
        "Groq API Key",
        value=st.session_state.groq_api_key,
        type="password",
        help="Enter your Groq API key. Get one from https://console.groq.com",
        placeholder="Enter your API key here..."
    )
    if api_key_input:
        st.session_state.groq_api_key = api_key_input
    
    # Complexity slider - always visible
    recursion_limit = st.slider("Complexity Level", 50, 200, 100, 10, 
                               help="Lower = Faster & Simpler | Higher = More Complex & Detailed")
    
    # Store in session state
    st.session_state.recursion_limit = recursion_limit
    
    # Quick start examples
    st.markdown('<div class="section-header">Quick Start</div>', unsafe_allow_html=True)
    
    # Dynamic examples based on recursion limit
    if recursion_limit <= 75:
        examples = [
            ("Calculator", "Create a simple calculator with HTML, CSS, and JavaScript"),
            ("Todo List", "Build a basic todo list with local storage"),
            ("Dice Game", "Create a simple dice rolling game")
        ]
    elif recursion_limit <= 125:
        examples = [
            ("Calculator", "Create a calculator web app with HTML, CSS, and JavaScript with memory functions"),
            ("Todo List", "Build a todo list app with local storage, filters, and edit functionality"),
            ("REST API", "Create a FastAPI REST API with SQLite database and basic CRUD operations")
        ]
    else:
        examples = [
            ("Calculator", "Create an advanced calculator with HTML, CSS, and JavaScript featuring scientific functions, history, and keyboard support"),
            ("Todo List", "Build a comprehensive todo list app with local storage, categories, due dates, search, and import/export features"),
            ("REST API", "Create a complete FastAPI REST API with SQLite database, authentication, data validation, and API documentation")
        ]
    
    # Example buttons in horizontal layout
    ex_cols = st.columns(3)
    for i, (short, full) in enumerate(examples):
        with ex_cols[i]:
            if st.button(short, key=f"ex_{i}", use_container_width=True):
                st.session_state.prompt_input = full
    
    # Main input section
    st.markdown('<div class="section-header">Project Description</div>', unsafe_allow_html=True)
    
    user_prompt = st.text_area(
        "Describe your project",
        value=st.session_state.prompt_input,
        height=150,
        placeholder="Example: Create a modern weather dashboard with HTML, CSS, and JavaScript that fetches data from an API and displays current conditions and forecasts...",
        label_visibility="collapsed"
    )
    
    generate_button = st.button("Generate Project", type="primary", use_container_width=True)

if generate_button and user_prompt:
    with st.spinner("Processing your project request..."):
        start_time = time.time()
        
        # Initialize project root with unique folder
        project_root = init_project_root(user_prompt)
        
        # Progress tracking with interactive indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Create status indicators container
        status_container = st.container()
        with status_container:
            col1, col2, col3 = st.columns(3)
            with col1:
                planner_status = st.empty()
            with col2:
                architect_status = st.empty()
            with col3:
                coder_status = st.empty()
        
        try:
            # Initialize status indicators
            planner_status.markdown("**Planner** • Starting...")
            architect_status.markdown("**Architect** • Waiting...")
            coder_status.markdown("**Coder** • Waiting...")
            
            # Phase 1: Planning with dynamic updates
            planner_status.markdown("**Planner** • Analyzing request...")
            status_text.text("Planner Agent: Analyzing your request...")
            progress_bar.progress(5)
            time.sleep(0.2)
            
            planner_status.markdown("**Planner** • Understanding requirements...")
            status_text.text("Planner Agent: Understanding project requirements...")
            progress_bar.progress(10)
            time.sleep(0.3)
            
            planner_status.markdown("**Planner** • Identifying technologies...")
            status_text.text("Planner Agent: Identifying technologies needed...")
            progress_bar.progress(15)
            time.sleep(0.2)
            
            planner_status.markdown("**Planner** • Complete")
            status_text.text("Planner Agent: Creating project structure...")
            progress_bar.progress(20)
            
            # Phase 2: Architecture with dynamic updates
            architect_status.markdown("**Architect** • Breaking down tasks...")
            status_text.text("Architect Agent: Breaking down into tasks...")
            progress_bar.progress(25)
            time.sleep(0.3)
            
            architect_status.markdown("**Architect** • Planning dependencies...")
            status_text.text("Architect Agent: Planning file dependencies...")
            progress_bar.progress(30)
            time.sleep(0.2)
            
            architect_status.markdown("**Architect** • Complete")
            status_text.text("Architect Agent: Organizing implementation steps...")
            progress_bar.progress(35)
            time.sleep(0.3)
            
            # Run the agent
            status_text.text("AI Agent: Starting project generation...")
            progress_bar.progress(40)
            
            result = agent.invoke(
                {"user_prompt": user_prompt},
                {"recursion_limit": recursion_limit}
            )
            
            # Phase 3: Coding with dynamic updates
            coder_status.markdown("**Coder** • Creating HTML...")
            status_text.text("Coder Agent: Creating HTML structure...")
            progress_bar.progress(50)
            time.sleep(0.4)
            
            coder_status.markdown("**Coder** • Writing CSS...")
            status_text.text("Coder Agent: Writing CSS styles...")
            progress_bar.progress(65)
            time.sleep(0.3)
            
            coder_status.markdown("**Coder** • JavaScript logic...")
            status_text.text("Coder Agent: Implementing JavaScript logic...")
            progress_bar.progress(80)
            time.sleep(0.4)
            
            coder_status.markdown("**Coder** • Documentation...")
            status_text.text("Coder Agent: Generating documentation...")
            progress_bar.progress(90)
            time.sleep(0.2)
            
            coder_status.markdown("**Coder** • Complete")
            status_text.text("Finalizing project files...")
            progress_bar.progress(95)
            
            end_time = time.time()
            generation_time = end_time - start_time
            
            progress_bar.progress(100)
            status_text.text("Project generated successfully")
            
            # Success animation effect
            st.balloons()
            time.sleep(0.3)
            
            # Store results
            st.session_state.project_generated = True
            st.session_state.generation_time = generation_time
            st.session_state.result = result
            
            # Success message
            st.success(f"Project generated in {generation_time:.2f} seconds")
            
            # Metrics
            st.markdown('<p style="font-size: 1.1rem; color: #ffffff; font-weight: 600; margin-top: 1.5rem; letter-spacing: 0.5px;">Generation Metrics</p>', unsafe_allow_html=True)
            
            plan = result.get('plan')
            col_m1, col_m2, col_m3 = st.columns(3)
            
            with col_m1:
                st.metric("Time", f"{generation_time:.1f}s")
            with col_m2:
                files_count = len(plan.files) if plan and hasattr(plan, 'files') else 0
                st.metric("Files", files_count)
            with col_m3:
                estimated_tokens = len(user_prompt) * 50
                tokens_per_sec = int(estimated_tokens / generation_time) if generation_time > 0 else 0
                st.metric("Speed", f"{tokens_per_sec} t/s")
            
            # Files
            st.markdown('<p style="font-size: 1.1rem; color: #ffffff; font-weight: 600; margin-top: 1.5rem; letter-spacing: 0.5px;">Generated Files</p>', unsafe_allow_html=True)
            if plan and hasattr(plan, 'files'):
                for file in plan.files:
                    st.markdown(f"- `{file.path}` - {file.purpose}")
            
            # Location
            st.markdown('<p style="font-size: 1.1rem; color: #ffffff; font-weight: 600; margin-top: 1.5rem; letter-spacing: 0.5px;">Project Location</p>', unsafe_allow_html=True)
            st.code(project_root, language="bash")
            
            # Download button
            st.markdown('<p style="font-size: 1.1rem; color: #ffffff; font-weight: 600; margin-top: 1.5rem; letter-spacing: 0.5px;">Download Project</p>', unsafe_allow_html=True)
            try:
                if os.path.exists(project_root) and os.listdir(project_root):
                    zip_data = create_project_zip(project_root)
                    project_name = user_prompt.replace(" ", "_").replace(",", "")[:30]  # Clean filename
                    st.download_button(
                        label="Download ZIP File",
                        data=zip_data,
                        file_name=f"{project_name}_project.zip",
                        mime="application/zip",
                        type="primary"
                    )
                    st.success("Your project is ready for download")
                else:
                    st.warning("No files were generated to download")
            except Exception as e:
                st.error(f"Error creating download: {str(e)}")
            
            # Next steps
            st.markdown('<p style="font-size: 1.1rem; color: #ffffff; font-weight: 600; margin-top: 1.5rem; letter-spacing: 0.5px;">Next Steps</p>', unsafe_allow_html=True)
            st.markdown("""
            1. **Download the ZIP file** using the button above
            2. **Extract** the ZIP file to your desired location
            3. **Open `index.html`** in a browser (for web projects)
            4. **Or run** the appropriate command for your project type
            """)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            progress_bar.progress(0)
            status_text.text("")

elif generate_button and not user_prompt:
    st.warning("Please describe your project first")

# Close the main column
st.markdown("---")

# Footer with professional styling
st.markdown("""
<div style='text-align: center; padding: 40px 20px; margin-top: 2rem; background: rgba(255, 255, 255, 0.03); border-radius: 16px; backdrop-filter: blur(10px);'>
    <p style='font-size: 0.95rem; font-weight: 500; margin-bottom: 15px; color: rgba(255, 255, 255, 0.6); letter-spacing: 1px;'>
        POWERED BY
    </p>
    <p style='font-size: 1.1rem; font-weight: 600; margin-bottom: 25px; color: rgba(255, 255, 255, 0.9);'>
        LangGraph × Groq AI
    </p>
    <p style='font-size: 2.8rem; font-weight: 900; margin: 15px 0; color: #ffffff; letter-spacing: -1px;'>
        AutoDev AI
    </p>
    <p style='font-size: 1rem; color: rgba(255, 255, 255, 0.7); margin-top: 15px; letter-spacing: 0.5px;'>
        Transform Ideas into Code, Instantly
    </p>
</div>
""", unsafe_allow_html=True)
