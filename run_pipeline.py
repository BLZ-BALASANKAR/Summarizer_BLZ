# # run_pipeline.py

# """
# Run the full summarization pipeline in one go:

# 1. doc_to_txt.py
#    - Reads input_path and output_text from config.yaml
#    - Converts the PDF/DOC/DOCX to a text file (e.g. converted.txt)

# 2. excel_demo.py
#    - Reads the same output_text file from config.yaml
#    - Runs extractive + abstractive summarization
#    - Exports an Excel report (full_summarization_report.xlsx)
# """

# import subprocess
# import sys
# import os
# from pathlib import Path

# def run_script(script_name: str) -> int:
#     """
#     Run a Python script as a subprocess and stream its stdout/stderr.

#     Returns:
#         The exit code of the script.
#     """
#     print("\n" + "=" * 30)
#     print(f" Running: {script_name}")
#     print("=" * 30)

#     result = subprocess.run(
#         [sys.executable, script_name],
#         stdout=sys.stdout,
#         stderr=sys.stderr
#     )
#     return result.returncode


# def run_full_pipeline() -> bool:
#     """
#     Runs the complete workflow:

#     1. doc_to_txt.py  → generates the text file defined in config.yaml (paths.output_text)
#     2. excel_demo.py  → generates the Excel report using that text file

#     Returns:
#         True if everything succeeded, False otherwise.
#     """

#     # ----------------------------
#     # STEP 1 – run doc_to_txt.py
#     # ----------------------------
#     code1 = run_script("doc_to_txt.py")
#     if code1 != 0:
#         print("\n❌ ERROR: doc_to_txt.py failed. Pipeline stopped.")
#         return False

#     # We don’t hardcode 'converted.txt' here; we just check that *some* output exists.
#     # But for a simple sanity check we can still look for converted.txt as default:
#     default_output = Path("converted.txt")
#     if not default_output.exists():
#         # It's possible the user changed paths.output_text in config.yaml.
#         # So we just warn, but don't strictly fail here.
#         print("\n⚠ Warning: 'converted.txt' not found.")
#         print("   If you changed paths.output_text in config.yaml, make sure")
#         print("   it matches what excel_demo.py expects.")
#     else:
#         print(f"\n✓ Found text file: {default_output.resolve()}")

#     # ----------------------------
#     # STEP 2 – run excel_demo.py
#     # ----------------------------
#     code2 = run_script("excel_demo.py")
#     if code2 != 0:
#         print("\n❌ ERROR: excel_demo.py failed.")
#         return False

#     print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
#     print("📄 Your Excel report should now be in the current folder.\n")
#     return True


# if __name__ == "__main__":
#     success = run_full_pipeline()
#     # set exit code for shells / CI
#     sys.exit(0 if success else 1)


# run_pipeline.py

"""
Run the full summarization pipeline in one go:

1. doc_to_txt.py
   - Reads input_path from config.yaml
   - Converts PDF/DOC/DOCX to text (paths.output_text)

2. excel_demo.py
   - Reads the text file from config.yaml
   - Runs extractive + abstractive summarization
   - Exports Excel report

3. gemini_analysis.py
   - Optional (based on config.yaml → gemini.enabled)
   - Calls Google Gemini LLM to analyze model performance
"""

import subprocess
import sys
from pathlib import Path
import yaml


# -------------------------- Helpers --------------------------

def run_script(script_name: str) -> int:
    """
    Run a Python script as a subprocess and stream its stdout/stderr.
    Returns the exit code.
    """
    print("\n" + "=" * 40)
    print(f" Running: {script_name}")
    print("=" * 40)

    result = subprocess.run(
        [sys.executable, script_name],
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    return result.returncode


def load_config():
    """Load config.yaml from project root."""
    cfg_path = Path("config.yaml")
    if not cfg_path.exists():
        print(" config.yaml not found!")
        sys.exit(1)

    with cfg_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# -------------------------- Pipeline Logic --------------------------

def run_full_pipeline() -> bool:
    cfg = load_config()
    gem_cfg = cfg.get("gemini", {})

    # ----------------------------
    # STEP 1 – doc_to_txt.py
    # ----------------------------
    code1 = run_script("doc_to_txt.py")
    if code1 != 0:
        print("\nERROR: doc_to_txt.py failed. Pipeline stopped.")

        return False

    # Check existence of converted.txt (not mandatory if user changed config)
    output_text = cfg["paths"].get("output_text", "converted.txt")
    out_path = Path(output_text)

    if out_path.exists():
        print(f"\n Found extracted text: {out_path.resolve()}")
    else:
        print(f"\n Warning: Expected text file {output_text} not found.")
        print("   Make sure paths.output_text in config.yaml matches excel_demo.py")

    # ----------------------------
    # STEP 2 – excel_demo.py
    # ----------------------------
    code2 = run_script("excel_demo.py")
    if code2 != 0:
        print("\n ERROR: excel_demo.py failed.")
        return False

    print("\n Excel report successfully generated!")

    # ----------------------------
    # STEP 3 – gemini_analysis.py (optional)
    # ----------------------------
    if gem_cfg.get("enabled", True):
        print("\n Gemini analysis enabled — running gemini_analysis.py...")
        code3 = run_script("gemini_analysis.py")

        if code3 != 0:
            print("\n Warning: gemini_analysis.py failed. Continuing without LLM analysis.")
        else:
            print("\n Gemini analysis completed successfully!")
    else:
        print("\n Gemini analysis disabled in config.yaml — skipping step.")

    print("\n FULL PIPELINE COMPLETED SUCCESSFULLY!")
    return True


# -------------------------- Main --------------------------

if __name__ == "__main__":
    success = run_full_pipeline()
    sys.exit(0 if success else 1)
