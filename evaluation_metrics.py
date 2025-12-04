"""
Evaluation Metrics Module
Provides various metrics to evaluate summarization quality
Includes: ROUGE, BLEU, METEOR, CIDEr, and custom metrics
"""

from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
from nltk.tokenize import word_tokenize
from typing import Dict, List, Tuple
import numpy as np
from collections import Counter
import time


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
        Calculate ROUGE scores (Recall-Oriented Understudy for Gisting Evaluation)
        
        ROUGE includes:
        - ROUGE-1: Unigram overlap
        - ROUGE-2: Bigram overlap
        - ROUGE-L: Longest common subsequence
        
        Args:
            reference: Reference/ground truth summary
            hypothesis: Generated/candidate summary
            
        Returns:
            Dictionary with ROUGE-1, ROUGE-2, ROUGE-L scores (F1 measures)
        """
        try:
            from rouge_score import rouge_scorer
            scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
            scores = scorer.score(reference, hypothesis)
            
            return {
                'rouge1_f': scores['rouge1'].fmeasure,
                'rouge1_p': scores['rouge1'].precision,
                'rouge1_r': scores['rouge1'].recall,
                'rouge2_f': scores['rouge2'].fmeasure,
                'rouge2_p': scores['rouge2'].precision,
                'rouge2_r': scores['rouge2'].recall,
                'rougeL_f': scores['rougeL'].fmeasure,
                'rougeL_p': scores['rougeL'].precision,
                'rougeL_r': scores['rougeL'].recall
            }
        except Exception as e:
            return {'error': str(e)}
    
    def bleu_score(self, reference: str, hypothesis: str, max_n: int = 4) -> Dict[str, float]:
        """
        Calculate BLEU (BiLingual Evaluation Understudy) scores
        
        BLEU measures n-gram precision (1-gram to n-gram)
        
        Args:
            reference: Reference summary
            hypothesis: Generated summary
            max_n: Maximum n-gram to consider (default 4)
            
        Returns:
            Dictionary with BLEU scores for different n-grams
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
                scores[f'bleu_{n}'] = score
            
            # Overall BLEU (equally weighted n-grams)
            overall_weights = tuple([1/max_n] * max_n)
            overall_score = sentence_bleu(
                ref_tokens,
                hyp_tokens,
                weights=overall_weights,
                smoothing_function=self.smoothing
            )
            scores['bleu_overall'] = overall_score
            
            return scores
        except Exception as e:
            return {'error': str(e)}
    
    def meteor_score(self, reference: str, hypothesis: str) -> Dict[str, float]:
        """
        Calculate METEOR (Metric for Evaluation of Translation with Explicit Ordering)
        
        METEOR considers synonyms and word order
        
        Args:
            reference: Reference summary
            hypothesis: Generated summary
            
        Returns:
            Dictionary with METEOR score
        """
        try:
            ref_tokens = self._tokenize(reference)
            hyp_tokens = self._tokenize(hypothesis)
            
            score = meteor_score([ref_tokens], hyp_tokens)
            return {'meteor': score}
        except Exception as e:
            return {'error': str(e)}
    
    def cosine_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts using word vectors
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0-1)
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
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            return 0.0
    
    def compression_ratio(self, reference: str, hypothesis: str) -> float:
        """
        Calculate compression ratio of the summary
        
        Args:
            reference: Original text
            hypothesis: Summary
            
        Returns:
            Compression ratio (summary_length / original_length)
        """
        original_len = len(reference.split())
        summary_len = len(hypothesis.split())
        
        if original_len == 0:
            return 0.0
        
        return summary_len / original_len
    
    def density(self, text: str) -> float:
        """
        Calculate information density (unique words / total words)
        
        Args:
            text: Input text
            
        Returns:
            Density score (0-1)
        """
        tokens = self._tokenize(text)
        unique_tokens = len(set(tokens))
        total_tokens = len(tokens)
        
        if total_tokens == 0:
            return 0.0
        
        return unique_tokens / total_tokens
    
    def evaluate_summary(self, 
                        original_text: str,
                        generated_summary: str, 
                        reference_summary: str = None) -> Dict:
        """
        Comprehensive evaluation of a generated summary
        
        Args:
            original_text: Original text
            generated_summary: Generated/candidate summary
            reference_summary: Reference/ground truth summary (optional)
            
        Returns:
            Dictionary with all evaluation metrics
        """
        results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'generated_summary_length': len(generated_summary.split()),
            'original_text_length': len(original_text.split())
        }
        
        # Always compute these metrics
        results['compression_ratio'] = self.compression_ratio(original_text, generated_summary)
        results['density'] = self.density(generated_summary)
        results['text_similarity'] = self.cosine_similarity(original_text, generated_summary)
        
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
        
        Args:
            summaries: Dictionary of {name: summary_text}
            reference_summary: Reference summary for comparison
            original_text: Original text for metrics
            
        Returns:
            Dictionary with comparison results for all summaries
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
        Pretty print evaluation results
        
        Args:
            evaluation_result: Result from evaluate_summary()
            verbose: Whether to print detailed information
        """
        print("\n" + "="*80)
        print(" EVALUATION METRICS")
        print("="*80)
        
        # Basic metrics
        print(f"\n Basic Metrics:")
        print(f"   Summary Length: {evaluation_result.get('generated_summary_length')} words")
        print(f"   Original Length: {evaluation_result.get('original_text_length')} words")
        print(f"   Compression Ratio: {evaluation_result.get('compression_ratio', 0):.2%}")
        print(f"   Information Density: {evaluation_result.get('density', 0):.2%}")
        print(f"   Text Similarity: {evaluation_result.get('text_similarity', 0):.4f}")
        
        # ROUGE scores
        if 'rouge' in evaluation_result:
            print(f"\n ROUGE Scores:")
            rouge_scores = evaluation_result['rouge']
            if 'error' not in rouge_scores:
                print(f"   ROUGE-1 F1: {rouge_scores.get('rouge1_f', 0):.4f}")
                print(f"   ROUGE-2 F1: {rouge_scores.get('rouge2_f', 0):.4f}")
                print(f"   ROUGE-L F1: {rouge_scores.get('rougeL_f', 0):.4f}")
            else:
                print(f"   Error: {rouge_scores['error']}")
        
        # BLEU scores
        if 'bleu' in evaluation_result:
            print(f"\n BLEU Scores:")
            bleu_scores = evaluation_result['bleu']
            if 'error' not in bleu_scores:
                print(f"   BLEU-1: {bleu_scores.get('bleu_1', 0):.4f}")
                print(f"   BLEU-2: {bleu_scores.get('bleu_2', 0):.4f}")
                print(f"   BLEU-4: {bleu_scores.get('bleu_4', 0):.4f}")
                print(f"   Overall: {bleu_scores.get('bleu_overall', 0):.4f}")
            else:
                print(f"   Error: {bleu_scores['error']}")
        
        # METEOR score
        if 'meteor' in evaluation_result:
            print(f"\n  METEOR Score:")
            meteor_score = evaluation_result['meteor']
            if 'error' not in meteor_score:
                print(f"   METEOR: {meteor_score.get('meteor', 0):.4f}")
            else:
                print(f"   Error: {meteor_score['error']}")
        
        # Reference similarity
        if 'reference_similarity' in evaluation_result:
            print(f"\n✨ Reference Similarity: {evaluation_result['reference_similarity']:.4f}")
        
        print("\n" + "="*80 + "\n")
