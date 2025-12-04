# """
# app.py
# Streamlit app to generate configuration YAML for document summarization.
# """


# import streamlit as st
# import yaml
# from pathlib import Path
# import os

# # Page configuration
# st.set_page_config(
#     page_title="Config Generator",
#     layout="centered",
#     initial_sidebar_state="collapsed"
# )

# # Professional styling
# st.markdown("""
#     <style>
#     .main {
#         background-color: #f8f9fa;
#     }
#     .stApp {
#         max-width: 900px;
#         margin: 0 auto;
#     }
#     h1 {
#         color: #1a1a1a;
#         font-weight: 600;
#         padding-bottom: 1rem;
#         border-bottom: 3px solid #2563eb;
#     }
#     h2 {
#         color: #2563eb;
#         font-size: 1.3rem;
#         font-weight: 600;
#         margin-top: 2rem;
#         margin-bottom: 1rem;
#     }
#     h3 {
#         color: #475569;
#         font-size: 1.1rem;
#         font-weight: 500;
#         margin-top: 1.5rem;
#     }
#     .stButton>button {
#         background-color: #2563eb;
#         color: white;
#         border: none;
#         padding: 0.5rem 2rem;
#         font-weight: 500;
#         border-radius: 6px;
#         width: 100%;
#     }
#     .stButton>button:hover {
#         background-color: #1d4ed8;
#     }
#     .stDownloadButton>button {
#         background-color: #059669;
#         color: white;
#         border: none;
#         padding: 0.5rem 2rem;
#         font-weight: 500;
#         border-radius: 6px;
#         width: 100%;
#     }
#     .stDownloadButton>button:hover {
#         background-color: #047857;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # Title
# st.title("Summarization Configuration Generator")

# # PATHS SECTION
# st.markdown("## 1. File Paths")

# uploaded_file = st.file_uploader("Upload your file", type=["pdf", "docx", "txt"])

# input_path = None

# if uploaded_file is not None:
#     # Create a full path inside a temporary folder
#     temp_path = f"./uploaded_{uploaded_file.name}"

#     # Save the file to disk
#     with open(temp_path, "wb") as f:
#         f.write(uploaded_file.getbuffer())

#     input_path = os.path.abspath(temp_path)

#     st.success(f"Full path: {input_path}")

# st.markdown("### Output Settings")
# output_text = st.text_input(
#     "Output Text Filename",
#     value="converted.txt",
#     help="Name for the converted text file"
# )

# st.markdown("### API Configuration")
# api_key = st.text_input(
#     "API Key",
#     value="",
#     type="password",
#     help="Enter your API key for model access"
# )

# # EXTRACTIVE SECTION
# st.markdown("## 2. Extractive Methods")

# st.markdown("### Select Algorithms")

# col1, col2 = st.columns(2)

# with col1:
#     algo_tfidf = st.checkbox("TF-IDF", value=True)
#     algo_custom_textrank = st.checkbox("Custom TextRank", value=True)
#     algo_sumy_textrank = st.checkbox("Sumy TextRank", value=True)
#     algo_sumy_lexrank = st.checkbox("Sumy LexRank", value=True)

# with col2:
#     algo_sumy_lsa = st.checkbox("Sumy LSA", value=True)
#     algo_semantic_textrank = st.checkbox("Semantic TextRank", value=True)
#     algo_embedding_lexrank = st.checkbox("Embedding LexRank", value=True)
#     algo_mmr = st.checkbox("MMR", value=True)

# selected_algorithms = []
# if algo_tfidf: selected_algorithms.append('tfidf')
# if algo_custom_textrank: selected_algorithms.append('custom_textrank')
# if algo_sumy_textrank: selected_algorithms.append('sumy_textrank')
# if algo_sumy_lexrank: selected_algorithms.append('sumy_lexrank')
# if algo_sumy_lsa: selected_algorithms.append('sumy_lsa')
# if algo_semantic_textrank: selected_algorithms.append('semantic_textrank')
# if algo_embedding_lexrank: selected_algorithms.append('embedding_lexrank')
# if algo_mmr: selected_algorithms.append('mmr')

