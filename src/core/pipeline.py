"""
Pipeline Orchestrator
Connects DocumentLoader, SummarizerEngine, and AIService.
"""

from typing import Generator, Tuple
from src.core.document_loader import DocumentLoader
from src.core.summarizer import SummarizerEngine
from src.core.ai_service import AIService
from src.utils.logger import setup_logger
from pathlib import Path
import json

logger = setup_logger("Pipeline")


class SummarizationPipeline:
    def __init__(self, config: dict):
        self.config = config
        self.loader = DocumentLoader()
        self.engine = SummarizerEngine(config)
        self.ai = AIService(config)

    def run(self) -> Generator[Tuple[str, float], None, dict]:
        """
        Execute the pipeline, yielding progress updates.
        Yields: (status_message, progress_float 0.0-1.0)
        Returns: Final results dictionary
        """
        try:
            # 1. Load Document
            input_path = self.config["paths"]["input_path"]
            yield "Loading Document...", 0.1

            # The loader saves to a temp file, but we read it back into memory
            # to pass to the engine. Ideally, we'd skip the file save if not needed,
            # but legacy compatibility suggests keeping 'converted.txt'.
            txt_path = self.loader.load_document(
                input_path, self.config["paths"].get("output_text", "converted.txt")
            )
            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read()

            if not text:
                raise ValueError("Extracted text is empty.")

            # 2. Summarize & Evaluate
            yield "Running Summarization Models (This may take a while)...", 0.3
            results = self.engine.run(text)
            yield "Summarization Complete. Generating Report...", 0.8

            # 3. Export Report
            # Save Excel
            excel_name = self.config["output"].get(
                "excel_filename", "full_summarization_report.xlsx"
            )
            self.engine.save_report(results, excel_name)

            # Save JSON for frontend
            with open("results.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            # 4. AI Analysis & Style Transfer
            if self.ai.enabled:
                yield "Running AI Analysis...", 0.9

                # Analysis
                analysis = self.ai.analyze_performance(excel_name)
                with open("inference.txt", "w", encoding="utf-8") as f:
                    f.write(analysis)

                # Style Transfer - Generate multiple versions
                # Pick best summary (simplified logic: pick first abstractive or first extractive)
                best_sum = ""
                if results["abstractive_summaries"]:
                    best_sum = list(results["abstractive_summaries"].values())[0][
                        "summary"
                    ]
                elif results["extractive_summaries"]:
                    best_sum = list(results["extractive_summaries"].values())[0][
                        "summary"
                    ]

                if best_sum:
                    # Generate summaries in multiple styles
                    styles_to_generate = [
                        "Formal",
                        "Casual",
                        "Bullet Points",
                        "Executive Summary",
                        "ELI5",
                    ]
                    stylized_versions = {}

                    for style_name in styles_to_generate:
                        try:
                            stylized = self.ai.style_transfer(best_sum, style_name)
                            stylized_versions[style_name] = stylized
                        except Exception as e:
                            logger.warning(f"Style {style_name} failed: {e}")
                            stylized_versions[style_name] = (
                                f"Error generating {style_name} version"
                            )

                    # Save all stylized versions as JSON
                    with open("stylized_summaries.json", "w", encoding="utf-8") as f:
                        json.dump(stylized_versions, f, ensure_ascii=False, indent=2)

                    # Also save user's selected style as primary for backward compatibility
                    user_style = self.config.get("gemini", {}).get("style", "Formal")
                    primary_summary = stylized_versions.get(
                        user_style, list(stylized_versions.values())[0]
                    )
                    with open("stylized_summary.txt", "w", encoding="utf-8") as f:
                        f.write(primary_summary)

            yield "Pipeline Complete!", 1.0
            return results

        except Exception as e:
            logger.critical(f"Pipeline crashed: {e}")
            raise
