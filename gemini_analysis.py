# """
# gemini_analysis.py

# Call Google Gemini to analyze summarization model performance.
# Uses API key and settings from config.yaml (gemini section).

# Flow:
# - Load config.yaml
# - Read Excel summarization report
# - Drop 'Summary' column
# - Convert rows to JSON (one record per line)
# - Inject that JSON into the Gemini prompt
# - Print Gemini's analysis
# - Save output as inference.txt
# """

# import sys
# from pathlib import Path
# import yaml
# import pandas as pd
# from colorama import init, Fore, Style

# # Requires: pip install google-genai
# from google import genai
# from google.genai import types

# init()


# # ----------------------------------------------------------
# # Load config.yaml
# # ----------------------------------------------------------
# def load_config():
#     """Load configuration from config.yaml"""
#     cfg_path = Path("config.yaml")
#     if not cfg_path.exists():
#         print(f"{Fore.RED}Error: config.yaml not found in project root.{Style.RESET_ALL}")
#         sys.exit(1)

#     try:
#         with cfg_path.open("r", encoding="utf-8") as f:
#             return yaml.safe_load(f)
#     except Exception as e:
#         print(f"{Fore.RED}Error: Could not load config.yaml → {e}{Style.RESET_ALL}")
#         sys.exit(1)


# # ----------------------------------------------------------
# # Load Excel and convert to JSON (NDJSON format)
# # ----------------------------------------------------------
# def load_excel_json(gem_cfg: dict) -> str:
#     """
#     Load the Excel sheet, drop the 'Summary' column if present,
#     and return newline-delimited JSON (one record per line).
#     """
#     excel_path_str = gem_cfg.get(
#         "excel_path",
#         "full_summarization_report.xlsx"  # default file in project root
#     )
#     excel_path = Path(excel_path_str)

#     if not excel_path.exists():
#         print(f"{Fore.RED}Error: Excel file not found → {excel_path}{Style.RESET_ALL}")
#         sys.exit(1)

#     try:
#         df = pd.read_excel(excel_path, sheet_name="All Results")
#     except Exception as e:
#         print(f"{Fore.RED}Error reading Excel file → {e}{Style.RESET_ALL}")
#         sys.exit(1)

#     if "Summary" in df.columns:
#         df = df.drop(columns=["Summary"])

#     return df.to_json(orient="records", lines=True)


# # ----------------------------------------------------------
# # Dynamic Prompt Builder
# # ----------------------------------------------------------
# def build_prompt(var_str: str) -> str:
#     """
#     Build the prompt sent to Gemini using dynamic Excel/JSON data.
#     """
#     return f"""
# Analyze the following summarization model performance data and provide a comprehensive evaluation:

# {var_str}

# Please provide the following, in bullet points and max 200 words:

# - Metric interpretations (Compression %, Density %, Cosine Similarity, Time):
#   - what they mean
#   - optimal ranges
#   - whether higher/lower is better
# - Performance rankings:
#   - rank extractive models
#   - rank abstractive models
#   - best for speed, best for quality, best overall balance
# - Red flags & issues:
#   - concerning values, potential failures/hallucinations, outliers
# - Practical recommendations:
#   - best for speed-critical
#   - best for quality-critical
#   - best balanced
#   - models to avoid or investigate
# - Trade-offs:
#   - speed vs quality
#   - extractive vs abstractive and when to use each
  
#   IMPORTANT:
# Provide the output in plain text only.
# Do NOT use markdown.
# Do NOT use bold text.
# Do NOT use asterisks or hyphens for bullets.
# Keep formatting clean and readable.
# """


# # ----------------------------------------------------------
# # Save Gemini Output to inference.txt
# # ----------------------------------------------------------
# def save_output_to_txt(text: str):
#     """Save Gemini output to inference.txt (no folders)."""
#     file_path = Path("inference.txt")

#     with file_path.open("w", encoding="utf-8") as f:
#         f.write(text)

#     print(f"{Fore.GREEN}Output saved to: {file_path.resolve()}{Style.RESET_ALL}")


# # ----------------------------------------------------------
# # Main Program
# # ----------------------------------------------------------
# def main():
#     cfg = load_config()
#     gem_cfg = cfg.get("gemini", {})

#     if not gem_cfg.get("enabled", True):
#         print(
#             f"{Fore.YELLOW}Gemini analysis disabled in config.yaml "
#             f"(gemini.enabled = false). Skipping.{Style.RESET_ALL}"
#         )
#         return

