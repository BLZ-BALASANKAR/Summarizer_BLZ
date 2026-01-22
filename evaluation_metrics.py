"""
Evaluation Metrics Module
Provides various metrics to evaluate summarization quality
Includes: ROUGE, BLEU, METEOR, CIDEr, and custom metrics
"""

from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
from nltk.tokenize import sent_tokenize, word_tokenize
from typing import Dict, List, Tuple
import numpy as np
from collections import Counter
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SummarizationEvaluator:
    """
    Class providing multiple evaluation metrics for summarization
    """
    
    def __init__(self):
        """Initialize evaluator"""
        self.smoothing = SmoothingFunction().method4
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        try:
            return word_tokenize(text.lower())
        except:
            return text.lower().split()
    
    def rouge_score(self, reference: str, hypothesis: str) -> Dict[str, float]:
        """
        Calculate ROUGE scores (0-100 scale)
        """
        try:
            from rouge_score import rouge_scorer
            scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
            scores = scorer.score(reference, hypothesis)
            
            return {
                'rouge1_f': scores['rouge1'].fmeasure * 100,
                'rouge1_p': scores['rouge1'].precision * 100,
                'rouge1_r': scores['rouge1'].recall * 100,
                'rouge2_f': scores['rouge2'].fmeasure * 100,
                'rouge2_p': scores['rouge2'].precision * 100,
                'rouge2_r': scores['rouge2'].recall * 100,
                'rougeL_f': scores['rougeL'].fmeasure * 100,
                'rougeL_p': scores['rougeL'].precision * 100,
                'rougeL_r': scores['rougeL'].recall * 100
            }
        except Exception as e:
            return {'error': str(e)}
    
    def bleu_score(self, reference: str, hypothesis: str, max_n: int = 4) -> Dict[str, float]:
        """
        Calculate BLEU scores (0-100 scale)
        """
        try:
            ref_tokens = [self._tokenize(reference)]
            hyp_tokens = self._tokenize(hypothesis)
            
            scores = {}
            for n in range(1, max_n + 1):
                weights = tuple([1/n] * n)
                score = sentence_bleu(
                    ref_tokens, 
                    hyp_tokens, 
                    weights=weights,
                    smoothing_function=self.smoothing
                )
                scores[f'bleu_{n}'] = score * 100
            
            # Overall BLEU (equally weighted n-grams)
            overall_weights = tuple([1/max_n] * max_n)
            overall_score = sentence_bleu(
                ref_tokens,
                hyp_tokens,
                weights=overall_weights,
                smoothing_function=self.smoothing
            )
            scores['bleu_overall'] = overall_score * 100
            
            return scores
        except Exception as e:
            return {'error': str(e)}
    
    def meteor_score(self, reference: str, hypothesis: str) -> Dict[str, float]:
        """
        Calculate METEOR score (0-100 scale)
        """
        try:
            ref_tokens = self._tokenize(reference)
            hyp_tokens = self._tokenize(hypothesis)
            
            score = meteor_score([ref_tokens], hyp_tokens)
            return {'meteor': score * 100}
        except Exception as e:
            return {'error': str(e)}
    
    def cosine_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity (0-100 scale)
        """
        try:
            tokens1 = self._tokenize(text1)
            tokens2 = self._tokenize(text2)
            
            # Create word frequency vectors
            counter1 = Counter(tokens1)
            counter2 = Counter(tokens2)
            
            # Get all unique words
            all_words = set(counter1.keys()) | set(counter2.keys())
            
            # Create vectors
            vec1 = np.array([counter1.get(w, 0) for w in all_words])
            vec2 = np.array([counter2.get(w, 0) for w in all_words])
            
            # Cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return (dot_product / (norm1 * norm2)) * 100
        except Exception as e:
            return 0.0
    
    def compression_ratio(self, reference: str, hypothesis: str) -> float:
        """
        Calculate compression ratio (0-100 scale)
        """
        original_len = len(reference.split())
        summary_len = len(hypothesis.split())
        
        if original_len == 0:
            return 0.0
        
        return (summary_len / original_len) * 100
    
    def density(self, text: str) -> float:
        """
        Calculate information density (0-100 scale)
        """
        tokens = self._tokenize(text)
        unique_tokens = len(set(tokens))
        total_tokens = len(tokens)
        
        if total_tokens == 0:
            return 0.0
        
        return (unique_tokens / total_tokens) * 100

    def get_source_mapping(self, original_text: str, summary_text: str) -> List[Dict]:
        """
        Map using Semantic Search (SBERT) for production-grade traceability.
        """
        try:
            from sentence_transformers import SentenceTransformer, util
            
            # Sentence Tokenization
            try:
                orig_sents = sent_tokenize(original_text)
                summ_sents = sent_tokenize(summary_text)
            except:
                orig_sents = original_text.split('.')
                summ_sents = summary_text.split('.')
                
            orig_sents = [s.strip() for s in orig_sents if len(s.strip()) > 5]
            summ_sents = [s.strip() for s in summ_sents if len(s.strip()) > 5]
            
            if not orig_sents or not summ_sents: return []

            # Initialize Model (Lazy Load to save memory if not used commonly)
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Compute Embeddings
            orig_embeddings = model.encode(orig_sents, convert_to_tensor=True)
            summ_embeddings = model.encode(summ_sents, convert_to_tensor=True)
            
            # Semantic Similarity
            cosine_scores = util.cos_sim(summ_embeddings, orig_embeddings)
            
            mapping = []
            for i, scores in enumerate(cosine_scores):
                best_idx = scores.argmax().item()
                best_score = scores[best_idx].item() * 100
                
                mapping.append({
                    'summary_sent': summ_sents[i],
                    'source_sent': orig_sents[best_idx],
                    'similarity': float(best_score),
                    'source_index': int(best_idx)
                })
                
            return mapping
            
        except Exception as e:
            # Fallback to TF-IDF if SBERT fails (e.g., model download error)
            # print(f"SBERT failed, falling back: {e}")
            return self._get_source_mapping_tfidf(original_text, summary_text)

    def _get_source_mapping_tfidf(self, original_text: str, summary_text: str) -> List[Dict]:
        """Backup legacy implementation"""
        try:
            # Tokenize sentences
            try:
                orig_sents = sent_tokenize(original_text)
                summ_sents = sent_tokenize(summary_text)
            except:
                orig_sents = original_text.split('.')
                summ_sents = summary_text.split('.')

            # Filter empty sentences
            orig_sents = [s.strip() for s in orig_sents if len(s.strip()) > 5]
            summ_sents = [s.strip() for s in summ_sents if len(s.strip()) > 5]
            
            if not orig_sents or not summ_sents:
                return []

            # TF-IDF Vectorization
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(orig_sents + summ_sents)
            
            # Split matrix back
            orig_tfidf = tfidf_matrix[:len(orig_sents)]
            summ_tfidf = tfidf_matrix[len(orig_sents):]
            
            # Calculate similarity
            similarity_matrix = cosine_similarity(summ_tfidf, orig_tfidf)
            
            mapping = []
            for i, sent_sims in enumerate(similarity_matrix):
                best_idx = sent_sims.argmax()
                best_score = sent_sims[best_idx] * 100  # Scale to 0-100
                
                mapping.append({
                    'summary_sent': summ_sents[i],
                    'source_sent': orig_sents[best_idx],
                    'similarity': float(best_score),
                    'source_index': int(best_idx)
                })
                
            return mapping
            
        except Exception as e:
            return []
    
    def evaluate_summary(self, 
                        original_text: str,
                        generated_summary: str, 
                        reference_summary: str = None) -> Dict:
        """
        Comprehensive evaluation of a generated summary
        """
        results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'generated_summary_length': len(generated_summary.split()),
            'original_text_length': len(original_text.split())
        }
        
        # Always compute these metrics (0-100 scale)
        results['compression_ratio'] = self.compression_ratio(original_text, generated_summary)
        results['density'] = self.density(generated_summary)
        results['text_similarity'] = self.cosine_similarity(original_text, generated_summary)
        
        # Compute Traceability
        results['source_mapping'] = self.get_source_mapping(original_text, generated_summary)
        
        # Compute these only if reference summary is provided
        if reference_summary:
            results['rouge'] = self.rouge_score(reference_summary, generated_summary)
            results['bleu'] = self.bleu_score(reference_summary, generated_summary)
            results['meteor'] = self.meteor_score(reference_summary, generated_summary)
            results['reference_similarity'] = self.cosine_similarity(
                reference_summary, 
                generated_summary
            )
        
        return results
    
    def compare_summaries(self, 
                         summaries: Dict[str, str],
                         reference_summary: str = None,
                         original_text: str = None) -> Dict:
        """
        Compare multiple summaries using all metrics
        """
        results = {}
        
        for name, summary in summaries.items():
            results[name] = self.evaluate_summary(
                original_text or "",
                summary,
                reference_summary
            )
        
        return results
    
    def print_evaluation(self, evaluation_result: Dict, verbose: bool = True):
        """
        Pretty print evaluation results (Updated for 0-100 scale)
        """
        print("\n" + "="*80)
        print(" EVALUATION METRICS (Scale: 0-100%)")
        print("="*80)
        
        # Basic metrics
        print(f"\n Basic Metrics:")
        print(f"   Summary Length: {evaluation_result.get('generated_summary_length')} words")
        print(f"   Original Length: {evaluation_result.get('original_text_length')} words")
        print(f"   Compression Ratio: {evaluation_result.get('compression_ratio', 0):.2f}%")
        print(f"   Information Density: {evaluation_result.get('density', 0):.2f}%")
        print(f"   Text Similarity: {evaluation_result.get('text_similarity', 0):.2f}/100")
        
        # ROUGE scores
        if 'rouge' in evaluation_result:
            print(f"\n ROUGE Scores (0-100):")
            rouge_scores = evaluation_result['rouge']
            if 'error' not in rouge_scores:
                print(f"   ROUGE-1 F1: {rouge_scores.get('rouge1_f', 0):.2f}")
                print(f"   ROUGE-2 F1: {rouge_scores.get('rouge2_f', 0):.2f}")
                print(f"   ROUGE-L F1: {rouge_scores.get('rougeL_f', 0):.2f}")
            else:
                print(f"   Error: {rouge_scores['error']}")
        
        # BLEU scores
        if 'bleu' in evaluation_result:
            print(f"\n BLEU Scores (0-100):")
            bleu_scores = evaluation_result['bleu']
            if 'error' not in bleu_scores:
                print(f"   BLEU-1: {bleu_scores.get('bleu_1', 0):.2f}")
                print(f"   BLEU-2: {bleu_scores.get('bleu_2', 0):.2f}")
                print(f"   BLEU-4: {bleu_scores.get('bleu_4', 0):.2f}")
                print(f"   Overall: {bleu_scores.get('bleu_overall', 0):.2f}")
            else:
                print(f"   Error: {bleu_scores['error']}")
        
        # METEOR score
        if 'meteor' in evaluation_result:
            print(f"\n  METEOR Score (0-100):")
            meteor_score = evaluation_result['meteor']
            if 'error' not in meteor_score:
                print(f"   METEOR: {meteor_score.get('meteor', 0):.2f}")
            else:
                print(f"   Error: {meteor_score['error']}")
        
        # Reference similarity
        if 'reference_similarity' in evaluation_result:
            print(f"\n ✨ Reference Similarity: {evaluation_result['reference_similarity']:.2f}")
        
        print("\n" + "="*80 + "\n")
