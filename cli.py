"""
Command-Line Interface for Summarization Accelerator
"""

import argparse
from summarization_accelerator import SummarizationAccelerator
import sys


def main():
    parser = argparse.ArgumentParser(
        description='Summarization Accelerator - Run multiple summarizers on text',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Summarize text from a file
  python cli.py -f input.txt
  
  # Summarize with only extractive methods
  python cli.py -f input.txt --no-abstractive
  
  # Summarize with only abstractive methods
  python cli.py -f input.txt --no-extractive
  
  # Custom parameters
  python cli.py -f input.txt -s 5 --max-length 200 --min-length 50
  
  # Save results to file
  python cli.py -f input.txt -o results.json
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-f', '--file', type=str, 
                            help='Path to input text file')
    input_group.add_argument('-t', '--text', type=str,
                            help='Text to summarize (as string)')
    
    # Summarization options
    parser.add_argument('--no-extractive', action='store_true',
                       help='Disable extractive summarizers')
    parser.add_argument('--no-abstractive', action='store_true',
                       help='Disable abstractive summarizers')
    parser.add_argument('-s', '--sentences', type=int, default=3,
                       help='Number of sentences for extractive summaries (default: 3)')
    parser.add_argument('--max-length', type=int, default=150,
                       help='Maximum length for abstractive summaries (default: 150)')
    parser.add_argument('--min-length', type=int, default=50,
                       help='Minimum length for abstractive summaries (default: 50)')
    
    # Output options
    parser.add_argument('-o', '--output', type=str,
                       help='Save results to JSON file')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Minimal output (only show summaries)')
    parser.add_argument('--no-gpu', action='store_true',
                       help='Disable GPU usage')
    
    args = parser.parse_args()
    
    # Read input text
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read().strip()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found")
            sys.exit(1)
    else:
        text = args.text
    
    if not text:
        print("Error: Input text is empty")
        sys.exit(1)
    
    # Initialize accelerator
    if not args.quiet:
        print("Initializing Summarization Accelerator...")
    
    accelerator = SummarizationAccelerator(use_gpu=not args.no_gpu)
    
    # Run summarization
    try:
        results = accelerator.summarize(
            text=text,
            extractive=not args.no_extractive,
            abstractive=not args.no_abstractive,
            extractive_sentence_count=args.sentences,
            abstractive_max_length=args.max_length,
            abstractive_min_length=args.min_length
        )
        
        # Print results
        accelerator.print_results(results, verbose=not args.quiet)
        
        # Save to file if requested
        if args.output:
            accelerator.save_results(results, args.output)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    
    finally:
        accelerator.cleanup()


if __name__ == "__main__":
    main()
