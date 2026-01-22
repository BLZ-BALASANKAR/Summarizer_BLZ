"""
gemini_analysis.py

Call Google Gemini to analyze summarization model performance AND perform Tone/Style customization.
Uses API key and settings from config.yaml (gemini section).

Flow:
- Load config.yaml
- Analyze performance (Excel -> Gemini)
- Perform Style Transfer (Best Summary -> Gemini -> Stylized Text)
"""

import sys
import json
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
        print(f"{Fore.RED}Error: Could not load config.yaml -> {e}{Style.RESET_ALL}")
        sys.exit(1)


# ----------------------------------------------------------
# Load data
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
        print(f"{Fore.RED}Error: Excel file not found -> {excel_path}{Style.RESET_ALL}")
        sys.exit(1)

    try:
        df = pd.read_excel(excel_path, sheet_name="All Results")
    except Exception as e:
        print(f"{Fore.RED}Error reading Excel file -> {e}{Style.RESET_ALL}")
        sys.exit(1)

    if "Summary" in df.columns:
        df = df.drop(columns=["Summary"])

    return df.to_json(orient="records", lines=True)

def excel_to_text(gem_cfg: dict) -> str:
    """
    Load Excel again, convert numeric fields, return text table.
    """
    excel_path_str = gem_cfg.get("excel_path", "full_summarization_report.xlsx")
    excel_path = Path(excel_path_str)

    if not excel_path.exists():
        return ""

    try:
        df = pd.read_excel(excel_path, sheet_name="All Results")
    except:
        return ""

    if "Summary" in df.columns:
        df = df.drop(columns=["Summary"])

    df = df.apply(pd.to_numeric, errors="ignore")
    return df.to_string(index=False)

def get_best_summary_text() -> str:
    """
    Load results.json and pick the best summary to style.
    Priority: Abstractive (BART/T5) -> Extractive -> First available.
    """
    path = Path("results.json")
    if not path.exists():
        return ""
    
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Try abstractive first
        abs_sums = data.get("abstractive_summaries", {})
        if "bart" in abs_sums and "summary" in abs_sums["bart"]:
            return abs_sums["bart"]["summary"]
        if "t5" in abs_sums and "summary" in abs_sums["t5"]:
            return abs_sums["t5"]["summary"]
            
        # Any abstractive
        for k, v in abs_sums.items():
             if "summary" in v: return v["summary"]
             
        # Any extractive
        ext_sums = data.get("extractive_summaries", {})
        for k, v in ext_sums.items():
             if "summary" in v: return v["summary"]
             
    except Exception as e:
        print(f"Error reading results.json: {e}")
        
    return ""


# ----------------------------------------------------------
# Prompts
# ----------------------------------------------------------
def build_analysis_prompt(var_str: str) -> str:
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

  IMPORTANT:
Provide the output in plain text only.
Do NOT use markdown.
Do NOT use bold text.
Keep formatting clean and readable.
"""

def build_style_prompt(original_summary: str, style: str) -> str:
    return f"""
Rewrite the following summary in a "{style}" tone/style.
Keep the core information accurate but change the phrasing and vocabulary to match the requested style.

Original Summary:
{original_summary}

Stylized Summary ({style}):
"""


# ----------------------------------------------------------
# Main Program
# ----------------------------------------------------------
def main():
    cfg = load_config()
    gem_cfg = cfg.get("gemini", {})

    if not gem_cfg.get("enabled", True):
        return

    api_key = gem_cfg.get("api_key")
    if not api_key:
        print(f"{Fore.RED}Error: Gemini API key not set.{Style.RESET_ALL}")
        sys.exit(1)

    model_name = gem_cfg.get("model", "gemini-2.5-flash")
    temperature = float(gem_cfg.get("temperature", 0.1))
    target_style = gem_cfg.get("style", "Standard")

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"{Fore.RED}Error initializing Gemini: {e}{Style.RESET_ALL}")
        sys.exit(1)


    # --- TASK 1: PERFORMANCE ANALYSIS ---
    print(f"{Fore.CYAN}Sending analysis request to Gemini...{Style.RESET_ALL}")
    
    var_str = load_excel_json(gem_cfg)
    prompt_text = build_analysis_prompt(var_str)

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt_text],
            config=types.GenerateContentConfig(temperature=temperature),
        )
        analysis_text = response.text.strip()
        
        # Save analysis
        excel_text = excel_to_text(gem_cfg)
        with open("inference.txt", "w", encoding="utf-8") as f:
            f.write("GEMINI ANALYSIS\n" + "="*80 + "\n\n")
            f.write(analysis_text + "\n\n")
            f.write("EXCEL DATA\n" + "="*80 + "\n\n")
            f.write(excel_text)
            
        print(f"{Fore.GREEN}Analysis saved to inference.txt{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}Analysis failed: {e}{Style.RESET_ALL}")


    # --- TASK 2: STYLE TRANSFER ---
    if target_style and target_style.lower() != "standard":
        print(f"\n{Fore.CYAN}Performing Style Transfer ({target_style})...{Style.RESET_ALL}")
        
        best_sum = get_best_summary_text()
        if best_sum:
            style_prompt = build_style_prompt(best_sum, target_style)
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[style_prompt],
                    config=types.GenerateContentConfig(temperature=0.7), # Higher temp for creativity
                )
                stylized_text = response.text.strip()
                
                with open("stylized_summary.txt", "w", encoding="utf-8") as f:
                    f.write(stylized_text)
                    
                print(f"{Fore.GREEN}Stylized summary saved to stylized_summary.txt{Style.RESET_ALL}")
                
            except Exception as e:
                 print(f"{Fore.RED}Style transfer failed: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}No summary found in results.json to stylize.{Style.RESET_ALL}")
    else:
        # If standard, just copy the best summary to stylized_summary.txt for consistency in UI
        best_sum = get_best_summary_text()
        if best_sum:
             with open("stylized_summary.txt", "w", encoding="utf-8") as f:
                    f.write(best_sum)


if __name__ == "__main__":
    main()