# # SBERT Settings
# if algo_semantic_textrank or algo_embedding_lexrank or algo_mmr:
#     st.markdown("### SBERT Settings")
    
#     sbert_model = st.selectbox(
#         "SBERT Model",
#         ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "paraphrase-MiniLM-L6-v2"],
#         index=0
#     )
    
#     col1, col2 = st.columns(2)
#     with col1:
#         similarity_threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.0, 0.1)
#     with col2:
#         top_k_enabled = st.checkbox("Limit Neighbors", value=False)
#         top_k = st.number_input("Top K", 1, 50, 10, disabled=not top_k_enabled) if top_k_enabled else None

# # MMR Settings
# if algo_mmr:
#     st.markdown("### MMR Settings")
#     lambda_param = st.slider("Lambda (Relevance vs Diversity)", 0.0, 1.0, 0.7, 0.1)

# # ABSTRACTIVE SECTION
# st.markdown("## 3. Abstractive Models")

# st.markdown("### Select Models")

# col1, col2 = st.columns(2)

# with col1:
#     model_bart = st.checkbox("BART Large CNN", value=True)
#     model_t5 = st.checkbox("T5 Small", value=True)
#     model_pegasus_xsum = st.checkbox("Pegasus XSum", value=True)
#     model_flan_t5_base = st.checkbox("Flan-T5 Base", value=True)

# with col2:
#     model_flan_t5_large = st.checkbox("Flan-T5 Large", value=False)
#     model_pegasus_large = st.checkbox("Pegasus Large", value=False)
#     model_bigbird_pegasus = st.checkbox("BigBird Pegasus", value=False)
#     model_led = st.checkbox("LED (Long Docs)", value=False)

# selected_models = []
# if model_bart: selected_models.append('bart')
# if model_t5: selected_models.append('t5')
# if model_pegasus_xsum: selected_models.append('pegasus_xsum')
# if model_flan_t5_base: selected_models.append('flan_t5_base')
# if model_flan_t5_large: selected_models.append('flan_t5_large')
# if model_pegasus_large: selected_models.append('pegasus_large')
# if model_bigbird_pegasus: selected_models.append('bigbird_pegasus')
# if model_led: selected_models.append('led')

# st.markdown("### Generation Parameters")

# col1, col2 = st.columns(2)
# with col1:
#     max_length = st.number_input("Max Length", 50, 512, 150, 10)
# with col2:
#     min_length = st.number_input("Min Length", 10, 200, 50, 10)

# # LED Settings
# if model_led:
#     st.markdown("### LED Specific Settings")
#     col1, col2 = st.columns(2)
#     with col1:
#         led_max_length = st.number_input("LED Max Length", 100, 1024, 256, 16)
#     with col2:
#         led_min_length = st.number_input("LED Min Length", 10, 200, 50, 10)
#     chunk_summary_once = st.checkbox("Chunk Summary Once", value=True)

# # PROCESSING SECTION
# st.markdown("## 4. Processing Settings")

# col1, col2 = st.columns(2)
# with col1:
#     batch_size = st.number_input("Batch Size", 1, 16, 1)
#     use_gpu = st.checkbox("Use GPU", value=False)

# with col2:
#     verbose = st.checkbox("Verbose Logging", value=True)
#     save_temp_excel = st.checkbox("Save Temp on Lock", value=True)

# # OUTPUT SECTION
# st.markdown("## 5. Output Settings")

# col1, col2 = st.columns(2)
# with col1:
#     output_dir = st.text_input("Output Directory", value=".")
# with col2:
#     excel_filename = st.text_input("Excel Filename", value="full_summarization_report.xlsx")

# # PERFORMANCE SECTION
# st.markdown("## 6. Performance Settings")

# max_sentences = st.number_input(
#     "Max Sentences for Full Embedding",
#     100, 1000, 400, 50,
#     help="Documents exceeding this will use chunking for semantic methods"
# )

# # BUILD CONFIG
# st.markdown("---")

# # Validation
# validation_errors = []

# if not input_path or input_path.strip() == "":
#     validation_errors.append("Input Document Path is required")

# if not output_text or output_text.strip() == "":
#     validation_errors.append("Output Text Filename is required")