#     api_key = gem_cfg.get("api_key")
#     if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
#         print(
#             f"{Fore.RED}Error: Gemini API key not set in config.yaml "
#             f"(gemini.api_key).{Style.RESET_ALL}"
#         )
#         sys.exit(1)

#     model_name = gem_cfg.get("model", "gemini-2.5-flash")
#     temperature = float(gem_cfg.get("temperature", 0.1))

#     # Initialize Gemini client
#     try:
#         client = genai.Client(api_key=api_key)
#     except Exception as e:
#         print(f"{Fore.RED}Error initializing Gemini client. Check API key & installation.{Style.RESET_ALL}")
#         print(f"Details: {e}")
#         sys.exit(1)

#     # Load data from Excel -> JSON string
#     var_str = load_excel_json(gem_cfg)

#     # Build dynamic LLM prompt
#     prompt_text = build_prompt(var_str)

#     print(f"{Fore.CYAN}Sending comprehensive analysis request to Gemini...{Style.RESET_ALL}")

#     try:
#         response = client.models.generate_content(
#             model=model_name,
#             contents=[prompt_text],
#             config=types.GenerateContentConfig(
#                 temperature=temperature
#             ),
#         )

#         output_text = response.text.strip()

#         print("\n" + "=" * 50)
#         print("## Gemini LLM Analysis Result")
#         print("=" * 50)
#         print(output_text)
#         print("=" * 50 + "\n")

#         # Save inference to text file
#         save_output_to_txt(output_text)

#     except Exception as e:
#         print(f"{Fore.RED}--- ERROR: Failed to get response from Gemini ---{Style.RESET_ALL}")
#         print(f"Details: {e}")
#         sys.exit(1)


# if __name__ == "__main__":
#     main()



"""
gemini_analysis.py

Call Google Gemini to analyze summarization model performance.
Uses API key and settings from config.yaml (gemini section).

Flow:
- Load config.yaml
- Read Excel summarization report
- Drop 'Summary' column
- Convert rows to JSON (one record per line)
- Inject that JSON into the Gemini prompt
- Print Gemini's analysis
- Save output as inference.txt (includes Gemini output + Excel table)
"""

import sys
from pathlib import Path
import yaml
import pandas as pd
from colorama import init, Fore, Style

# Requires: pip install google-genai
from google import genai
from google.genai import types

init()


# ----------------------------------------------------------
# Load config.yaml
# ----------------------------------------------------------
def load_config():
    """Load configuration from config.yaml"""
    cfg_path = Path("config.yaml")
    if not cfg_path.exists():
        print(f"{Fore.RED}Error: config.yaml not found in project root.{Style.RESET_ALL}")
        sys.exit(1)

    try:
        with cfg_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"{Fore.RED}Error: Could not load config.yaml → {e}{Style.RESET_ALL}")
        sys.exit(1)


# ----------------------------------------------------------
# Load Excel and convert to JSON (NDJSON format) for Gemini
# ----------------------------------------------------------
def load_excel_json(gem_cfg: dict) -> str:
    """
    Load the Excel sheet, drop the 'Summary' column if present,
    and return newline-delimited JSON (one record per line).
    """
    excel_path_str = gem_cfg.get(
        "excel_path",
        "full_summarization_report.xlsx"  # default file in project root
    )
    excel_path = Path(excel_path_str)

    if not excel_path.exists():
        print(f"{Fore.RED}Error: Excel file not found → {excel_path}{Style.RESET_ALL}")
        sys.exit(1)

    try:
        df = pd.read_excel(excel_path, sheet_name="All Results")
    except Exception as e:
        print(f"{Fore.RED}Error reading Excel file → {e}{Style.RESET_ALL}")
        sys.exit(1)

    if "Summary" in df.columns:
        df = df.drop(columns=["Summary"])

    return df.to_json(orient="records", lines=True)


