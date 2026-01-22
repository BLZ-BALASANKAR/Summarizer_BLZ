# """
# Excel Export Demo - Generate comprehensive Excel report with all metrics
# Input default: output_file_directory/Contract_doc_1pages_text.txt
# """

# from summarization_accelerator import SummarizationAccelerator
# from colorama import init, Fore, Style
# import sys
# import os
# import datetime

# # Initialize colorama
# init()

# def print_banner():
#     """Print a beautiful banner"""
#     print(Fore.CYAN + Style.BRIGHT)
#     print("╔" + "═"*78 + "╗")
#     print("║" + " "*18 + " EXCEL EXPORT DEMO - FULL REPORT" + " "*26 + "║")
#     print("║" + " "*10 + "Save all results with metrics to Excel spreadsheet" + " "*17 + "║")
#     print("╚" + "═"*78 + "╝")
#     print(Style.RESET_ALL)

# def load_input_text(filepath=None):
#     """
#     Load summarization input text from a file.
#     Default: output_file_directory/Contract_doc_1pages_text.txt
#     """
#     if filepath is None:
#         filepath = os.path.join("output_file_directory", "Contract_doc_1pages_text.txt")

#     # Expand user and make absolute for clarity
#     filepath = os.path.abspath(os.path.expanduser(filepath))

#     if not os.path.exists(filepath):
#         raise FileNotFoundError(
#             f"Input file '{filepath}' not found.\n"
#             "Please ensure the file exists. If you extracted text from a document earlier,\n"
#             "check the 'output_file_directory' folder for 'Contract_doc_1pages_text.txt'."
#         )
#     with open(filepath, "r", encoding="utf-8") as f:
#         return f.read()

# def _make_timestamped_name(base_name="full_summarization_report.xlsx"):
#     """Return a timestamped filename to avoid locking/permission issues."""
#     name, ext = os.path.splitext(base_name)
#     ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     return f"{name}_{ts}{ext}"

# def main():
#     print_banner()

#     # --- Important: call load_input_text() WITH NO ARG so it uses the default path ---
#     try:
#         text = load_input_text()   # uses output_file_directory/Contract_doc_1pages_text.txt by default
#     except Exception as e:
#         print(f"\n{Fore.RED} Error loading input file: {e}{Style.RESET_ALL}\n")
#         print(f"{Fore.YELLOW}Hint:{Style.RESET_ALL} Place 'Contract_doc_1pages_text.txt' inside the folder 'output_file_directory' (next to this script).")
#         sys.exit(1)

#     if not text or not text.strip():
#         print(f"\n{Fore.YELLOW} Input file is empty. Please ensure 'output_file_directory/Contract_doc_1pages_text.txt' has text and re-run.{Style.RESET_ALL}\n")
#         sys.exit(1)

#     print(f"\n{Fore.YELLOW} Sample Text Statistics:{Style.RESET_ALL}")
#     words = text.split()
#     print(f"  • Words: {len(words)}")
#     print(f"  • Characters: {len(text)}")
#     print(f"  • Sentences: ~{text.count('.')}\n")

#     print(f"{Fore.GREEN}  Initializing Summarization Accelerator...{Style.RESET_ALL}")
#     accelerator = SummarizationAccelerator(use_gpu=False)

#     print(f"{Fore.GREEN} Running ALL summarizers (Extractive + Abstractive)...{Style.RESET_ALL}")
#     print(f"{Fore.CYAN}   Note: First run will download models (~1-2GB per model){Style.RESET_ALL}")
#     print(f"{Fore.CYAN}   This may take 1-2 minutes...{Style.RESET_ALL}\n")

#     # Run BOTH extractive and abstractive summarization
#     results = accelerator.summarize(
#         text=text.strip(),
#         extractive=True,
#         abstractive=True,  # NOW ENABLED - will use BART, T5, PEGASUS
#         extractive_sentence_count=3,
#         abstractive_max_length=150,
#         abstractive_min_length=40
#     )

#     # Display results in table format
#     print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
#     print(f"{Fore.YELLOW}Results Preview:{Style.RESET_ALL}\n")
#     accelerator.print_results(results, verbose=False)

