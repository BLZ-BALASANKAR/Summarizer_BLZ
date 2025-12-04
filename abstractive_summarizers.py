# """
# Abstractive Summarizers Module
# Implements various transformer-based abstractive summarization models
# """

# from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
# import torch
# from typing import Dict, Optional
# import time
# import warnings
# warnings.filterwarnings('ignore')


# class AbstractiveSummarizers:
#     """
#     Class containing multiple abstractive summarization models
#     """
    
#     def __init__(self, use_gpu: bool = True):
#         """
#         Initialize abstractive summarizers
        
#         Args:
#             use_gpu: Whether to use GPU for inference
#         """
#         self.device = 0 if use_gpu and torch.cuda.is_available() else -1
#         self.models = {}
        
#     def _load_model(self, model_name: str, model_path: str):
#         """
#         Lazy load a summarization model
        
#         Args:
#             model_name: Name identifier for the model
#             model_path: HuggingFace model path
#         """
#         if model_name not in self.models:
#             print(f"Loading {model_name} model...")
#             self.models[model_name] = pipeline(
#                 "summarization",
#                 model=model_path,
#                 device=self.device
#             )
    
#     def bart_summarize(self, text: str, max_length: int = 150, 
#                        min_length: int = 50) -> Dict:
#         """
#         BART model for abstractive summarization
        
#         Args:
#             text: Input text to summarize
#             max_length: Maximum length of summary
#             min_length: Minimum length of summary
            
#         Returns:
#             Dictionary with summary and metadata
#         """
#         start_time = time.time()
        
#         model_path = 'facebook/bart-large-cnn'
#         self._load_model('bart', model_path)
        
#         summary = self.models['bart'](
#             text,
#             max_length=max_length,
#             min_length=min_length,
#             do_sample=False
#         )[0]['summary_text']
        
#         return {
#             'model': 'BART',
#             'type': 'abstractive',
#             'summary': summary,
#             'max_length': max_length,
#             'min_length': min_length,
#             'execution_time': time.time() - start_time
#         }
    
#     def t5_summarize(self, text: str, max_length: int = 150, 
#                      min_length: int = 50) -> Dict:
#         """
#         T5 model for abstractive summarization
        
#         Args:
#             text: Input text to summarize
#             max_length: Maximum length of summary
#             min_length: Minimum length of summary
            
#         Returns:
#             Dictionary with summary and metadata
#         """
#         start_time = time.time()
        
#         model_path = 't5-small'
#         self._load_model('t5', model_path)
        
#         # T5 requires a prefix
#         prefixed_text = f"summarize: {text}"
        
#         summary = self.models['t5'](
#             prefixed_text,
#             max_length=max_length,
#             min_length=min_length,
#             do_sample=False
#         )[0]['summary_text']
        
#         return {
#             'model': 'T5',
#             'type': 'abstractive',
#             'summary': summary,
#             'max_length': max_length,
#             'min_length': min_length,
#             'execution_time': time.time() - start_time
#         }
    
#     def pegasus_summarize(self, text: str, max_length: int = 150, 
#                           min_length: int = 50) -> Dict:
#         """
#         PEGASUS model for abstractive summarization
        
#         Args:
#             text: Input text to summarize
#             max_length: Maximum length of summary
#             min_length: Minimum length of summary
            
#         Returns:
#             Dictionary with summary and metadata
#         """
#         start_time = time.time()
        
#         model_path = 'google/pegasus-xsum'
#         self._load_model('pegasus', model_path)
        
#         summary = self.models['pegasus'](
#             text,
#             max_length=max_length,
#             min_length=min_length,
#             do_sample=False
#         )[0]['summary_text']
        
#         return {
#             'model': 'PEGASUS',
#             'type': 'abstractive',
#             'summary': summary,
#             'max_length': max_length,
#             'min_length': min_length,
#             'execution_time': time.time() - start_time
#         }
    
