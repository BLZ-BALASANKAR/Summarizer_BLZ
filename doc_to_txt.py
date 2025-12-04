# """
# doc_to_txt.py

# PDF/DOC/DOCX to Text Converter (Config-driven)
# Reads the input file path from config.yaml (paths.input_path)
# and writes the extracted text to paths.output_text (e.g. converted.txt).
# """

# import os
# import sys
# from pathlib import Path
# import yaml

# # Check for required libraries
# MISSING_LIBS = []

# try:
#     import PyPDF2
# except ImportError:
#     MISSING_LIBS.append("PyPDF2")

# try:
#     import docx2txt
# except ImportError:
#     MISSING_LIBS.append("docx2txt")

# if MISSING_LIBS:
#     print("Missing required libraries. Please install them using:")
#     print(f"pip install {' '.join(MISSING_LIBS)}")
#     sys.exit(1)


# def load_config():
#     """Load configuration from config.yaml"""
#     cfg_path = Path("config.yaml")
#     if not cfg_path.exists():
#         print(" Error: config.yaml not found in current directory.")
#         sys.exit(1)

#     try:
#         with open(cfg_path, "r", encoding="utf-8") as f:
#             return yaml.safe_load(f)
#     except Exception as e:
#         print(f"Error reading config.yaml: {e}")
#         sys.exit(1)


# def extract_text_from_pdf(file_path):
#     """Extract text from PDF file using PyPDF2"""
#     text = ""
#     try:
#         with open(file_path, 'rb') as file:
#             pdf_reader = PyPDF2.PdfReader(file)
#             num_pages = len(pdf_reader.pages)

#             print(f"  → Processing PDF: {num_pages} pages found")

#             for page_num in range(num_pages):
#                 page = pdf_reader.pages[page_num]
#                 page_text = page.extract_text()
#                 text += f"\n{'='*60}\n[Page {page_num + 1}]\n{'='*60}\n\n"
#                 text += (page_text or "") + "\n"

#         return text.strip()
#     except Exception as e:
#         raise Exception(f"Error extracting PDF: {str(e)}")


# def extract_text_from_docx(file_path):
#     """Extract text from DOCX file using docx2txt"""
#     try:
#         text = docx2txt.process(file_path)
#         return text.strip()
#     except Exception as e:
#         error_msg = str(e).lower()
#         if 'zip' in error_msg or 'corrupt' in error_msg:
#             raise Exception(
#                 "File appears to be corrupted or is an old .doc file with .docx extension. "
#                 "Try opening and re-saving it in Word, or rename to .doc"
#             )
#         raise Exception(f"Error extracting DOCX: {str(e)}")


# def extract_text_from_doc(file_path):
#     """
#     Extract text from old DOC file
#     Note: This requires antiword to be installed on your system
#     """
#     try:
#         import subprocess

#         result = subprocess.run(
#             ['antiword', file_path],
#             capture_output=True,
#             text=True,
#             check=True
#         )
#         return result.stdout.strip()
#     except FileNotFoundError:
#         raise Exception(
#             "Old .doc file support requires 'antiword' to be installed.\n"
#             "Skipping .doc file..."
#         )
#     except Exception as e:
#         raise Exception(f"Error extracting DOC: {str(e)}")


# def normalize_file_path(file_path: str) -> str:
#     """
#     Convert file URLs and normalize paths

#     Args:
#         file_path: File path or file:/// URL

#     Returns:
#         Normalized file path
#     """
#     from urllib.parse import unquote, urlparse

#     file_path = file_path.strip('"').strip("'")

#     if file_path.startswith('file:///'):
#         parsed = urlparse(file_path)
#         file_path = unquote(parsed.path)
#         if os.name == 'nt' and file_path.startswith('/') and len(file_path) > 2 and file_path[2] == ':':
#             file_path = file_path[1:]

#     file_path = unquote(file_path)
#     return file_path


# def convert_file_to_txt(file_path: Path, output_path: Path) -> str:
#     """
#     Convert a single file to TXT.

#     Args:
#         file_path: Path to input file
#         output_path: Full path to output text file

#     Returns:
#         Path to output file or raises on failure
#     """
#     file_ext = file_path.suffix.lower()
#     print(f"\n Processing: {file_path.name}")

#     try:
#         if file_ext == '.pdf':
#             text = extract_text_from_pdf(str(file_path))
#         elif file_ext == '.docx':
#             text = extract_text_from_docx(str(file_path))
#         elif file_ext == '.doc':
#             text = extract_text_from_doc(str(file_path))
#         else:
#             raise Exception(f"Unsupported file extension: {file_ext}")

#         # Ensure parent directory exists
#         output_path.parent.mkdir(parents=True, exist_ok=True)

#         with open(output_path, 'w', encoding='utf-8') as f:
#             f.write(text)

#         print(f"  ✓ Saved: {output_path}")
#         print(f"  ✓ Characters: {len(text):,}")

#         return str(output_path)

#     except Exception as e:
#         print(f"  ✗ Error: {str(e)}")
#         raise


# def main():
#     """Main entry point – uses config.yaml to decide input & output paths."""
#     cfg = load_config()

#     # Read paths from config
#     try:
#         input_raw = cfg["paths"]["input_path"]
#         output_name = cfg["paths"].get("output_text", "converted.txt")
#     except KeyError as e:
#         print(f" Missing key in config.yaml: {e}")
#         sys.exit(1)

#     input_norm = normalize_file_path(input_raw)
#     input_path = Path(os.path.expanduser(input_norm))