#     # Evaluate all summaries with a reference summary
#     print(f"\n{Fore.YELLOW} Evaluating all summaries with metrics...{Style.RESET_ALL}")
#     print(f"{Fore.CYAN}   Computing: ROUGE, BLEU, METEOR, Cosine Similarity, etc.{Style.RESET_ALL}\n")

#     # Create a reference summary for proper ROUGE/BLEU scoring
#     reference_summary = """Machine learning and artificial intelligence revolutionize technology 
#     by enabling computers to learn from data, understand language, and recognize images. These 
#     technologies power modern applications while raising important ethical considerations."""

#     evaluation = accelerator.evaluate_results(results, reference_summary=reference_summary)

#     # Show evaluation summary
#     accelerator.print_evaluation_report(evaluation, verbose=False)

#     # Export to Excel
#     print(f"\n{Fore.GREEN + Style.BRIGHT} EXPORTING TO EXCEL...{Style.RESET_ALL}\n")

#     excel_filename = "full_summarization_report.xlsx"
#     try:
#         accelerator.save_to_excel(results, evaluation, excel_filename)
#         saved_name = excel_filename
#     except PermissionError as pe:
#         # Try fallback timestamped filename
#         print(f"{Fore.RED} PermissionError while writing '{excel_filename}': {pe}{Style.RESET_ALL}")
#         fallback = _make_timestamped_name(excel_filename)
#         try:
#             accelerator.save_to_excel(results, evaluation, fallback)
#             saved_name = fallback
#             print(f"{Fore.GREEN} Successfully saved to fallback file: {saved_name}{Style.RESET_ALL}")
#         except Exception as e2:
#             print(f"{Fore.RED} Failed to save to fallback file as well: {e2}{Style.RESET_ALL}")
#             print("\nQuick checklist to try now (before re-running):")
#             print("  • Close Excel if the file is open.")
#             print("  • Check file properties and folder write permissions.")
#             print("  • Try running from a different folder (e.g., Desktop).")
#             raise

#     # Summary of what was saved
#     print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
#     print(f"{Fore.GREEN + Style.BRIGHT} EXPORT COMPLETE!{Style.RESET_ALL}\n")

#     print(f"{Fore.YELLOW} Excel file created: {Fore.GREEN + Style.BRIGHT}{saved_name}{Style.RESET_ALL}\n")

#     print(f"{Fore.CYAN}The Excel file contains:{Style.RESET_ALL}")
#     print(f"   {Fore.GREEN}Sheet 1:{Style.RESET_ALL} Extractive Summaries")
#     print(f"     - Method name, Type, Full summary text")
#     print(f"     - Word count, Execution time")
#     print(f"     - Compression %, Density %, Cosine similarity")
#     print(f"     - ROUGE-1, ROUGE-2, ROUGE-L F1 scores")
#     print(f"     - BLEU score, METEOR score")

#     if results.get('abstractive_summaries'):
#         print(f"\n   {Fore.MAGENTA}Sheet 2:{Style.RESET_ALL} Abstractive Summaries (BART, T5, PEGASUS)")
#         print(f"     - Model name, Type, Full summary text")
#         print(f"     - Word count, Execution time")
#         print(f"     - Compression %, Density %, Cosine similarity")
#         print(f"     - ROUGE-1, ROUGE-2, ROUGE-L F1 scores")
#         print(f"     - BLEU score, METEOR score")

#     print(f"\n   {Fore.YELLOW}Sheet 3:{Style.RESET_ALL} All Summaries Combined")
#     print(f"     - Side-by-side comparison of all methods")
#     print(f"     - Easy sorting and filtering")

#     print(f"\n  ℹ  {Fore.CYAN}Sheet 4:{Style.RESET_ALL} Metadata & Statistics")
#     print(f"     - Execution times, model counts, timestamps")
#     print(f"     - Original text information")