# if not api_key or api_key.strip() == "":
#     validation_errors.append("API Key is required")

# if len(selected_algorithms) == 0:
#     validation_errors.append("At least one Extractive Algorithm must be selected")

# if len(selected_models) == 0:
#     validation_errors.append("At least one Abstractive Model must be selected")

# if not output_dir or output_dir.strip() == "":
#     validation_errors.append("Output Directory is required")

# if not excel_filename or excel_filename.strip() == "":
#     validation_errors.append("Excel Filename is required")

# # Show validation errors if any
# if validation_errors:
#     st.error("Please complete all required fields:")
#     for error in validation_errors:
#         st.write(f"- {error}")

# generate_button_disabled = len(validation_errors) > 0

# if st.button("Generate Configuration", disabled=generate_button_disabled):
#     config = {
#         'paths': {
#             'input_path': input_path,
#             'output_text': output_text
#         },
#          'gemini': {
#             'enabled': True,             
#             'api_key': api_key,          
#         },
         
#         'extractive': {
#             'algorithms': selected_algorithms
#         },
#         'abstractive': {
#             'models': {
#                 'bart': 'facebook/bart-large-cnn',
#                 't5': 't5-small',
#                 'pegasus_xsum': 'google/pegasus-xsum',
#                 'flan_t5_base': 'google/flan-t5-base',
#                 'flan_t5_large': 'google/flan-t5-large',
#                 'pegasus_large': 'google/pegasus-large',
#                 'bigbird_pegasus': 'google/bigbird-pegasus-large-arxiv',
#                 'led': 'allenai/led-base-16384'
#             },
#             'default_to_run': selected_models,
#             'generation': {
#                 'max_length': max_length,
#                 'min_length': min_length
#             }
#         },
#         'processing': {
#             'batch_size': batch_size,
#             'use_gpu': use_gpu,
#             'verbose': verbose,
#             'save_temp_excel_on_lock': save_temp_excel
#         },
#         'output': {
#             'dir': output_dir,
#             'excel_filename': excel_filename
#         },
#         'performance': {
#             'max_sentences_for_full_embedding': max_sentences,
#             'notes': f"If a document has more than {max_sentences} sentences:\n- SBERT-based models become slow (O(n²) similarity matrix)\n- Accelerator should chunk or skip heavy semantic methods"
#         }
#     }
    
#     # Add SBERT config if needed
#     if algo_semantic_textrank or algo_embedding_lexrank or algo_mmr:
#         config['extractive']['sbert'] = {
#             'model': sbert_model,
#             'similarity_threshold': similarity_threshold,
#             'top_k': top_k
#         }
    
#     # Add MMR config if needed
#     if algo_mmr:
#         config['extractive']['mmr'] = {
#             'lambda_param': lambda_param
#         }
    
#     # Add LED config if needed
#     if model_led:
#         config['abstractive']['led'] = {
#             'max_length': led_max_length,
#             'min_length': led_min_length,
#             'chunk_summary_once': chunk_summary_once
#         }
    
#     yaml_content = yaml.dump(config, default_flow_style=False, sort_keys=False)
    
#     # Create configs directory if it doesn't exist
#     configs_dir = Path("configs")
#     configs_dir.mkdir(exist_ok=True)
    
#     # Save to configs/config.yaml
#     config_path =  "config.yaml"
    
#     try:
#         with open(config_path, 'w') as f:
#             f.write(yaml_content)
        
#         st.success(f"Configuration saved successfully to: {config_path}")
        
#         st.code(yaml_content, language='yaml')
        
#     except Exception as e:
#         st.error(f"Error saving configuration: {str(e)}")







"""
app.py
Streamlit app to generate configuration YAML for document summarization.
"""

import streamlit as st
import yaml
from pathlib import Path
import os
import subprocess  
import pandas as pd  
import sys