#     def summarize_all(self, text: str, max_length: int = 150, 
#                       min_length: int = 50) -> Dict[str, Dict]:
#         """
#         Run all abstractive summarization models
        
#         Args:
#             text: Input text to summarize
#             max_length: Maximum length of summary
#             min_length: Minimum length of summary
            
#         Returns:
#             Dictionary with results from all models
#         """
#         return {
#             'bart': self.bart_summarize(text, max_length, min_length),
#             't5': self.t5_summarize(text, max_length, min_length),
#             'pegasus': self.pegasus_summarize(text, max_length, min_length)
#         }
    
#     def cleanup(self):
#         """Clean up models to free memory"""
#         self.models.clear()
#         if torch.cuda.is_available():
#             torch.cuda.empty_cache()






"""
Abstractive Summarizers Module
Implements various transformer-based abstractive summarization models
"""

from transformers import pipeline, AutoTokenizer
import torch
from typing import Dict, Optional
import time
import warnings
warnings.filterwarnings('ignore')


class AbstractiveSummarizers:
    """
    Class containing multiple abstractive summarization models
    """

    def __init__(self, use_gpu: bool = True):
        """
        Initialize abstractive summarizers

        Args:
            use_gpu: Whether to use GPU for inference
        """
        self.device = 0 if use_gpu and torch.cuda.is_available() else -1
        self.models = {}   # name -> pipeline
        self.tokenizers = {}  # name -> tokenizer (for LED chunking)
        self.use_gpu = use_gpu and torch.cuda.is_available()

    def _load_model(self, model_name: str, model_path: str):
        """
        Lazy load a summarization model as a transformers pipeline.

        Args:
            model_name: Name identifier for the model
            model_path: HuggingFace model path
        """
        if model_name not in self.models:
            print(f"Loading {model_name} model from '{model_path}' (device={self.device}) ...")
            # create pipeline
            self.models[model_name] = pipeline(
                "summarization",
                model=model_path,
                device=self.device
            )
            # attempt to load tokenizer if we need it later (LED)
            try:
                tok = AutoTokenizer.from_pretrained(model_path, use_fast=True)
                self.tokenizers[model_name] = tok
            except Exception:
                # some pipelines may still work without a local tokenizer object
                self.tokenizers[model_name] = None

    def _summarize_with_pipeline(self, model_key: str, text: str, max_length: int, min_length: int):
        """
        Helper to call a loaded pipeline and return the summary string.
        """
        pipe = self.models.get(model_key)
        if pipe is None:
            raise RuntimeError(f"Model '{model_key}' not loaded")
        # Note: pipeline returns a list of generated dicts
        out = pipe(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
            truncation=True
        )
        return out[0]['summary_text']

    def bart_summarize(self, text: str, max_length: int = 150,
                       min_length: int = 50) -> Dict:
        start_time = time.time()
        model_path = 'facebook/bart-large-cnn'
        self._load_model('bart', model_path)

        summary = self._summarize_with_pipeline('bart', text, max_length, min_length)

        return {
            'model': 'BART',
            'type': 'abstractive',
            'summary': summary,
            'max_length': max_length,
            'min_length': min_length,
            'execution_time': time.time() - start_time
        }

    def t5_summarize(self, text: str, max_length: int = 150,
                     min_length: int = 50) -> Dict:
        start_time = time.time()
        model_path = 't5-small'
        self._load_model('t5', model_path)

        # T5 requires a prefix
        prefixed_text = f"summarize: {text}"
        summary = self._summarize_with_pipeline('t5', prefixed_text, max_length, min_length)

        return {
            'model': 'T5',
            'type': 'abstractive',
            'summary': summary,
            'max_length': max_length,
            'min_length': min_length,
            'execution_time': time.time() - start_time
        }

    def pegasus_summarize(self, text: str, max_length: int = 150,
                          min_length: int = 50) -> Dict:
        start_time = time.time()
        model_path = 'google/pegasus-xsum'
        self._load_model('pegasus', model_path)

        summary = self._summarize_with_pipeline('pegasus', text, max_length, min_length)

        return {
            'model': 'PEGASUS-XSUM',
            'type': 'abstractive',
            'summary': summary,
            'max_length': max_length,
            'min_length': min_length,
            'execution_time': time.time() - start_time
        }

    # ----- NEW: FLAN-T5 (base / large) -----
    def flan_t5_summarize(self, text: str, max_length: int = 150,
                          min_length: int = 50, variant: str = "base") -> Dict:
        """
        FLAN-T5 summarization. variant: 'base' or 'large'
        """
        start_time = time.time()
        if variant == "large":
            model_path = "google/flan-t5-large"
            model_key = "flan_t5_large"
        else:
            model_path = "google/flan-t5-base"
            model_key = "flan_t5_base"

        self._load_model(model_key, model_path)
        prefixed_text = f"summarize: {text}"  # FLAN-T5 works well with prompt
        summary = self._summarize_with_pipeline(model_key, prefixed_text, max_length, min_length)

        return {
            'model': f'FLAN-T5-{variant}',
            'type': 'abstractive',
            'summary': summary,
            'max_length': max_length,
            'min_length': min_length,
            'execution_time': time.time() - start_time
        }

    # ----- NEW: PEGASUS-LARGE & BigBird-Pegasus -----
    def pegasus_large_summarize(self, text: str, max_length: int = 150,
                                min_length: int = 50) -> Dict:
        """
        PEGASUS-large summarization (higher capacity than xsum)
        """
        start_time = time.time()
        model_path = "google/pegasus-large"
        model_key = "pegasus_large"
        # Some environments may not have pegasus-large; fallback to xsum if loading fails
        try:
            self._load_model(model_key, model_path)
        except Exception:
            # fallback
            model_path = "google/pegasus-xsum"
            model_key = "pegasus"
            self._load_model(model_key, model_path)

        summary = self._summarize_with_pipeline(model_key, text, max_length, min_length)

        return {
            'model': 'PEGASUS-LARGE',
            'type': 'abstractive',
            'summary': summary,
            'max_length': max_length,
            'min_length': min_length,
            'execution_time': time.time() - start_time
        }

    def bigbird_pegasus_summarize(self, text: str, max_length: int = 150,
                                   min_length: int = 50) -> Dict:
        """
        BigBird-Pegasus variant for long-document summarization (e.g. arXiv papers).
        Model: google/bigbird-pegasus-large-arxiv
        """
        start_time = time.time()
        model_path = "google/bigbird-pegasus-large-arxiv"
        model_key = "bigbird_pegasus"
        self._load_model(model_key, model_path)

        # This model can handle longer inputs but you may still want to chunk very long text.
        summary = self._summarize_with_pipeline(model_key, text, max_length, min_length)

        return {
            'model': 'BigBird-Pegasus',
            'type': 'abstractive',
            'summary': summary,
            'max_length': max_length,
            'min_length': min_length,
            'execution_time': time.time() - start_time
        }

    # ----- NEW: LED (Longformer Encoder-Decoder) with basic chunking -----
    def led_summarize(self, text: str, max_length: int = 256, min_length: int = 50,
                      chunk_summary_once: bool = True) -> Dict:
        """
        LED (Longformer Encoder-Decoder) summarizer. This method will:
         - load the LED pipeline (allenai/led-base-16384)
         - chunk the document into tokenizer.model_max_length pieces (approx),
           summarize each chunk, then optionally summarize concatenated chunk-summaries.

        chunk_summary_once: if True, after summarizing each chunk, run one final summarization
                             over the concatenated chunk summaries (helps compress).
        """
        start_time = time.time()
        model_path = "allenai/led-base-16384"
        model_key = "led"
        self._load_model(model_key, model_path)

        # get tokenizer to know model_max_length
        tokenizer = self.tokenizers.get(model_key)
        if tokenizer is None:
            try:
                tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)
                self.tokenizers[model_key] = tokenizer
            except Exception:
                tokenizer = None

        # Determine chunk size (in characters fallback)
        if tokenizer and hasattr(tokenizer, "model_max_length"):
            max_tokens = getattr(tokenizer, "model_max_length", 4096)
            # leave room for generation
            chunk_token_size = max_tokens - 512 if max_tokens > 1024 else max_tokens // 2
        else:
            # fallback to characters approx for safety
            chunk_token_size = 4000

        # Simple chunking by characters while trying to be sentence-aware
        chunks = []
        if len(text) <= chunk_token_size:
            chunks = [text]
        else:
            # naive sentence split
            sentences = text.split('. ')
            current = ""
            for sent in sentences:
                # add a period back (we split it out earlier)
                candidate = (sent + '. ') if not sent.endswith('.') else (sent + ' ')
                if len(current) + len(candidate) <= chunk_token_size:
                    current += candidate
                else:
                    if current.strip():
                        chunks.append(current.strip())
                    current = candidate
            if current.strip():
                chunks.append(current.strip())

        chunk_summaries = []
        for idx, chunk in enumerate(chunks):
            # summarizer may still truncate if chunk is too long; set truncation=True in pipeline
            try:
                summary_chunk = self._summarize_with_pipeline(model_key, chunk, max_length, min_length)
            except Exception:
                # fallback: attempt summarization with truncation flag via direct pipeline call
                summary_chunk = self.models[model_key](
                    chunk,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False,
                    truncation=True
                )[0]['summary_text']
            chunk_summaries.append(summary_chunk)

        # Combine chunk summaries and optionally compress once more
        combined = " ".join(chunk_summaries).strip()

        if chunk_summary_once and len(combined) > 20:
            # run final summarization to condense
            try:    
                final_summary = self._summarize_with_pipeline(model_key, combined, max_length, min_length)
            except Exception:
                final_summary = combined
        else:
            final_summary = combined

        return {
            'model': 'LED',
            'type': 'abstractive',
            'summary': final_summary,
            'chunks': len(chunks),
            'execution_time': time.time() - start_time
        }

    def summarize_all(self, text: str, max_length: int = 150,
                      min_length: int = 50) -> Dict[str, Dict]:
        """
        Run all abstractive summarization models
        """
        results = {}
        # baseline models
        results['bart'] = self.bart_summarize(text, max_length, min_length)
        results['t5'] = self.t5_summarize(text, max_length, min_length)
        results['pegasus'] = self.pegasus_summarize(text, max_length, min_length)

        # new high-quality models (load on demand)
        try:
            results['flan_t5_base'] = self.flan_t5_summarize(text, max_length, min_length, variant="base")
        except Exception as e:
            results['flan_t5_base'] = {'error': str(e)}

        try:
            results['flan_t5_large'] = self.flan_t5_summarize(text, max_length, min_length, variant="large")
        except Exception as e:
            results['flan_t5_large'] = {'error': str(e)}

        try:
            results['pegasus_large'] = self.pegasus_large_summarize(text, max_length, min_length)
        except Exception as e:
            results['pegasus_large'] = {'error': str(e)}

        try:
            results['bigbird_pegasus'] = self.bigbird_pegasus_summarize(text, max_length, min_length)
        except Exception as e:
            results['bigbird_pegasus'] = {'error': str(e)}

        try:
            results['led'] = self.led_summarize(text, max_length=max_length, min_length=min_length)
        except Exception as e:
            results['led'] = {'error': str(e)}

        return results

    def cleanup(self):
        """Clean up models to free memory"""
        try:
            self.models.clear()
            self.tokenizers.clear()
            if torch.cuda.is_available() and self.use_gpu:
                try:
                    torch.cuda.empty_cache()
                except Exception:
                    pass
        except Exception:
            pass