#     print(f"\n{Fore.GREEN} Pro Tip:{Style.RESET_ALL} Open the file in Excel to:")
#     print(f"   • Sort by any metric (ROUGE, BLEU, time, etc.)")
#     print(f"   • Filter to see only extractive or abstractive")
#     print(f"   • Create charts comparing different methods")
#     print(f"   • Find the best summarizer for your use case")

#     print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
#     print(f"     - Number of models used")
#     print(f"     - Timestamp")

#     print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")

#     print(f"\n{Fore.GREEN + Style.BRIGHT}🎉 SUCCESS!{Style.RESET_ALL}")
#     print(f"\n{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
#     print(f"  1. Open {Fore.CYAN}{saved_name}{Style.RESET_ALL} in Excel/LibreOffice/Google Sheets")
#     print(f"  2. Review all summaries and metrics")
#     print(f"  3. Compare different methods side-by-side")
#     print(f"  4. Identify the best performing summarizer for your needs")

#     print(f"\n{Fore.CYAN} Tip:{Style.RESET_ALL} The Excel file has formatted headers, borders, and auto-sized columns")
#     print(f"        for easy reading and analysis!\n")

#     # Cleanup
#     accelerator.cleanup()

# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         print(f"\n\n{Fore.YELLOW}  Demo interrupted by user{Style.RESET_ALL}")
#         sys.exit(0)
#     except Exception as e:
#         print(f"\n{Fore.RED} Error: {str(e)}{Style.RESET_ALL}")
#         import traceback
#         traceback.print_exc()
#         sys.exit(1)



"""
Excel Export Demo - Generate comprehensive Excel report with all metrics
Input default: paths.output_text from config.yaml (e.g. converted.txt)
"""

from summarization_accelerator import SummarizationAccelerator
from colorama import init, Fore, Style
import sys
import os
import datetime
import yaml

# Initialize colorama
init()

def load_config():
    """Load configuration from config.yaml"""
    try:
        with open("config.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"{Fore.RED}Error: Could not load config.yaml -> {e}{Style.RESET_ALL}")
        sys.exit(1)

def print_banner():
    """Print a simple ASCII banner (no Unicode)."""
    line = "=" * 78
    print(line)
    print(" SUPERVISED ML ACCELERATOR — EXCEL DEMO".center(78))
    print(line)

def load_input_text(filepath=None):
    """
    Load summarization input text from a file.
    Default: paths.output_text from config.yaml (e.g. converted.txt)
    """
    cfg = load_config()
    default_txt = cfg["paths"].get("output_text", "converted.txt")

    if filepath is None:
        filepath = default_txt

    filepath = os.path.abspath(os.path.expanduser(filepath))

    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Input file '{filepath}' not found.\n"
            f"Expected text file (paths.output_text) from config.yaml.\n"
            "Hint: run doc_to_txt.py first to convert your PDF/DOC/DOCX."
        )
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
    
def _make_timestamped_name(base_name="full_summarization_report.xlsx"):
    # You said no timestamp, so just return the base name.
    return base_name