# Page configuration
st.set_page_config(
    page_title="Config Generator",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Professional styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        max-width: 900px;
        margin: 0 auto;
    }
    h1 {
        color: #1a1a1a;
        font-weight: 600;
        padding-bottom: 1rem;
        border-bottom: 3px solid #2563eb;
    }
    h2 {
        color: #2563eb;
        font-size: 1.3rem;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    h3 {
        color: #475569;
        font-size: 1.1rem;
        font-weight: 500;
        margin-top: 1.5rem;
    }
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 500;
        border-radius: 6px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
    }
    .stDownloadButton>button {
        background-color: #059669;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 500;
        border-radius: 6px;
        width: 100%;
    }
    .stDownloadButton>button:hover {
        background-color: #047857;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("Summarization Configuration Generator")

# PATHS SECTION
st.markdown("## 1. File Paths")

uploaded_file = st.file_uploader("Upload your file", type=["pdf", "docx", "txt"])

input_path = None

if uploaded_file is not None:
    # Create a full path inside a temporary folder
    temp_path = f"./uploaded_{uploaded_file.name}"

    # Save the file to disk
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    input_path = os.path.abspath(temp_path)

    st.success(f"Full path: {input_path}")

st.markdown("### Output Settings")
output_text = st.text_input(
    "Output Text Filename",
    value="converted.txt",
    help="Name for the converted text file"
)

st.markdown("### API Configuration")
api_key = st.text_input(
    "API Key",
    value="",
    type="password",
    help="Enter your API key for model access"
)

# EXTRACTIVE SECTION
st.markdown("## 2. Extractive Methods")

st.markdown("### Select Algorithms")

col1, col2 = st.columns(2)

with col1:
    algo_tfidf = st.checkbox("TF-IDF", value=True)
    algo_custom_textrank = st.checkbox("Custom TextRank", value=True)
    algo_sumy_textrank = st.checkbox("Sumy TextRank", value=True)
    algo_sumy_lexrank = st.checkbox("Sumy LexRank", value=True)

with col2:
    algo_sumy_lsa = st.checkbox("Sumy LSA", value=True)
    algo_semantic_textrank = st.checkbox("Semantic TextRank", value=True)
    algo_embedding_lexrank = st.checkbox("Embedding LexRank", value=True)
    algo_mmr = st.checkbox("MMR", value=True)

selected_algorithms = []
if algo_tfidf: selected_algorithms.append('tfidf')
if algo_custom_textrank: selected_algorithms.append('custom_textrank')
if algo_sumy_textrank: selected_algorithms.append('sumy_textrank')
if algo_sumy_lexrank: selected_algorithms.append('sumy_lexrank')
if algo_sumy_lsa: selected_algorithms.append('sumy_lsa')
if algo_semantic_textrank: selected_algorithms.append('semantic_textrank')
if algo_embedding_lexrank: selected_algorithms.append('embedding_lexrank')
if algo_mmr: selected_algorithms.append('mmr')

# SBERT Settings
if algo_semantic_textrank or algo_embedding_lexrank or algo_mmr:
    st.markdown("### SBERT Settings")
    
    sbert_model = st.selectbox(
        "SBERT Model",
        ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "paraphrase-MiniLM-L6-v2"],
        index=0
    )
    
    col1, col2 = st.columns(2)
    with col1:
        similarity_threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.0, 0.1)
    with col2:
        top_k_enabled = st.checkbox("Limit Neighbors", value=False)
        top_k = st.number_input("Top K", 1, 50, 10, disabled=not top_k_enabled) if top_k_enabled else None

# MMR Settings
if algo_mmr:
    st.markdown("### MMR Settings")
    lambda_param = st.slider("Lambda (Relevance vs Diversity)", 0.0, 1.0, 0.7, 0.1)

# ABSTRACTIVE SECTION
st.markdown("## 3. Abstractive Models")

st.markdown("### Select Models")

col1, col2 = st.columns(2)

with col1:
    model_bart = st.checkbox("BART Large CNN", value=True)
    model_t5 = st.checkbox("T5 Small", value=True)
    model_pegasus_xsum = st.checkbox("Pegasus XSum", value=True)
    model_flan_t5_base = st.checkbox("Flan-T5 Base", value=True)

with col2:
    model_flan_t5_large = st.checkbox("Flan-T5 Large", value=False)
    model_pegasus_large = st.checkbox("Pegasus Large", value=False)
    model_bigbird_pegasus = st.checkbox("BigBird Pegasus", value=False)
    model_led = st.checkbox("LED (Long Docs)", value=False)