#     if not input_path.exists():
#         print(f" Input file not found:\n   {input_path}")
#         sys.exit(1)

#     output_path = Path.cwd() / output_name

#     print("============================================================")
#     print(" PDF/DOC/DOCX to Text Converter - Config Mode")
#     print("============================================================")
#     print(f"\nInput file : {input_path}")
#     print(f" Output text: {output_path}")

#     try:
#         convert_file_to_txt(input_path, output_path)
#     except Exception:
#         print("\n Conversion failed.")
#         sys.exit(1)

#     print("\n============================================================")
#     print(" CONVERSION COMPLETE")
#     print("============================================================")


# if __name__ == "__main__":
#     main()



"""
doc_to_txt.py

PDF/DOC/DOCX to Text Converter (Config-driven)
Reads the input file path from config.yaml (paths.input_path)
and writes the extracted text to paths.output_text (e.g. converted.txt).
"""

import os
import sys
from pathlib import Path
import yaml
import traceback  # NEW


# Check for required libraries
MISSING_LIBS = []

try:
    import PyPDF2
except ImportError:
    MISSING_LIBS.append("PyPDF2")

try:
    import docx2txt
except ImportError:
    MISSING_LIBS.append("docx2txt")

if MISSING_LIBS:
    print("Missing required libraries. Please install them using:")
    print(f"pip install {' '.join(MISSING_LIBS)}")
    sys.exit(1)


def load_config():
    """Load configuration from config.yaml"""
    cfg_path = Path("config.yaml")
    if not cfg_path.exists():
        print("Error: config.yaml not found in current directory.")
        sys.exit(1)

    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading config.yaml: {e}")
        sys.exit(1)


def extract_text_from_pdf(file_path):
    """Extract text from PDF file using PyPDF2"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)

            print(f"Processing PDF: {num_pages} pages found")

            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                text += "\n" + "=" * 60 + f"\n[Page {page_num + 1}]\n" + "=" * 60 + "\n\n"
                text += (page_text or "") + "\n"

        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting PDF: {str(e)}")


def extract_text_from_docx(file_path):
    """Extract text from DOCX file using docx2txt"""
    try:
        text = docx2txt.process(file_path)
        return text.strip()
    except Exception as e:
        error_msg = str(e).lower()
        if 'zip' in error_msg or 'corrupt' in error_msg:
            raise Exception(
                "File appears to be corrupted or is an old .doc file with .docx extension. "
                "Try opening and re-saving it in Word, or rename to .doc"
            )
        raise Exception(f"Error extracting DOCX: {str(e)}")


def extract_text_from_doc(file_path):
    """
    Extract text from old DOC file
    Note: This requires antiword to be installed on your system
    """
    try:
        import subprocess

        result = subprocess.run(
            ['antiword', file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except FileNotFoundError:
        raise Exception(
            "Old .doc file support requires 'antiword' to be installed.\n"
            "Skipping .doc file..."
        )
    except Exception as e:
        raise Exception(f"Error extracting DOC: {str(e)}")


def normalize_file_path(file_path: str) -> str:
    """
    Convert file URLs and normalize paths

    Args:
        file_path: File path or file:/// URL

    Returns:
        Normalized file path
    """
    from urllib.parse import unquote, urlparse

    file_path = file_path.strip('"').strip("'")

    if file_path.startswith('file:///'):
        parsed = urlparse(file_path)
        file_path = unquote(parsed.path)
        if os.name == 'nt' and file_path.startswith('/') and len(file_path) > 2 and file_path[2] == ':':
            file_path = file_path[1:]

    file_path = unquote(file_path)
    return file_path


def convert_file_to_txt(file_path: Path, output_path: Path) -> str:
    """
    Convert a single file to TXT.

    Args:
        file_path: Path to input file
        output_path: Full path to output text file

    Returns:
        Path to output file or raises on failure
    """
    file_ext = file_path.suffix.lower()
    print(f"\nProcessing: {file_path.name}")

    try:
        if file_ext == '.pdf':
            text = extract_text_from_pdf(str(file_path))
        elif file_ext == '.docx':
            text = extract_text_from_docx(str(file_path))
        elif file_ext == '.doc':
            text = extract_text_from_doc(str(file_path))
        else:
            raise Exception(f"Unsupported file extension: {file_ext}")

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"Saved text to: {output_path}")
        print(f"Characters written: {len(text):,}")

        return str(output_path)

    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        raise


def main():
    """Main entry point – uses config.yaml to decide input & output paths."""
    cfg = load_config()

    # Read paths from config
    try:
        input_raw = cfg["paths"]["input_path"]
        output_name = cfg["paths"].get("output_text", "converted.txt")
    except KeyError as e:
        print(f"Missing key in config.yaml: {e}")
        sys.exit(1)

    input_norm = normalize_file_path(input_raw)
    input_path = Path(os.path.expanduser(input_norm))

    if not input_path.exists():
        print(f"Input file not found:\n  {input_path}")
        sys.exit(1)

    output_path = Path.cwd() / output_name

    print("============================================================")
    print(" PDF/DOC/DOCX to Text Converter - Config Mode")
    print("============================================================")
    print(f"\nInput file : {input_path}")
    print(f"Output text: {output_path}")

    try:
        convert_file_to_txt(input_path, output_path)
    except Exception:
        print("\nConversion failed.")
        print("Reason:")
        traceback.print_exc()
        sys.exit(1)

    print("\n============================================================")
    print(" CONVERSION COMPLETE")
    print("============================================================")


if __name__ == "__main__":
    main()