# ----------------------------------------------------------
# Load Excel and convert to plain text table for saving
# ----------------------------------------------------------
def excel_to_text(gem_cfg: dict) -> str:
    """
    Load Excel again, drop Summary column, convert numeric fields,
    and return a clean text table for saving into inference.txt.
    """
    excel_path_str = gem_cfg.get("excel_path", "full_summarization_report.xlsx")
    excel_path = Path(excel_path_str)

    if not excel_path.exists():
        print(f"{Fore.RED}Error: Excel file not found → {excel_path}{Style.RESET_ALL}")
        sys.exit(1)

    try:
        df = pd.read_excel(excel_path, sheet_name="All Results")
    except Exception as e:
        print(f"{Fore.RED}Error reading Excel file → {e}{Style.RESET_ALL}")
        sys.exit(1)

    # Drop Summary if present
    if "Summary" in df.columns:
        df = df.drop(columns=["Summary"])

    # Convert numbers where possible
    df = df.apply(pd.to_numeric, errors="ignore")

    # Convert dataframe to readable text table
    return df.to_string(index=False)


# ----------------------------------------------------------
# Dynamic Prompt Builder
# ----------------------------------------------------------
def build_prompt(var_str: str) -> str:
    """
    Build the prompt sent to Gemini using dynamic Excel/JSON data.
    """
    return f"""
Analyze the following summarization model performance data and provide a comprehensive evaluation:

{var_str}

Please provide the following, in bullet points and max 200 words:

- Metric interpretations (Compression %, Density %, Cosine Similarity, Time):
  - what they mean
  - optimal ranges
  - whether higher/lower is better
- Performance rankings:
  - rank extractive models
  - rank abstractive models
  - best for speed, best for quality, best overall balance
- Red flags & issues:
  - concerning values, potential failures/hallucinations, outliers
- Practical recommendations:
  - best for speed-critical
  - best for quality-critical
  - best balanced
  - models to avoid or investigate
- Trade-offs:
  - speed vs quality
  - extractive vs abstractive and when to use each
  
  IMPORTANT:
Provide the output in plain text only.
Do NOT use markdown.
Do NOT use bold text.
Do NOT use asterisks or hyphens for bullets.
Keep formatting clean and readable.
"""


# ----------------------------------------------------------
# Save Gemini Output + Excel Text to inference.txt
# ----------------------------------------------------------
def save_output_to_txt(gemini_text: str, excel_text: str):
    """Save Gemini output + Excel numeric table into inference.txt"""
    file_path = Path("inference.txt")

    with file_path.open("w", encoding="utf-8") as f:
        f.write("GEMINI ANALYSIS\n")
        f.write("=" * 80 + "\n\n")
        f.write(gemini_text + "\n\n")

        f.write("EXCEL DATA (NUMERIC TABLE)\n")
        f.write("=" * 80 + "\n\n")
        f.write(excel_text + "\n")

    print(f"{Fore.GREEN}Output saved to: {file_path.resolve()}{Style.RESET_ALL}")


# ----------------------------------------------------------
# Main Program
# ----------------------------------------------------------
def main():
    cfg = load_config()
    gem_cfg = cfg.get("gemini", {})

    if not gem_cfg.get("enabled", True):
        print(
            f"{Fore.YELLOW}Gemini analysis disabled in config.yaml "
            f"(gemini.enabled = false). Skipping.{Style.RESET_ALL}"
        )
        return

    api_key = gem_cfg.get("api_key")
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        print(
            f"{Fore.RED}Error: Gemini API key not set in config.yaml "
            f"(gemini.api_key).{Style.RESET_ALL}"
        )
        sys.exit(1)

    model_name = gem_cfg.get("model", "gemini-2.5-flash")
    temperature = float(gem_cfg.get("temperature", 0.1))

    # Initialize Gemini client
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"{Fore.RED}Error initializing Gemini client. Check API key & installation.{Style.RESET_ALL}")
        print(f"Details: {e}")
        sys.exit(1)

    # Load data from Excel -> JSON string for prompt
    var_str = load_excel_json(gem_cfg)

    # Build dynamic LLM prompt
    prompt_text = build_prompt(var_str)

    print(f"{Fore.CYAN}Sending comprehensive analysis request to Gemini...{Style.RESET_ALL}")

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt_text],
            config=types.GenerateContentConfig(
                temperature=temperature
            ),
        )

        output_text = response.text.strip()

        print("\n" + "=" * 50)
        print("## Gemini LLM Analysis Result")
        print("=" * 50)
        print(output_text)
        print("=" * 50 + "\n")

        # Prepare Excel text table
        excel_text = excel_to_text(gem_cfg)

        # Save inference + Excel data to text file
        save_output_to_txt(output_text, excel_text)

    except Exception as e:
        print(f"{Fore.RED}--- ERROR: Failed to get response from Gemini ---{Style.RESET_ALL}")
        print(f"Details: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