selected_models = []
if model_bart: selected_models.append('bart')
if model_t5: selected_models.append('t5')
if model_pegasus_xsum: selected_models.append('pegasus_xsum')
if model_flan_t5_base: selected_models.append('flan_t5_base')
if model_flan_t5_large: selected_models.append('flan_t5_large')
if model_pegasus_large: selected_models.append('pegasus_large')
if model_bigbird_pegasus: selected_models.append('bigbird_pegasus')
if model_led: selected_models.append('led')

st.markdown("### Generation Parameters")

col1, col2 = st.columns(2)
with col1:
    max_length = st.number_input("Max Length", 50, 512, 150, 10)
with col2:
    min_length = st.number_input("Min Length", 10, 200, 50, 10)

# LED Settings
if model_led:
    st.markdown("### LED Specific Settings")
    col1, col2 = st.columns(2)
    with col1:
        led_max_length = st.number_input("LED Max Length", 100, 1024, 256, 16)
    with col2:
        led_min_length = st.number_input("LED Min Length", 10, 200, 50, 10)
    chunk_summary_once = st.checkbox("Chunk Summary Once", value=True)

# PROCESSING SECTION
st.markdown("## 4. Processing Settings")

col1, col2 = st.columns(2)
with col1:
    batch_size = st.number_input("Batch Size", 1, 16, 1)
    use_gpu = st.checkbox("Use GPU", value=False)

with col2:
    verbose = st.checkbox("Verbose Logging", value=True)
    save_temp_excel = st.checkbox("Save Temp on Lock", value=True)

# OUTPUT SECTION
st.markdown("## 5. Output Settings")

col1, col2 = st.columns(2)
with col1:
    output_dir = st.text_input("Output Directory", value=".")
with col2:
    excel_filename = st.text_input("Excel Filename", value="full_summarization_report.xlsx")

# PERFORMANCE SECTION
st.markdown("## 6. Performance Settings")

max_sentences = st.number_input(
    "Max Sentences for Full Embedding",
    100, 1000, 400, 50,
    help="Documents exceeding this will use chunking for semantic methods"
)

# BUILD CONFIG
st.markdown("---")

# Validation
validation_errors = []

if not input_path or input_path.strip() == "":
    validation_errors.append("Input Document Path is required")

if not output_text or output_text.strip() == "":
    validation_errors.append("Output Text Filename is required")

if not api_key or api_key.strip() == "":
    validation_errors.append("API Key is required")

if len(selected_algorithms) == 0:
    validation_errors.append("At least one Extractive Algorithm must be selected")

if len(selected_models) == 0:
    validation_errors.append("At least one Abstractive Model must be selected")

if not output_dir or output_dir.strip() == "":
    validation_errors.append("Output Directory is required")

if not excel_filename or excel_filename.strip() == "":
    validation_errors.append("Excel Filename is required")

# Show validation errors if any
if validation_errors:
    st.error("Please complete all required fields:")
    for error in validation_errors:
        st.write(f"- {error}")

generate_button_disabled = len(validation_errors) > 0

