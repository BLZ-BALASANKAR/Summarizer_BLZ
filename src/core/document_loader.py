"""
Document Loader
Handles conversion of PDF, DOCX, and output to text.
"""
import os
import sys
from pathlib import Path
import traceback
from typing import Optional
from src.utils.logger import setup_logger

logger = setup_logger("DocumentLoader")

class DocumentLoader:
    def __init__(self):
        self.check_dependencies()

    def check_dependencies(self):
        missing = []
        try: import PyPDF2
        except ImportError: missing.append("PyPDF2")
        
        try: import docx2txt
        except ImportError: missing.append("docx2txt")
        
        if missing:
            logger.warning(f"Missing libraries: {', '.join(missing)}")

    def load_document(self, input_path: str, output_path: str = "converted.txt") -> str:
        """
        Convert document to text and save to output_path.
        Returns the absolute path to the saved text file.
        """
        input_file = Path(input_path)
        output_file = Path(output_path).resolve()
        
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        logger.info(f"Processing: {input_file.name}")
        
        text = ""
        ext = input_file.suffix.lower()
        
        try:
            if ext == '.pdf':
                text = self._extract_pdf(input_file)
            elif ext == '.docx':
                text = self._extract_docx(input_file)
            elif ext == '.doc':
                text = self._extract_doc(input_file)
            elif ext == '.txt':
                with open(input_file, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                raise ValueError(f"Unsupported file extension: {ext}")
            
            # Save to text file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
                
            logger.info(f"Saved text to: {output_file} ({len(text)} chars)")
            return str(output_file)

        except Exception as e:
            logger.error(f"Failed to process document: {e}")
            raise

    def _extract_pdf(self, path: Path) -> str:
        import PyPDF2
        text = ""
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages):
                content = page.extract_text() or ""
                text += f"\n--- Page {i+1} ---\n{content}\n"
        return text.strip()

    def _extract_docx(self, path: Path) -> str:
        import docx2txt
        return docx2txt.process(path).strip()

    def _extract_doc(self, path: Path) -> str:
        # Requires antiword
        import subprocess
        try:
            res = subprocess.run(['antiword', str(path)], capture_output=True, text=True, check=True)
            return res.stdout.strip()
        except FileNotFoundError:
            raise RuntimeError("antiword not installed for .doc files")
