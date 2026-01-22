"""
app.py
Summarization Accelerator - Enterprise Dashboard
Streamlit-based frontend integrating unified Pipeline.
"""

import streamlit as st
import yaml
import os
import time
import pandas as pd
import json
from pathlib import Path

# Download NLTK data (required for Streamlit Cloud)
import nltk

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)
    nltk.download("averaged_perceptron_tagger", quiet=True)
    nltk.download("wordnet", quiet=True)

# Import Enterprise Modules
from src.core.pipeline import SummarizationPipeline
from src.utils.config_loader import ConfigLoader
from src.utils.logger import setup_logger

logger = setup_logger("App")

# Page Config
st.set_page_config(
    page_title="Summarization Accelerator (Enterprise)",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styling
st.markdown(
    """
    <style>
    .main {background-color: #f8f9fa;}
    .stApp {max-width: 1400px; margin: 0 auto;}
    h1 {color: #1a1a1a; border-bottom: 3px solid #2563eb; padding-bottom: 1rem;}
    .stButton>button {background-color: #2563eb; color: white; width: 100%;}
    .stButton>button:hover {background-color: #1d4ed8;}
    </style>
""",
    unsafe_allow_html=True,
)

st.title("Summarization Accelerator")

# Initialize session state
if "pipeline_run" not in st.session_state:
    st.session_state.pipeline_run = False
if "pipeline_timestamp" not in st.session_state:
    st.session_state.pipeline_timestamp = None

# Sidebar
with st.sidebar:
    st.header("Configuration")

    # Input
    st.subheader("1. Input Document")
    uploaded_file = st.file_uploader(
        "Upload (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"]
    )
    input_path = None

    if uploaded_file:
        # Save to temp
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        input_path = temp_dir / uploaded_file.name
        with open(input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Loaded: {uploaded_file.name}")

    # AI Config
    st.subheader("2. AI Settings")
    api_key = st.text_input("Gemini API Key", type="password")

    styles = [
        "Standard",
        "Formal",
        "Casual",
        "Bullet Points",
        "ELI5",
        "Executive Summary",
    ]
    style = st.selectbox("Tone / Style", styles)

    # Model Config (simplified for UI)
    st.subheader("3. Models")
    run_extract = st.checkbox("Run Extractive Models", value=True)
    run_abstract = st.checkbox("Run Abstractive Models", value=True)

    # Run Button
    start_btn = st.button("RUN PIPELINE", type="primary")

# Main Area
if start_btn:
    if not input_path:
        st.error("Please upload a document first.")
    elif not api_key:
        st.error("Gemini API Key is required.")
    else:
        # Build Config Dictionary in-memory
        config = {
            "paths": {
                "input_path": str(input_path.resolve()),
                "output_text": str((Path("temp_uploads") / "converted.txt").resolve()),
            },
            "gemini": {"enabled": True, "api_key": api_key, "style": style},
            "extractive": {
                "algorithms": ["tfidf", "sumy_textrank", "sumy_lexrank"]
                if run_extract
                else []
            },
            "abstractive": {
                "default_to_run": ["bart", "t5", "flan_t5_base"]
                if run_abstract
                else [],
                "generation": {"max_length": 150, "min_length": 50},
            },
            "processing": {"use_gpu": False},
            "output": {"excel_filename": "full_summarization_report.xlsx"},
        }

        # Save config for persistence/debug
        with open("config.yaml", "w", encoding="utf-8") as f:
            yaml.dump(config, f)

        # Initialize Pipeline
        pipeline = SummarizationPipeline(config)

        # Progress UI
        progress_bar = st.progress(0, text="Initializing...")
        status_area = st.empty()

        try:
            # Run Generator
            final_results = {}
            for status, prog in pipeline.run():
                progress_bar.progress(prog, text=status)
                time.sleep(0.1)  # UI smoothness

            st.success("Analysis Complete!")
            # Mark pipeline as run in this session
            st.session_state.pipeline_run = True
            st.session_state.pipeline_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            # Trigger refresh to load tabs
            time.sleep(1)
            st.rerun()

        except Exception as e:
            st.error(f"Pipeline Failed: {e}")
            logger.error(f"UI Error: {e}")

# Visualization Tabs
st.markdown("---")

# Only show results if pipeline has been run in this session
if st.session_state.pipeline_run:
    st.caption(f"Results generated at: {st.session_state.pipeline_timestamp}")
    tabs = st.tabs(
        ["Stylized Summary", "Metrics & Report", "Traceability", "AI Insight"]
    )
else:
    st.info("👆 Please upload a document and run the pipeline to see results.")
    tabs = None

# Tab 1: Stylized
if tabs:
    with tabs[0]:
        st.subheader(" Stylized Summaries")
        st.write("The same summary, rewritten in different tones by AI:")

        # Try loading multiple versions first
        if Path("stylized_summaries.json").exists():
            try:
                with open("stylized_summaries.json", "r", encoding="utf-8") as f:
                    stylized_versions = json.load(f)

                # Display each style in a card
                for style_name, summary_text in stylized_versions.items():
                    # Style-specific colors
                    style_colors = {
                        "Formal": "#1e40af",  # Dark blue
                        "Casual": "#ea580c",  # Orange
                        "Bullet Points": "#059669",  # Green
                        "Executive Summary": "#7c3aed",  # Purple
                        "ELI5": "#dc2626",  # Red
                    }
                    border_color = style_colors.get(style_name, "#2563eb")

                    with st.expander(
                        f" {style_name}", expanded=(style_name == "Executive Summary")
                    ):
                        st.markdown(
                            f'<div style="padding:15px; background:#f8fafc; border-left:5px solid {border_color}; border-radius:5px;">{summary_text}</div>',
                            unsafe_allow_html=True,
                        )

            except Exception as e:
                st.error(f"Error loading stylized versions: {e}")
                # Fallback to single version
                if Path("stylized_summary.txt").exists():
                    with open("stylized_summary.txt", "r", encoding="utf-8") as f:
                        st.markdown(
                            f'<div style="padding:15px; background:#fff; border-left:5px solid #2563eb;">{f.read()}</div>',
                            unsafe_allow_html=True,
                        )
        elif Path("stylized_summary.txt").exists():
            # Fallback for old single-version format
            with open("stylized_summary.txt", "r", encoding="utf-8") as f:
                st.markdown(
                    f'<div style="padding:15px; background:#fff; border-left:5px solid #2563eb;">{f.read()}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("Run pipeline to see results.")

    # Tab 2: Report
    with tabs[1]:
        df = pd.DataFrame()
        if Path("full_summarization_report.xlsx").exists():
            try:
                df = pd.read_excel(
                    "full_summarization_report.xlsx", sheet_name="All Results"
                )
            except Exception as e:
                st.error(f"Error reading Excel file: {e}")
                df = pd.DataFrame()

        if not df.empty:
            # --- NEW: Integrated Insights ---
            st.subheader(" Smart Analysis & Recommendations")

            # Metrics Reference Table
            with st.expander(" Metrics Glossary - What do these numbers mean?"):
                st.markdown("""
                ### Quality Metrics (Higher is Better)
                
                | Metric | Range | What it Measures | Interpretation |
                |--------|-------|------------------|----------------|
                | **ROUGE-1 F1** | 0-100% | Unigram (single word) overlap with original | **60-80%**: Good content preservation<br>**>80%**: Excellent coverage<br>**<60%**: Significant information loss |
                | **ROUGE-2 F1** | 0-100% | Bigram (2-word phrase) overlap | Measures phrase-level accuracy |
                | **ROUGE-L F1** | 0-100% | Longest common subsequence | Evaluates sentence structure preservation |
                | **BLEU Score** | 0-100% | N-gram precision across all levels | Overall quality match with original |
                | **METEOR** | 0-100% | Advanced matching with synonyms | More nuanced quality (considers paraphrasing) |
                | **Cosine Similarity** | 0-100% | Semantic similarity (meaning-based) | **>70%**: Preserves core meaning<br>**50-70%**: Partial similarity<br>**<50%**: Significant drift |
                | **Density %** | 0-100% | Vocabulary richness (unique words / total words) | **60-85%**: Well-balanced<br>**>85%**: Very information-dense<br>**<60%**: Repetitive |
                
                ### Efficiency Metrics (Context-Dependent)
                
                | Metric | Range | What it Measures | Interpretation |
                |--------|-------|------------------|----------------|
                | **Compression %** | 0-100% | Summary size relative to original | **15-25%**: Highly concise<br>**25-40%**: Moderate compression<br>**>40%**: Minimal compression |
                | **Time (s)** | 0-∞ | Processing speed | **<1s**: Instant (extractive)<br>**1-10s**: Fast (small abstractive models)<br>**>10s**: Slow (large models or long docs) |
                
                ### Quick Decision Guide
                - **For Legal/Medical**: Prioritize high **ROUGE-1** (>75%) and **Cosine Sim** (>80%)
                - **For Social Media**: Low **Compression** (<20%) and high **Density** (>70%)
                - **For Real-Time Apps**: **Time** <1s, acceptable **ROUGE** >60%
                - **For Reports**: Balance **ROUGE** >70% with **Density** >65%
                """)

            # Detect the model/method identifier column
            model_col = None
            for col_name in ["Method/Model", "Model", "Method", "Algorithm"]:
                if col_name in df.columns:
                    model_col = col_name
                    break

            # Helper to safely get best row
            def get_best_row(df, col, method="max"):
                if col not in df.columns:
                    return None
                # Force numeric, turning errors to NaN
                s = pd.to_numeric(df[col], errors="coerce")
                s = s.dropna()
                if s.empty:
                    return None

                idx = s.idxmax() if method == "max" else s.idxmin()
                return df.loc[idx]

            found_rec = False

            # 1. Accuracy (ROUGE)
            best_rouge = get_best_row(df, "ROUGE-1 F1", "max")
            if best_rouge is not None and model_col:
                found_rec = True
                st.success(f"""
                ###  Best for Accuracy & Detail: **{best_rouge[model_col]}**
                *   **Why?** It achieved the highest **ROUGE score** ({best_rouge['ROUGE-1 F1']:.2f}).
                *   **What this means:** This model captured the most keywords and phrases from your original text.
                *   **Use this when:** You need a high-quality summary that doesn't miss important facts.
                """)

            # 2. Brevity (Compression)
            concise = get_best_row(df, "Compression %", "max")
            if concise is not None and model_col:
                found_rec = True
                st.warning(f"""
                ###  Best for Quick Reading: **{concise[model_col]}**
                *   **Why?** It compressed the text by **{concise['Compression %']:.1f}%**.
                *   **What this means:** It produced the shortest summary relative to the original.
                *   **Use this when:** You want a tweet-style summary or have limited screen space.
                """)

            # 3. Speed (Time)
            fastest = get_best_row(df, "Time (s)", "min")
            if fastest is not None and model_col:
                found_rec = True
                st.info(f"""
                ###  Best for Real-Time Speed: **{fastest[model_col]}**
                *   **Why?** It finished in just **{fastest['Time (s)']:.3f} seconds**.
                *   **What this means:** It works almost instantly.
                *   **Use this when:** You need to summarize thousands of documents in a batch process.
                """)

            if not found_rec:
                st.write("Run the pipeline to see smart recommendations here.")

            st.divider()
            st.subheader("Detailed Comparison Table")

            # Gradient styling on available columns
            cols = [
                c
                for c in [
                    "Compression %",
                    "Density %",
                    "Cosine Sim",
                    "ROUGE-1 F1",
                    "ROUGE-2 F1",
                    "ROUGE-L F1",
                    "BLEU Score",
                    "METEOR",
                ]
                if c in df.columns
            ]
            # Ensure numeric for gradient
            for c in cols:
                df[c] = pd.to_numeric(df[c], errors="coerce")

            st.dataframe(
                df.style.background_gradient(subset=cols, cmap="Greens"),
                use_container_width=True,
            )

            with open("full_summarization_report.xlsx", "rb") as f:
                st.download_button(
                    "Download Excel Report", f, file_name="summarization_report_v1.xlsx"
                )
        else:
            st.info("No report data found. Please run the pipeline first.")

    # Tab 3: Traceability
    with tabs[2]:
        st.subheader(" Source Traceability")
        st.write("See exactly which source sentences each summary line came from.")

        if Path("results.json").exists():
            with open("results.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            # Collect all available mappings
            all_mappings = {}

            # Extractive mappings
            evals_ext = data.get("evaluation", {}).get("extractive", {})
            for algo, metrics in evals_ext.items():
                if "source_mapping" in metrics and metrics["source_mapping"]:
                    all_mappings[f"Extractive: {algo}"] = metrics["source_mapping"]

            # Abstractive mappings
            evals_abs = data.get("evaluation", {}).get("abstractive", {})
            for model, metrics in evals_abs.items():
                if "source_mapping" in metrics and metrics["source_mapping"]:
                    all_mappings[f"Abstractive: {model}"] = metrics["source_mapping"]

            if all_mappings:
                # Model selector
                selected_model = st.selectbox(
                    "Choose Model to Analyze",
                    options=list(all_mappings.keys()),
                    help="Select which summarization model's traceability you want to view",
                )

                mapping = all_mappings[selected_model]

                # Export button
                col1, col2 = st.columns([3, 1])
                with col2:
                    mapping_csv = "Summary Sentence,Source Sentence,Similarity %,Source Position\n"
                    for item in mapping:
                        mapping_csv += f'"{item.get("summary_sent", "")}","{item.get("source_sent", "")}",{item.get("similarity", 0):.1f},{item.get("source_index", 0)}\n'

                    st.download_button(
                        "📥 Export CSV",
                        mapping_csv,
                        file_name=f"traceability_{selected_model.replace(' ', '_').replace(':', '')}.csv",
                        mime="text/csv",
                    )

                with col1:
                    st.caption(f"Found **{len(mapping)}** mapped sentence pairs")

                st.divider()

                # Display mappings with enhanced info
                for idx, item in enumerate(mapping, 1):
                    score = item.get("similarity", 0)
                    source_idx = item.get("source_index", 0)

                    # Color coding
                    if score > 80:
                        color = "#dcfce7"
                        badge = "🟢 High Match"
                    elif score > 50:
                        color = "#fef9c3"
                        badge = "🟡 Moderate"
                    else:
                        color = "#fee2e2"
                        badge = "🔴 Low Match"

                    st.markdown(
                        f"""
                    <div style="margin-bottom:15px; padding:12px; background:{color}; border-radius:8px; border-left:4px solid #333;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <b>#{idx} Summary Sentence:</b>
                            <span style="background:white; padding:4px 8px; border-radius:4px; font-size:12px;">{badge} ({score:.1f}%)</span>
                        </div>
                        <div style="margin-bottom:10px; font-size:15px;">"{item['summary_sent']}"</div>
                        <div style="background:rgba(255,255,255,0.7); padding:8px; border-radius:4px;">
                            <small style="color:#666;">📄 Source (Position {source_idx}):</small><br>
                            <i style="color:#444;">"{item['source_sent']}"</i>
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
            else:
                st.warning(
                    "No traceability data found. Run the pipeline to generate mappings."
                )
        else:
            st.info("No results file found. Please run the pipeline first.")

    # Tab 4: AI Insight
    with tabs[3]:
        if Path("inference.txt").exists():
            with open("inference.txt", "r", encoding="utf-8") as f:
                st.markdown(f.read())
