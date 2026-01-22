"""
AI Service
Handles interactions with Google Gemini for analysis and style transfer.
"""

from typing import Optional
from src.utils.logger import setup_logger
import pandas as pd
import json
from pathlib import Path

# Try importing google-genai
try:
    from google import genai
    from google.genai import types

    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

logger = setup_logger("AIService")


class AIService:
    def __init__(self, config: dict):
        self.config = config.get("gemini", {})
        self.enabled = self.config.get("enabled", False)
        self.api_key = self.config.get("api_key")
        self.client = None

        if self.enabled and self.api_key and HAS_GENAI:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to init Gemini client: {e}")

    def analyze_performance(self, excel_path: str) -> str:
        """Analyze the summarization report using Gemini with a Consultant Persona."""
        if not self.client:
            return "AI Analysis Unavailable"

        try:
            # Load Data
            df = pd.read_excel(excel_path, sheet_name="All Results")
            if "Summary" in df.columns:
                df = df.drop(columns=["Summary"])

            # Pre-calculate Champions for Context
            fastest = df.loc[df["Time (s)"].idxmin()]
            most_accurate = df.loc[df["Cosine Sim"].idxmax()]

            # Identify high density (ignoring excessively high density that might be just keywords)
            dense_df = df[df["Density %"] < 90]  # Filter potential outliers
            most_dense = (
                dense_df.loc[dense_df["Density %"].idxmax()]
                if not dense_df.empty
                else df.loc[df["Density %"].idxmax()]
            )

            # Best ROUGE score (if available)
            best_rouge = None
            if "ROUGE-1 F1" in df.columns:
                best_rouge = df.loc[df["ROUGE-1 F1"].idxmax()]

            data_str = df.to_json(orient="records", lines=True)

            rouge_context = (
                f"- Best Content Preservation (ROUGE-1): {best_rouge['Method']} ({best_rouge['ROUGE-1 F1']:.2f}%)"
                if best_rouge is not None
                else ""
            )

            prompt = f"""
            You are a Senior NLP Architect advising a CTO. 
            
            CONTEXT:
            - User needs to pick a summarization model for their production pipeline.
            - "Extractive" models (e.g., TF-IDF) select sentences (Fast, Factual, Rigid).
            - "Abstractive" models (e.g., BART, T5) generate new text (Slower, Fluent, Risk of Hallucination).
            
            PERFORMANCE DATA:
            {data_str}
            
            QUICK STATS:
            - Fastest: {fastest['Method']} ({fastest['Time (s)']:.4f}s)
            - Most Faithful (Cosine): {most_accurate['Method']}
            - Most Dense: {most_dense['Method']}
            {rouge_context}

            KEY METRICS EXPLAINED:
            - **ROUGE-1 F1**: Measures how much original content (unigrams) is preserved. Higher = more complete.
            - **BLEU**: Measures n-gram overlap. Higher = better quality match.
            - **Cosine Similarity**: Semantic similarity between summary and original.
            - **Compression %**: Lower = more concise summary.
            - **Density %**: Higher = richer vocabulary, less repetition.

            Develop a Strategic Analysis in exactly this format:

            # Executive Summary
            [1-sentence bottom line. E.g., "For high-volume processing, strictly use **TF-IDF**. For customer-facing summaries, upgrade to **BART**."]

            # Champion Models
            ### 1. Best for **Efficiency (Cost/Speed)**
            - **Model**: [Name]
            - **Why**: [Explanation. e.g., "Instant latency, zero GPU cost."]
            - **Use Case**: [e.g., "Internal indexing, Search preview"]

            ### 2. Best for **Quality (Content Preservation)**
            - **Model**: [Highest ROUGE/BLEU score if available, otherwise Cosine Sim]
            - **Why**: [Explanation referencing ROUGE/BLEU scores. e.g., "ROUGE-1: 85% - captures most key information"]
            - **Use Case**: [e.g., "Legal summaries, Technical documentation where accuracy is critical"]

            ### 3. Best for **Readability (Human-Centric)**
            - **Model**: [Best Abstractive Model usually, or high-scoring Extractive]
            - **Why**: [Explanation. e.g., "Generates coherent narrative."]
            - **Use Case**: [e.g., "Newsletters, Executive Briefs"]

            # Risk Assessment
            - **Content Loss**: [Flag models with ROUGE-1 < 60% or low BLEU scores - significant information missing]
            - **Hallucinations**: [Check Abstractive models with < 70% cosine sim. Warn if high.]
            - **Latency Bottlenecks**: [Flag anything > 5s unless quality is amazing.]
            - **Repetition Issues**: [Flag models with Density < 50% - too redundant]

            # Optimization Strategy
            [Specific advice. e.g., "Switch T5 to ONNX runtime" or "Use TF-IDF to filter sentences before sending to BART." Reference specific metric weaknesses.]
            """

            response = self.client.models.generate_content(
                model=self.config.get("model", "gemini-2.5-flash"),
                contents=[prompt],
                config=types.GenerateContentConfig(temperature=0.2),
            )
            return response.text.strip()

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return f"Error during analysis: {e}"

    def style_transfer(self, text: str, style: str) -> str:
        """Rewrite the summary in the requested style."""
        if not self.client or not text:
            return ""

        try:
            prompt = f"""
            Rewrite this summary in a "{style}" tone/style.
            
            Original:
            {text}
            
            Stylized:
            """

            response = self.client.models.generate_content(
                model=self.config.get("model", "gemini-2.5-flash"),
                contents=[prompt],
                config=types.GenerateContentConfig(temperature=0.7),
            )
            return response.text.strip()

        except Exception as e:
            logger.error(f"Style transfer failed: {e}")
            return f"Style transfer error: {e}"
