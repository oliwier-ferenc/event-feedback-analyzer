import time
import streamlit as st

from src.ui.components import render_header, render_sidebar, render_results, show_error
from src.utils import fetch_survey_data
from src.agent import analyze_feedback_with_ai

# Page Configuration
st.set_page_config(page_title="Event Feedback AI Analyzer", layout="wide")

render_header()
data_source, mock_mode, user_api_key = render_sidebar()

if mock_mode:
    st.markdown(
        """
        <div class="mock-notice">
        <b>Mock Mode is Enabled</b><br>
        1. Bypassing real data ingestion and Gemini API calls.<br>
        2. Displaying pre-generated sample insights for demonstration purposes. 
        </div>
        """,
        unsafe_allow_html=True
    )


if st.sidebar.button("Fetch & Analyze Responses", type="primary"):
    if not data_source and not mock_mode:
        st.warning("Please provide a Google Sheet URL or upload a supported file in the sidebar.")
    else:
        try:
            if mock_mode:
                df = None
                with st.spinner("Simulating AI Analysis..."):
                    time.sleep(1.5)
                    analysis_result = analyze_feedback_with_ai(
                        df, 
                        mock_mode=True
                        )
            else:
                # Enforce 5MB file size limit for uploaded files
                if hasattr(data_source, "size") and data_source.size > 5 * 1024 * 1024:
                    raise ValueError(
                        """File size exceeds the 5MB limit. Please upload a smaller file."""
                    )

                with st.spinner("Processing survey data..."):
                    df = fetch_survey_data(data_source)

                st.success(f"Successfully loaded {len(df)} response(s)!")

                with st.spinner("Generating structured summary with Gemini..."):
                    analysis_result = analyze_feedback_with_ai(
                        df,
                        mock_mode=False,
                        user_api_key=user_api_key
                    )

            if analysis_result is None:
                show_error(
                    """
                    The AI analysis did not return any results.
                    Please check your API key and try again.
                    """
                )
            else:
                render_results(
                    df, 
                    analysis_result, 
                    mock_mode=mock_mode
                )

        except ValueError as e:
            show_error(str(e))

        except Exception:
            show_error(
                """
                Something went wrong while loading the data or generating
                the analysis. Please check your input and API settings.
                """
            )