"""
config.py

Thin wrapper over config.yaml so that older code like
    from config import DEFAULT_ABSTRACTIVE_TO_RUN, ...
still works.

It reads config.yaml and exposes the constants that
summarization_accelerator.py expects.
"""

import yaml
from pathlib import Path

# ---- load YAML once ----
_CFG_PATH = Path("config.yaml")
if not _CFG_PATH.exists():
    raise FileNotFoundError(
        "config.yaml not found in project root. "
        "Create it or move it next to config.py."
    )

with _CFG_PATH.open("r", encoding="utf-8") as f:
    _cfg = yaml.safe_load(f)

# -----------------------------
# PATHS (optional, for reference)
# -----------------------------
PATHS = _cfg.get("paths", {})
INPUT_PATH = PATHS.get("input_path")
OUTPUT_TEXT = PATHS.get("output_text", "converted.txt")

# ============================================================
#                 ABSTRACTIVE MODEL CONFIG
# ============================================================

_abstr = _cfg.get("abstractive", {})

# HuggingFace model paths for each abstractive summarizer
ABSTRACTIVE_MODELS = _abstr.get("models", {})

# Run ALL abstractive models (list of keys)
DEFAULT_ABSTRACTIVE_TO_RUN = _abstr.get("default_to_run", [])

# Generic generation params
_gen = _abstr.get("generation", {})
DEFAULT_MAX_LENGTH = _gen.get("max_length", 150)
DEFAULT_MIN_LENGTH = _gen.get("min_length", 50)

# LED-specific options (if needed elsewhere)
LED_CONFIG = _abstr.get("led", {})

# ============================================================
#               EXTRACTIVE ALGORITHM CONFIG
# ============================================================

_extr = _cfg.get("extractive", {})

EXTRACTIVE_ALGORITHMS = _extr.get("algorithms", [])

_sbert = _extr.get("sbert", {})
DEFAULT_SBERT_MODEL = _sbert.get("model", "all-MiniLM-L6-v2")
DEFAULT_SIMILARITY_THRESHOLD = _sbert.get("similarity_threshold", 0.0)
DEFAULT_TOP_K = _sbert.get("top_k", None)

_mmr = _extr.get("mmr", {})
DEFAULT_MMR_LAMBDA = _mmr.get("lambda_param", 0.7)

# ============================================================
#                 SUMMARIZATION PARAMETERS
# ============================================================

_sum = _cfg.get("summarization", {})
DEFAULT_SENTENCE_COUNT = _sum.get("sentence_count", 3)
# Note: DEFAULT_MAX_LENGTH / DEFAULT_MIN_LENGTH already set above
# from abstractive.generation, but if you prefer you can override:
DEFAULT_MAX_LENGTH = _sum.get("max_length", DEFAULT_MAX_LENGTH)
DEFAULT_MIN_LENGTH = _sum.get("min_length", DEFAULT_MIN_LENGTH)

# ============================================================
#                 PROCESSING / SYSTEM SETTINGS
# ============================================================

_proc = _cfg.get("processing", {})
BATCH_SIZE = _proc.get("batch_size", 1)
USE_GPU = _proc.get("use_gpu", False)
VERBOSE = _proc.get("verbose", True)
SAVE_TEMP_EXCEL_ON_LOCK = _proc.get("save_temp_excel_on_lock", True)

# ============================================================
#                       OUTPUT SETTINGS
# ============================================================

_out = _cfg.get("output", {})
DEFAULT_OUTPUT_DIR = _out.get("dir", ".")
DEFAULT_EXCEL_FILENAME = _out.get("excel_filename", "full_summarization_report.xlsx")

# ============================================================
#                   PERFORMANCE / SAFETY
# ============================================================

_perf = _cfg.get("performance", {})
MAX_SENTENCES_FOR_FULL_EMBEDDING = _perf.get("max_sentences_for_full_embedding", 400)
