"""
Summarization Accelerator - Main Orchestrator
Coordinates multiple summarization algorithms and aggregates results
Includes evaluation metrics for comparing summaries
"""

from extractive_summarizers import ExtractiveSummarizers
from abstractive_summarizers import AbstractiveSummarizers
from config import DEFAULT_ABSTRACTIVE_TO_RUN
from evaluation_metrics import SummarizationEvaluator
from typing import Dict
import time
import json


class SummarizationAccelerator:
    """
    Main class that orchestrates multiple summarization techniques
    and provides comprehensive summarization results
    """

    def __init__(self, use_gpu: bool = True, language: str = "english"):
        """
        Initialize the Summarization Accelerator

        Args:
            use_gpu: Whether to use GPU for abstractive models
            language: Language for text processing
        """
        self.extractive = ExtractiveSummarizers(language=language)
        self.abstractive = AbstractiveSummarizers(use_gpu=use_gpu)
        self.evaluator = SummarizationEvaluator()

    def summarize(
        self,
        text: str,
        extractive: bool = True,
        abstractive: bool = True,
        extractive_sentence_count: int = 3,
        abstractive_max_length: int = 150,
        abstractive_min_length: int = 50,
    ) -> Dict:
        """
        Run multiple summarizers on the input text

        Args:
            text: Input text to summarize
            extractive: Whether to run extractive summarizers
            abstractive: Whether to run abstractive summarizers
            extractive_sentence_count: Number of sentences for extractive summaries
            abstractive_max_length: Maximum length for abstractive summaries
            abstractive_min_length: Minimum length for abstractive summaries

        Returns:
            Dictionary containing all summarization results
        """
        from colorama import Fore, Style

        start_time = time.time()
        results = {
            "input_text": text,
            "input_length": len(text),
            "extractive_summaries": {},
            "abstractive_summaries": {},
            "metadata": {},
        }

        # Run extractive summarizers
        if extractive:
            print(f"\nRunning Extractive Summarizers...{Style.RESET_ALL}")
            try:
                extractive_results = self.extractive.summarize_all(
                    text, sentence_count=extractive_sentence_count
                )
                results["extractive_summaries"] = extractive_results
                print(
                    f"{Fore.GREEN}Completed {len(extractive_results)} extractive algorithms{Style.RESET_ALL}"
                )
            except Exception as e:
                print(
                    f"{Fore.RED}Error in extractive summarization: {str(e)}{Style.RESET_ALL}"
                )
                results["extractive_summaries"] = {"error": str(e)}

        # Run abstractive summarizers
        if abstractive:
            print(f"\nRunning Abstractive Summarizers...{Style.RESET_ALL}")

            try:
                abstractive_results = {}

                for model_key in DEFAULT_ABSTRACTIVE_TO_RUN:
                    try:
                        if model_key == "bart":
                            abstractive_results["bart"] = self.abstractive.bart_summarize(
                                text, abstractive_max_length, abstractive_min_length
                            )

                        elif model_key == "t5":
                            abstractive_results["t5"] = self.abstractive.t5_summarize(
                                text, abstractive_max_length, abstractive_min_length
                            )

                        elif model_key == "pegasus_xsum":
                            abstractive_results[
                                "pegasus_xsum"
                            ] = self.abstractive.pegasus_summarize(
                                text, abstractive_max_length, abstractive_min_length
                            )

                        elif model_key == "flan_t5_base":
                            abstractive_results[
                                "flan_t5_base"
                            ] = self.abstractive.flan_t5_summarize(
                                text,
                                abstractive_max_length,
                                abstractive_min_length,
                                variant="base",
                            )

                        elif model_key == "flan_t5_large":
                            abstractive_results[
                                "flan_t5_large"
                            ] = self.abstractive.flan_t5_summarize(
                                text,
                                abstractive_max_length,
                                abstractive_min_length,
                                variant="large",
                            )

                        elif model_key == "pegasus_large":
                            abstractive_results[
                                "pegasus_large"
                            ] = self.abstractive.pegasus_large_summarize(
                                text, abstractive_max_length, abstractive_min_length
                            )

                        elif model_key == "bigbird_pegasus":
                            abstractive_results[
                                "bigbird_pegasus"
                            ] = self.abstractive.bigbird_pegasus_summarize(
                                text, abstractive_max_length, abstractive_min_length
                            )

                        elif model_key == "led":
                            abstractive_results[
                                "led"
                            ] = self.abstractive.led_summarize(
                                text,
                                max_length=abstractive_max_length,
                                min_length=abstractive_min_length,
                            )

                    except Exception as model_error:
                        abstractive_results[model_key] = {"error": str(model_error)}

                results["abstractive_summaries"] = abstractive_results
                print(
                    f"{Fore.GREEN}Completed {len(abstractive_results)} abstractive models{Style.RESET_ALL}"
                )

            except Exception as e:
                print(
                    f"{Fore.RED}Error in abstractive summarization: {str(e)}{Style.RESET_ALL}"
                )
                results["abstractive_summaries"] = {"error": str(e)}

        # Add metadata
        results["metadata"] = {
            "total_execution_time": time.time() - start_time,
            "extractive_count": len(results["extractive_summaries"]),
            "abstractive_count": len(results["abstractive_summaries"]),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        return results

    def get_best_summary(self, results: Dict, method: str = "shortest") -> Dict:
        """
        Select the best summary based on a criterion

        Args:
            results: Results from summarize() method
            method: Selection method ('shortest', 'longest', 'first')

        Returns:
            Dictionary with the selected best summary
        """
        all_summaries = []

        # Collect all summaries
        for algo, data in results.get("extractive_summaries", {}).items():
            if "summary" in data:
                all_summaries.append(
                    {
                        "algorithm": algo,
                        "type": "extractive",
                        "summary": data["summary"],
                        "length": len(data["summary"]),
                    }
                )

        for model, data in results.get("abstractive_summaries", {}).items():
            if "summary" in data:
                all_summaries.append(
                    {
                        "model": model,
                        "type": "abstractive",
                        "summary": data["summary"],
                        "length": len(data["summary"]),
                    }
                )

        if not all_summaries:
            return {"error": "No summaries available"}

        # Select best based on method
        if method == "shortest":
            best = min(all_summaries, key=lambda x: x["length"])
        elif method == "longest":
            best = max(all_summaries, key=lambda x: x["length"])
        else:  # first
            best = all_summaries[0]

        return best

    def print_results(self, results: Dict, verbose: bool = True):
        """
        Print results in a readable format (ASCII-safe)
        """
        from colorama import Fore, Style

        print("\n" + "=" * 80)
        print("SUMMARIZATION RESULTS".center(80))
        print("=" * 80 + "\n")

        # Original text stats
        if results.get("input_text"):
            original = results["input_text"]
            words = original.split()
            print(
                Fore.YELLOW
                + f"Original Text: {len(words)} words | {len(original)} characters"
                + Style.RESET_ALL
                + "\n"
            )

        # Extractive summaries
        if results.get("extractive_summaries"):
            print(Fore.GREEN + Style.BRIGHT + "EXTRACTIVE SUMMARIES" + Style.RESET_ALL)
            print("-" * 80)
            header = f"{'#':<3} | {'Method':<20} | {'Words':>6} | {'Time (s)':>8} | Preview"
            print(header)
            print("-" * 80)

            for idx, (algo, data) in enumerate(
                results["extractive_summaries"].items(), 1
            ):
                if "error" in data:
                    msg = f"ERROR: {data['error'][:60]}"
                    print(f"{idx:<3} | {algo[:20]:<20} | {'':>6} | {'':>8} | {msg}")
                else:
                    summary = data["summary"]
                    words_list = summary.split()
                    preview = summary[:60] + "..." if len(summary) > 60 else summary
                    # Sanitize for Windows console
                    try:
                        preview = preview.encode(sys.stdout.encoding or 'utf-8', 'replace').decode(sys.stdout.encoding or 'utf-8')
                    except:
                        preview = preview.encode('ascii', 'replace').decode('ascii')
                        
                    time_s = data.get("execution_time", 0.0)
                    print(
                        f"{idx:<3} | {algo.replace('_', ' ').title()[:20]:<20} | {len(words_list):>6} | {time_s:>8.3f} | {preview}"
                    )

            print("-" * 80 + "\n")

        # Abstractive summaries
        if results.get("abstractive_summaries"):
            print(
                Fore.MAGENTA + Style.BRIGHT + "ABSTRACTIVE SUMMARIES" + Style.RESET_ALL
            )
            print("-" * 80)
            header = f"{'#':<3} | {'Model':<20} | {'Words':>6} | {'Time (s)':>8} | Preview"
            print(header)
            print("-" * 80)

            for idx, (model, data) in enumerate(
                results["abstractive_summaries"].items(), 1
            ):
                if "error" in data:
                    msg = f"ERROR: {data['error'][:60]}"
                    print(f"{idx:<3} | {model[:20]:<20} | {'':>6} | {'':>8} | {msg}")
                else:
                    summary = data["summary"]
                    words_list = summary.split()
                    preview = summary[:60] + "..." if len(summary) > 60 else summary
                    # Sanitize for Windows console
                    try:
                        preview = preview.encode(sys.stdout.encoding or 'utf-8', 'replace').decode(sys.stdout.encoding or 'utf-8')
                    except:
                        preview = preview.encode('ascii', 'replace').decode('ascii')

                    time_s = data.get("execution_time", 0.0)
                    print(
                        f"{idx:<3} | {model.replace('_', ' ').title()[:20]:<20} | {len(words_list):>6} | {time_s:>8.3f} | {preview}"
                    )

            print("-" * 80 + "\n")

        # Metadata
        if verbose and results.get("metadata"):
            meta = results["metadata"]
            print(Fore.YELLOW + Style.BRIGHT + "EXECUTION SUMMARY" + Style.RESET_ALL)
            print("-" * 50)
            print(
                f"{'Total Execution Time (s)':<30} : {meta.get('total_execution_time', 0):>10.2f}"
            )
            print(
                f"{'Extractive Models Used':<30} : {meta.get('extractive_count', 0):>10}"
            )
            print(
                f"{'Abstractive Models Used':<30} : {meta.get('abstractive_count', 0):>10}"
            )
            print(f"{'Timestamp':<30} : {meta.get('timestamp', ''):>10}")
            print("-" * 50 + "\n")

    def save_results(self, results: Dict, filename: str = "results.json"):
        """
        Save results to a JSON file
        """
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"[OK] Results saved to {filename}")

    def save_to_excel(
        self,
        results: Dict,
        evaluation_results: Dict = None,
        filename: str = "full_summarization_report.xlsx",
    ):
        """
        Save all summarization results and metrics to a single Excel file.
        Always saves to 'full_summarization_report.xlsx'.
        """
        import pandas as pd
        from openpyxl import load_workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from colorama import Fore, Style

        # 🔒 Force a fixed filename
        filename = "full_summarization_report.xlsx"

        # Create a Pandas Excel writer
        writer = pd.ExcelWriter(filename, engine="openpyxl")

        # Sheet 1: Extractive Summaries
        if results.get("extractive_summaries"):
            extractive_data = []
            for algo, data in results["extractive_summaries"].items():
                if "error" not in data:
                    row = {
                        "Method": algo.replace("_", " ").title(),
                        "Type": "Extractive",
                        "Summary": data["summary"],
                        "Word Count": len(data["summary"].split()),
                        "Execution Time (s)": round(
                            data.get("execution_time", 0), 3
                        ),
                    }

                    # Add evaluation metrics if available
                    if (
                        evaluation_results
                        and evaluation_results.get("extractive_evaluations")
                    ):
                        metrics = evaluation_results["extractive_evaluations"].get(
                            algo, {}
                        )
                        row["Compression Ratio (%)"] = round(
                            metrics.get("compression_ratio", 0), 2
                        )
                        row["Density (%)"] = round(
                            metrics.get("density", 0), 2
                        )
                        row["Cosine Similarity"] = round(
                            metrics.get("text_similarity", 0), 2
                        )

                        rouge = metrics.get("rouge", {})
                        if "error" not in rouge:
                            row["ROUGE-1 F1"] = round(
                                rouge.get("rouge1_f", 0), 2
                            )
                            row["ROUGE-2 F1"] = round(
                                rouge.get("rouge2_f", 0), 2
                            )
                            row["ROUGE-L F1"] = round(
                                rouge.get("rougeL_f", 0), 2
                            )

                        bleu = metrics.get("bleu", {})
                        if "error" not in bleu:
                            row["BLEU Score"] = round(
                                bleu.get("bleu_overall", 0), 2
                            )

                        meteor = metrics.get("meteor", {})
                        if "error" not in meteor:
                            row["METEOR Score"] = round(
                                meteor.get("meteor", 0), 2
                            )

                    extractive_data.append(row)

            if extractive_data:
                df_extractive = pd.DataFrame(extractive_data)
                df_extractive.to_excel(
                    writer, sheet_name="Extractive Summaries", index=False
                )

        # Sheet 2: Abstractive Summaries
        if results.get("abstractive_summaries"):
            abstractive_data = []
            for model, data in results["abstractive_summaries"].items():
                if "error" not in data:
                    row = {
                        "Model": model.replace("_", " ").title(),
                        "Type": "Abstractive",
                        "Summary": data["summary"],
                        "Word Count": len(data["summary"].split()),
                        "Execution Time (s)": round(
                            data.get("execution_time", 0), 3
                        ),
                    }

                    if (
                        evaluation_results
                        and evaluation_results.get("abstractive_evaluations")
                    ):
                        metrics = evaluation_results["abstractive_evaluations"].get(
                            model, {}
                        )
                        row["Compression Ratio (%)"] = round(
                            metrics.get("compression_ratio", 0), 2
                        )
                        row["Density (%)"] = round(
                            metrics.get("density", 0), 2
                        )
                        row["Cosine Similarity"] = round(
                            metrics.get("text_similarity", 0), 2
                        )

                        rouge = metrics.get("rouge", {})
                        if "error" not in rouge:
                            row["ROUGE-1 F1"] = round(
                                rouge.get("rouge1_f", 0), 2
                            )
                            row["ROUGE-2 F1"] = round(
                                rouge.get("rouge2_f", 0), 2
                            )
                            row["ROUGE-L F1"] = round(
                                rouge.get("rougeL_f", 0), 2
                            )

                        bleu = metrics.get("bleu", {})
                        if "error" not in bleu:
                            row["BLEU Score"] = round(
                                bleu.get("bleu_overall", 0), 2
                            )

                        meteor = metrics.get("meteor", {})
                        if "error" not in meteor:
                            row["METEOR Score"] = round(
                                meteor.get("meteor", 0), 2
                            )

                    abstractive_data.append(row)

            if abstractive_data:
                df_abstractive = pd.DataFrame(abstractive_data)
                df_abstractive.to_excel(
                    writer, sheet_name="Abstractive Summaries", index=False
                )

        # Sheet 3: Combined Summary
        all_data = []
        if results.get("extractive_summaries"):
            for algo, data in results["extractive_summaries"].items():
                if "error" not in data:
                    row = {
                        "Method/Model": algo.replace("_", " ").title(),
                        "Type": "Extractive",
                        "Summary": data["summary"],
                        "Word Count": len(data["summary"].split()),
                        "Time (s)": round(data.get("execution_time", 0), 3),
                    }
                    if (
                        evaluation_results
                        and evaluation_results.get("extractive_evaluations")
                    ):
                        metrics = evaluation_results["extractive_evaluations"].get(
                            algo, {}
                        )
                        row["Compression %"] = round(
                            metrics.get("compression_ratio", 0), 2
                        )
                        row["Density %"] = round(
                            metrics.get("density", 0), 2
                        )
                        row["Cosine Sim"] = round(
                            metrics.get("text_similarity", 0), 2
                        )
                    all_data.append(row)

        if results.get("abstractive_summaries"):
            for model, data in results["abstractive_summaries"].items():
                if "error" not in data:
                    row = {
                        "Method/Model": model.replace("_", " ").title(),
                        "Type": "Abstractive",
                        "Summary": data["summary"],
                        "Word Count": len(data["summary"].split()),
                        "Time (s)": round(data.get("execution_time", 0), 3),
                    }
                    if (
                        evaluation_results
                        and evaluation_results.get("abstractive_evaluations")
                    ):
                        metrics = evaluation_results["abstractive_evaluations"].get(
                            model, {}
                        )
                        row["Compression %"] = round(
                            metrics.get("compression_ratio", 0), 2
                        )
                        row["Density %"] = round(
                            metrics.get("density", 0), 2
                        )
                        row["Cosine Sim"] = round(
                            metrics.get("text_similarity", 0), 2
                        )
                    all_data.append(row)

        if all_data:
            df_combined = pd.DataFrame(all_data)
            df_combined.to_excel(
                writer, sheet_name="All Results", index=False
            )

        # Sheet 4: Metadata
        metadata_data = []
        if results.get("metadata"):
            meta = results["metadata"]
            metadata_data = [
                {
                    "Metric": "Total Execution Time (s)",
                    "Value": round(meta.get("total_execution_time", 0), 2),
                },
                {
                    "Metric": "Extractive Models Used",
                    "Value": meta.get("extractive_count", 0),
                },
                {
                    "Metric": "Abstractive Models Used",
                    "Value": meta.get("abstractive_count", 0),
                },
                {"Metric": "Timestamp", "Value": meta.get("timestamp", "")},
            ]

            if results.get("input_text"):
                metadata_data.insert(
                    0,
                    {
                        "Metric": "Original Word Count",
                        "Value": len(results["input_text"].split()),
                    },
                )
                metadata_data.insert(
                    1,
                    {
                        "Metric": "Original Character Count",
                        "Value": len(results["input_text"]),
                    },
                )

        if metadata_data:
            df_metadata = pd.DataFrame(metadata_data)
            df_metadata.to_excel(
                writer, sheet_name="Metadata", index=False
            )

        writer.close()

        # Apply formatting
        wb = load_workbook(filename)

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]

            header_fill = PatternFill(
                start_color="4472C4", end_color="4472C4", fill_type="solid"
            )
            header_font = Font(bold=True, color="FFFFFF", size=11)
            border = Border(
                left=Side(style="thin"),
                right=Side(style="thin"),
                top=Side(style="thin"),
                bottom=Side(style="thin"),
            )

            # Header row
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(
                    horizontal="center", vertical="center", wrap_text=True
                )
                cell.border = border

            # Columns
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter

                for cell in column:
                    cell.border = border
                    cell.alignment = Alignment(vertical="top", wrap_text=True)
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except Exception:
                        pass

                adjusted_width = min(max_length + 2, 100)
                header_val = str(ws[f"{column_letter}1"].value)
                if column_letter == "C" or "Summary" in header_val:
                    adjusted_width = 80

                ws.column_dimensions[column_letter].width = adjusted_width

            # Row height
            for row in ws.iter_rows(min_row=2):
                ws.row_dimensions[row[0].row].height = 60

        wb.save(filename)

        print(
            f"{Fore.GREEN}Results saved to Excel file: {filename}{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}Sheets created: {', '.join(wb.sheetnames)}{Style.RESET_ALL}"
        )

    def evaluate_results(self, results: Dict, reference_summary: str = None) -> Dict:
        """
        Evaluate all generated summaries using multiple metrics
        """
        original_text = results.get("input_text", "")
        evaluation_results = {
            "extractive_evaluations": {},
            "abstractive_evaluations": {},
        }

        # Extractive
        for algo, data in results.get("extractive_summaries", {}).items():
            if "summary" in data:
                evaluation_results["extractive_evaluations"][algo] = (
                    self.evaluator.evaluate_summary(
                        original_text, data["summary"], reference_summary
                    )
                )

        # Abstractive
        for model, data in results.get("abstractive_summaries", {}).items():
            if "summary" in data:
                evaluation_results["abstractive_evaluations"][model] = (
                    self.evaluator.evaluate_summary(
                        original_text, data["summary"], reference_summary
                    )
                )

        return evaluation_results

    def print_evaluation_report(self, evaluation_results: Dict, verbose: bool = True):
        """
        Print evaluation report in a readable ASCII-safe format
        """
        from colorama import Fore, Style

        print("\n" + "=" * 80)
        print("EVALUATION REPORT".center(80))
        print("=" * 80 + "\n")

        # Extractive evaluations
        if evaluation_results.get("extractive_evaluations"):
            print(
                Fore.GREEN
                + Style.BRIGHT
                + "EXTRACTIVE SUMMARIES EVALUATION"
                + Style.RESET_ALL
            )

            if verbose:
                # UPDATED: Assuming metrics are 0-100, formatting with .2f and %
                header = (
                    f"{'#':<3} | {'Method':<16} | {'Words':>6} | {'Compress':>10} | "
                    f"{'Density':>8} | {'Cosine':>8} | {'ROUGE-1 (P/R/F1)':>20} | "
                    f"{'ROUGE-2 (P/R/F1)':>20} | {'BLEU':>8}"
                )
                print("-" * len(header))
                print(header)
                print("-" * len(header))

                for idx, (algo, metrics) in enumerate(
                    evaluation_results["extractive_evaluations"].items(), 1
                ):
                    rouge = metrics.get("rouge", {})
                    bleu = metrics.get("bleu", {})

                    if "error" not in rouge:
                        rouge1_str = (
                            f"{rouge.get('rouge1_p', 0):.2f}/"
                            f"{rouge.get('rouge1_r', 0):.2f}/"
                            f"{rouge.get('rouge1_f', 0):.2f}"
                        )
                        rouge2_str = (
                            f"{rouge.get('rouge2_p', 0):.2f}/"
                            f"{rouge.get('rouge2_r', 0):.2f}/"
                            f"{rouge.get('rouge2_f', 0):.2f}"
                        )
                    else:
                        rouge1_str = "N/A"
                        rouge2_str = "N/A"

                    if "error" not in bleu:
                        bleu_str = f"{bleu.get('bleu_overall', 0):.4f}"
                    else:
                        bleu_str = "N/A"

                    print(
                        f"{idx:<3} | {algo.replace('_',' ').title()[:16]:<16} | "
                        f"{metrics.get('generated_summary_length', 0):>6} | "
                        f"{metrics.get('compression_ratio', 0):>9.2f}% | "
                        f"{metrics.get('density', 0):>7.2f}% | "
                        f"{metrics.get('text_similarity', 0):>8.2f} | "
                        f"{rouge1_str:>20} | {rouge2_str:>20} | {bleu_str:>8}"
                    )

                print("-" * len(header) + "\n")
            else:
                header = (
                    f"{'#':<3} | {'Method':<20} | {'Words':>6} | "
                    f"{'Compress':>10} | {'Density':>8} | {'Cosine':>8}"
                )
                print("-" * len(header))
                print(header)
                print("-" * len(header))

                for idx, (algo, metrics) in enumerate(
                    evaluation_results["extractive_evaluations"].items(), 1
                ):
                    print(
                        f"{idx:<3} | {algo.replace('_',' ').title()[:20]:<20} | "
                        f"{metrics.get('generated_summary_length', 0):>6} | "
                        f"{metrics.get('compression_ratio', 0):>9.2f}% | "
                        f"{metrics.get('density', 0):>7.2f}% | "
                        f"{metrics.get('text_similarity', 0):>8.2f}"
                    )

                print("-" * len(header) + "\n")

        # Abstractive evaluations
        if evaluation_results.get("abstractive_evaluations"):
            print(
                Fore.MAGENTA
                + Style.BRIGHT
                + "ABSTRACTIVE SUMMARIES EVALUATION"
                + Style.RESET_ALL
            )

            if verbose:
                header = (
                    f"{'#':<3} | {'Model':<16} | {'Words':>6} | {'Compress':>10} | "
                    f"{'Density':>8} | {'Cosine':>8} | {'ROUGE-1 (P/R/F1)':>20} | "
                    f"{'ROUGE-2 (P/R/F1)':>20} | {'BLEU':>8}"
                )
                print("-" * len(header))
                print(header)
                print("-" * len(header))

                for idx, (model, metrics) in enumerate(
                    evaluation_results["abstractive_evaluations"].items(), 1
                ):
                    rouge = metrics.get("rouge", {})
                    bleu = metrics.get("bleu", {})

                    if "error" not in rouge:
                        rouge1_str = (
                            f"{rouge.get('rouge1_p', 0):.2f}/"
                            f"{rouge.get('rouge1_r', 0):.2f}/"
                            f"{rouge.get('rouge1_f', 0):.2f}"
                        )
                        rouge2_str = (
                            f"{rouge.get('rouge2_p', 0):.2f}/"
                            f"{rouge.get('rouge2_r', 0):.2f}/"
                            f"{rouge.get('rouge2_f', 0):.2f}"
                        )
                    else:
                        rouge1_str = "N/A"
                        rouge2_str = "N/A"

                    if "error" not in bleu:
                        bleu_str = f"{bleu.get('bleu_overall', 0):.4f}"
                    else:
                        bleu_str = "N/A"

                    print(
                        f"{idx:<3} | {model.replace('_',' ').title()[:16]:<16} | "
                        f"{metrics.get('generated_summary_length', 0):>6} | "
                        f"{metrics.get('compression_ratio', 0):>9.2f}% | "
                        f"{metrics.get('density', 0):>7.2f}% | "
                        f"{metrics.get('text_similarity', 0):>8.2f} | "
                        f"{rouge1_str:>20} | {rouge2_str:>20} | {bleu_str:>8}"
                    )

                print("-" * len(header) + "\n")
            else:
                header = (
                    f"{'#':<3} | {'Model':<20} | {'Words':>6} | "
                    f"{'Compress':>10} | {'Density':>8} | {'Cosine':>8}"
                )
                print("-" * len(header))
                print(header)
                print("-" * len(header))

                for idx, (model, metrics) in enumerate(
                    evaluation_results["abstractive_evaluations"].items(), 1
                ):
                    print(
                        f"{idx:<3} | {model.replace('_',' ').title()[:20]:<20} | "
                        f"{metrics.get('generated_summary_length', 0):>6} | "
                        f"{metrics.get('compression_ratio', 0):>9.2f}% | "
                        f"{metrics.get('density', 0):>7.2f}% | "
                        f"{metrics.get('text_similarity', 0):>8.2f}"
                    )

                print("-" * len(header) + "\n")

        print("\n" + "=" * 80 + "\n")

    def cleanup(self):
        """Clean up resources"""
        self.abstractive.cleanup()
