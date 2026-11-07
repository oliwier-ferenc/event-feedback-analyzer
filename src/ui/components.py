import os
import html
import streamlit as st

def load_css():
    css_path = os.path.join("assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def show_error(message):
    message = html.escape(str(message))
    st.markdown(
        f'<div class="error-banner">{message}</div>',
        unsafe_allow_html=True
    )

def render_header():
    st.title("Event Feedback Analyzer")
    st.write("Convert Google Form or Typeform responses into structured insights using Gemini & Pydantic.")
    st.markdown("---")

def render_sidebar():
    load_css()

    st.sidebar.header("Configuration")
    
    # Let the user choose their data ingestion method
    input_method = st.sidebar.radio(
        "**Select Data Source**",
        ["Google Sheet URL", "Upload File (CSV/XLSX)", "Load Demo Data"]
    )
    
    source = None
    
    if input_method == "Google Sheet URL":
        st.sidebar.markdown(
            """
            <div class="instruction-box">
                <b>Google Sheets Instructions:</b><br>
                1. Click <b>Share</b> (top right).<br>
                2. Set access to <b>"Anyone with the link"</b>.<br>
                3. Copy and paste your Sheet link below.
            </div>
            """,
            unsafe_allow_html=True
        )
        source = st.sidebar.text_input( 
            " ",
            placeholder="Paste published CSV link here..."
        )
        
    elif input_method == "Upload File (CSV/XLSX)":
        st.sidebar.markdown(
            """
            <div class="instruction-box">
                Upload your exported <code>.csv</code> or <code>.xlsx</code> file from your survey platform's results.
            </div>
            """,
            unsafe_allow_html=True
        )
        source = st.sidebar.file_uploader(
                    " ",
                    type=["csv", "xlsx"],
                    max_upload_size=5
                )

    elif input_method == "Load Demo Data":
        demo_choice = st.sidebar.selectbox(
            "**Choose Demo Dataset**",
            ["Standard Sample Feedback (Normal)", "Adversarial Test (Prompt Injection)"]
        )

        if demo_choice == "Standard Sample Feedback (Normal)":
            st.sidebar.markdown(
                """
                <div class="demo-box">
                    <b>Demo Mode Active:</b><br>
                    Using <code>data/sample_feedback.csv</code> to test normal AI analysis.
                </div>
                """,
                unsafe_allow_html=True
            )
            source = "data/sample_feedback.csv"
        else:
            st.sidebar.markdown(
                """
                <div class="demo-box">
                    <b>Demo Mode Active:</b><br>
                    Using <code>data/test_injection.csv</code> to test prompt injection defenses.
                </div>
                """,
                unsafe_allow_html=True
            )
            source = "data/test_injection.csv"
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### App Settings")

    mock_mode = st.sidebar.checkbox(
        """Enable Mock Mode (no API Required)""",
        value=False,
        help="Bypass the Gemini API calls and use static mock data to simulate a response"
    )

    user_api_key = st.sidebar.text_input(
        """Custom API key (Optional)""",
        type="password",
        help="Provide your own Gemini API key to use the app",
        placeholder="Paste a valid Gemini API key here..."
    )

    return source, mock_mode, user_api_key

def render_results(df, summary, mock_mode=False):
    """Renders the structured Pydantic analysis output and the raw data table."""
    st.subheader("AI Executive Summary")
    st.markdown(
        """
        <div class="description">
        A structured overview of the main themes in your survey feedback.
        </div>         
        """,
        unsafe_allow_html=True
        )
    

    with st.container(border=False):
        st.markdown("### Overall Sentiment")
        st.info(summary.overall_sentiment)
        
    
    # Render Likes & Complaints side-by-side using columns
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=False):
            st.markdown("### What Attendees Loved")
            for idx, like in enumerate(summary.top_likes, 1):
                st.markdown(f"{idx}. {like}")
            
    with col2:
        with st.container(border=False):
            st.markdown("### Areas to Fix")
            for idx, complaint in enumerate(summary.top_complaints, 1):
                st.markdown(f"{idx}. {complaint}")
            
    # Render Recommendation
    with st.container(border=False):
        st.markdown("### Strategic AI Recommendation")
        st.success(summary.recommendations)

    st.markdown("---")

    if not mock_mode:
        st.subheader("Raw Survey Data")
        st.markdown(
            """
            <div class="description">
            Review the original response alongside the generated insights.
            </div>         
            """,
            unsafe_allow_html=True
        )
        st.dataframe(df)
    else:
        st.subheader("Sample insight response")
        st.markdown(
            """
            <div class="description">
            These are pre-generated example insights. No survey data was processed.
            </div>         
            """,
            unsafe_allow_html=True
        )
        st.dataframe()