def main():
    print_banner()

    try:
        text = load_input_text()   # uses paths.output_text from config.yaml
    except Exception as e:
        print(f"\n{Fore.RED} Error loading input file: {e}{Style.RESET_ALL}\n")
        sys.exit(1)

    if not text or not text.strip():
        print(f"\n{Fore.YELLOW} Input file is empty. Please ensure the converted text file has content and re-run.{Style.RESET_ALL}\n")
        sys.exit(1)

    print(f"\n{Fore.YELLOW} Sample Text Statistics:{Style.RESET_ALL}")
    words = text.split()
    print(f"  - Words: {len(words)}")
    print(f"  - Characters: {len(text)}")
    print(f"  - Sentences: ~{text.count('.')}\n")

    print(f"{Fore.GREEN}  Initializing Summarization Accelerator...{Style.RESET_ALL}")
    accelerator = SummarizationAccelerator(use_gpu=False)

    print(f"{Fore.GREEN} Running ALL summarizers (Extractive + Abstractive)...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   Note: First run will download models (~1-2GB per model){Style.RESET_ALL}")
    print(f"{Fore.CYAN}   This may take some time...{Style.RESET_ALL}\n")

    results = accelerator.summarize(
        text=text.strip(),
        extractive=True,
        abstractive=True,
        extractive_sentence_count=3,
        abstractive_max_length=150,
        abstractive_min_length=40
    )

    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Results Preview:{Style.RESET_ALL}\n")
    accelerator.print_results(results, verbose=False)

    print(f"\n{Fore.YELLOW} Evaluating all summaries with metrics...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   Computing: ROUGE, BLEU, METEOR, Cosine Similarity, etc.{Style.RESET_ALL}\n")

    reference_summary = """Machine learning and artificial intelligence revolutionize technology 
    by enabling computers to learn from data, understand language, and recognize images. These 
    technologies power modern applications while raising important ethical considerations."""

    evaluation = accelerator.evaluate_results(results, reference_summary=reference_summary)

    # Merge evaluation into results and save to JSON for the frontend
    results['evaluation'] = evaluation
    accelerator.save_results(results, "results.json")

    accelerator.print_evaluation_report(evaluation, verbose=False)

    print(f"\n{Fore.GREEN + Style.BRIGHT} EXPORTING TO EXCEL...{Style.RESET_ALL}\n")

    excel_filename = "full_summarization_report.xlsx"
    saved_name = None  # make sure the variable exists in all cases

    try:
        accelerator.save_to_excel(results, evaluation, excel_filename)
        # we always use the same name; you can use absolute path if you prefer
        saved_name = excel_filename
        print(f"{Fore.GREEN} Successfully saved: {saved_name}{Style.RESET_ALL}")

    except PermissionError as pe:
        print(f"{Fore.RED} PermissionError while writing '{excel_filename}': {pe}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW} Please close the file in Excel and run again.{Style.RESET_ALL}")
        saved_name = None

    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.GREEN + Style.BRIGHT} EXPORT COMPLETE!{Style.RESET_ALL}\n")

    if saved_name:
        print(f"{Fore.YELLOW} Excel file created: {Fore.GREEN + Style.BRIGHT}{saved_name}{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.RED} Excel file was not created due to an earlier error.{Style.RESET_ALL}\n")

    # (rest of your pretty printing left unchanged)
    print(f"{Fore.CYAN}The Excel file contains:{Style.RESET_ALL}")
    print(f"   {Fore.GREEN}Sheet 1:{Style.RESET_ALL} Extractive Summaries")
    print(f"     - Method name, Type, Full summary text")
    print(f"     - Word count, Execution time")
    print(f"     - Compression %, Density %, Cosine similarity")
    print(f"     - ROUGE-1, ROUGE-2, ROUGE-L F1 scores")
    print(f"     - BLEU score, METEOR score")

    if results.get('abstractive_summaries'):
        print(f"\n   {Fore.MAGENTA}Sheet 2:{Style.RESET_ALL} Abstractive Summaries (BART, T5, PEGASUS)")
        print(f"     - Model name, Type, Full summary text")
        print(f"     - Word count, Execution time")
        print(f"     - Compression %, Density %, Cosine similarity")
        print(f"     - ROUGE-1, ROUGE-2, ROUGE-L F1 scores")
        print(f"     - BLEU score, METEOR score")

    print(f"\n   {Fore.YELLOW}Sheet 3:{Style.RESET_ALL} All Summaries Combined")
    print(f"     - Side-by-side comparison of all methods")
    print(f"     - Easy sorting and filtering")

    print(f"\n  [i]  {Fore.CYAN}Sheet 4:{Style.RESET_ALL} Metadata & Statistics")
    print(f"     - Execution times, model counts, timestamps")
    print(f"     - Original text information")

    print(f"\n{Fore.GREEN} Pro Tip:{Style.RESET_ALL} Open the file in Excel to:")
    print(f"   - Sort by any metric (ROUGE, BLEU, time, etc.)")
    print(f"   - Filter to see only extractive or abstractive")
    print(f"   - Create charts comparing different methods")
    print(f"   - Find the best summarizer for your use case\n")

    accelerator.cleanup()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}  Demo interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED} Error: {str(e)}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