if st.button("Generate Configuration", disabled=generate_button_disabled):
    config = {
        'paths': {
            'input_path': input_path,
            'output_text': output_text
        },
        'gemini': {
            'enabled': True,
            'api_key': api_key,
        },
        'extractive': {
            'algorithms': selected_algorithms
        },
        'abstractive': {
            'models': {
                'bart': 'facebook/bart-large-cnn',
                't5': 't5-small',
                'pegasus_xsum': 'google/pegasus-xsum',
                'flan_t5_base': 'google/flan-t5-base',
                'flan_t5_large': 'google/flan-t5-large',
                'pegasus_large': 'google/pegasus-large',
                'bigbird_pegasus': 'google/bigbird-pegasus-large-arxiv',
                'led': 'allenai/led-base-16384'
            },
            'default_to_run': selected_models,
            'generation': {
                'max_length': max_length,
                'min_length': min_length
            }
        },
        'processing': {
            'batch_size': batch_size,
            'use_gpu': use_gpu,
            'verbose': verbose,
            'save_temp_excel_on_lock': save_temp_excel
        },
        'output': {
            'dir': output_dir,
            'excel_filename': excel_filename
        },
        'performance': {
            'max_sentences_for_full_embedding': max_sentences,
            'notes': f"If a document has more than {max_sentences} sentences:\n"
                     f"- SBERT-based models become slow (O(n²) similarity matrix)\n"
                     f"- Accelerator should chunk or skip heavy semantic methods"
        }
    }
    
    # Add SBERT config if needed
    if algo_semantic_textrank or algo_embedding_lexrank or algo_mmr:
        config['extractive']['sbert'] = {
            'model': sbert_model,
            'similarity_threshold': similarity_threshold,
            'top_k': top_k
        }
    
    # Add MMR config if needed
    if algo_mmr:
        config['extractive']['mmr'] = {
            'lambda_param': lambda_param
        }
    
    # Add LED config if needed
    if model_led:
        config['abstractive']['led'] = {
            'max_length': led_max_length,
            'min_length': led_min_length,
            'chunk_summary_once': chunk_summary_once
        }
    
    yaml_content = yaml.dump(config, default_flow_style=False, sort_keys=False)
    
    config_path = "config.yaml"
    
    try:
        with open(config_path, 'w', encoding="utf-8") as f:
            f.write(yaml_content)
        
        st.success(f"Configuration saved successfully to: {config_path}")
        st.code(yaml_content, language='yaml')
        
    except Exception as e:
        st.error(f"Error saving configuration: {str(e)}")


# =========================================================
# 7. Run Pipeline and Show Results
# =========================================================

# 7. Run Pipeline and View Results
st.markdown("## 7. Run Pipeline and View Results")
st.markdown(
    "This will run `run_pipeline.py` using the generated `config.yaml` and then display:\n"
    "- The generated Excel report (latest full_summarization_report*.xlsx)\n"
    "- The Gemini inference from `inference.txt`"
)

BASE_DIR = Path(__file__).resolve().parent  # project root (where run_pipeline.py lives)

if st.button("Run Full Pipeline"):
    with st.spinner("Running full pipeline (doc_to_txt → excel_demo → gemini_analysis)..."):
        # Use the same Python interpreter that Streamlit is using
        result = subprocess.run(
            [sys.executable, "run_pipeline.py"],
            cwd=BASE_DIR,              # IMPORTANT: run from project root
            capture_output=True,
            text=True
        )

    st.success("Pipeline finished. See logs below.")

    # Show stdout
    if result.stdout:
        st.markdown("### Pipeline Output (stdout)")
        st.code(result.stdout)
    else:
        st.markdown("### Pipeline Output (stdout)")
        st.write("(no stdout)")

    # Show stderr
    if result.stderr:
        st.markdown("### Pipeline Errors/Warnings (stderr)")
        st.code(result.stderr)

    # === Show Excel report ===
    st.markdown("### Generated Excel Report")

    # Find the latest full_summarization_report*.xlsx under BASE_DIR
    excel_files = sorted(
        BASE_DIR.glob("full_summarization_report*.xlsx"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    if excel_files:
        latest_excel = excel_files[0]
        st.write(f"Using file: `{latest_excel.name}`")

        try:
            import pandas as pd

            df_excel = pd.read_excel(latest_excel, sheet_name="All Results")
            st.dataframe(df_excel)
        except Exception as e:
            st.error(f"Could not read Excel file: {e}")
    else:
        st.warning(
            "No Excel file found matching `full_summarization_report*.xlsx`. "
            "Check that the pipeline ran without fatal errors."
        )

    # === Show inference.txt (Gemini output) ===
    st.markdown("### Gemini Inference (inference.txt)")
    inference_path = BASE_DIR / "inference.txt"

    if inference_path.exists():
        try:
            with inference_path.open("r", encoding="utf-8") as f:
                content = f.read()
            st.text_area("inference.txt", content, height=300)
        except Exception as e:
            st.error(f"Error reading inference.txt: {e}")
    else:
        st.warning(
            "`inference.txt` not found in project root.\n\n"
            "Make sure:\n"
            "- `gemini.enabled` is `true` in config.yaml\n"
            "- The pipeline completed Gemini analysis (see stdout above)"
        )