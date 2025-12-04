# Summarization Accelerator

A text summarization tool that runs multiple extractive and abstractive summarizers, evaluates them with various metrics, and exports results to Excel.

## Features

- 5 Extractive Methods:
  - TF-IDF based summarization
  - Custom TextRank implementation
  - Sumy TextRank
  - Sumy LexRank
  - Sumy LSA
  
- 3 Abstractive Models:
  - BART (Facebook)
  - T5 (Google)
  - PEGASUS (Google)

- Comprehensive Evaluation Metrics:
  - ROUGE (ROUGE-1, ROUGE-2, ROUGE-L)
  - BLEU (BLEU-1 to BLEU-4)
  - METEOR
  - Cosine Similarity
  - Compression Ratio
  - Information Density

- Excel Export with all summaries, metrics, and execution times
- Tabular output for easy comparison
- GPU support (optional)

## Requirements

- Python 3.8+
- PyTorch
- Transformers library
- pandas, openpyxl
- See requirements.txt for complete list

## Installation

1. Create a virtual environment (recommended):

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Download required NLTK data (first run only):

```python
python -c "import nltk; nltk.download('punkt_tab')"
```

## Quick Start

### Run the Excel Export Demo (RECOMMENDED)

This is the main file to run - it generates a comprehensive Excel report:

```bash
python excel_demo.py
```

This will:
- Run all 5 extractive summarizers
- Run all 3 abstractive models (BART, T5, PEGASUS)
- Calculate all evaluation metrics (ROUGE, BLEU, METEOR, etc.)
- Generate an Excel file: full_summarization_report.xlsx

The Excel file contains:
- Sheet 1: Extractive Summaries with all metrics
- Sheet 2: Abstractive Summaries with all metrics
- Sheet 3: Combined comparison table
- Sheet 4: Metadata and execution statistics

### Input Data

To test with your own text:

1. Edit the text in excel_demo.py (around line 20-45), OR
2. Create a text file and use the CLI tool (see below)

Sample text is already provided in sample_text.txt for reference.

## Usage Examples

### Option 1: Excel Export (Best for Analysis)

```bash
python excel_demo.py
```

Output: full_summarization_report.xlsx with all results and metrics

### Option 2: Interactive Demo

```bash
python demo.py
```

Features:
- Choose from sample texts or enter your own
- Select GPU/CPU processing
- View formatted tabular output
- Save results to JSON

### Option 3: Command-Line Interface

```bash
# Summarize from file
python cli.py -f your_text_file.txt

# Extractive only (fast)
python cli.py -f your_text_file.txt --no-abstractive

# Abstractive only
python cli.py -f your_text_file.txt --no-extractive

# Custom parameters
python cli.py -f your_text_file.txt -s 3 --max-length 150

# Save results
python cli.py -f your_text_file.txt -o results.json
```

```

### Option 4: Python API

Use in your own Python code:

```python
from summarization_accelerator import SummarizationAccelerator

# Initialize
accelerator = SummarizationAccelerator(use_gpu=False)

# Your text
text = """
Your long text goes here...
"""

# Run summarization
results = accelerator.summarize(
    text=text,
    extractive=True,
    abstractive=True,
    extractive_sentence_count=3,
    abstractive_max_length=150,
    abstractive_min_length=50
)

# Display results
accelerator.print_results(results)

# Evaluate with metrics
evaluation = accelerator.evaluate_results(results)
accelerator.print_evaluation_report(evaluation)

# Export to Excel
accelerator.save_to_excel(results, evaluation, 'output.xlsx')

# Save to JSON
accelerator.save_results(results, 'results.json')

# Clean up
accelerator.cleanup()
```

## Configuration

Edit config.py to customize:
- Which models to use (BART, T5, PEGASUS)
- Which extractive algorithms to run
- Default sentence counts
- Max/min lengths for abstractive summaries
- GPU settings

## Output Files

1. Excel Export: full_summarization_report.xlsx
   - Contains all summaries with metrics in separate sheets
   - Easy to sort, filter, and analyze

2. JSON Export: results.json (optional)
   - Complete structured output
   - All metadata and execution times

## Where to Put Your Test Data

Two options:

1. Edit excel_demo.py directly (line 20-45):
   Replace the sample text with your own text

2. Create a text file:
   - Save your text as any_name.txt
   - Run: python cli.py -f any_name.txt

Sample text is provided in sample_text.txt for reference.

## Performance Notes

Extractive summarizers: Very fast (0.01-0.15 seconds)
Abstractive models: Slower (2-120 seconds on first run, faster after)
- BART: ~5 seconds
- T5: ~3 seconds  
- PEGASUS: ~10 seconds

First run downloads models (~4GB total), subsequent runs are much faster.

## Project Structure

```
ACC_SUM/
├── summarization_accelerator.py    # Main engine
├── extractive_summarizers.py       # 5 extractive methods
├── abstractive_summarizers.py      # 3 AI models
├── evaluation_metrics.py            # Scoring system
├── excel_demo.py                    # MAIN FILE TO RUN
├── cli.py                           # Command-line tool
├── config.py                        # Settings
├── requirements.txt                 # Dependencies
├── sample_text.txt                  # Example input
└── full_summarization_report.xlsx   # Output
```
