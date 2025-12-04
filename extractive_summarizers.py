"""
Extractive Summarizers Module
Implements various extractive summarization algorithms including:
- TF-IDF based summarization
- Custom TextRank implementation
- Sumy TextRank
- Sumy LexRank
- Sumy LSA
- Semantic TextRank (SBERT-based)
- Embedding-based LexRank
- MMR (Maximal Marginal Relevance)
"""

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from typing import Dict, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np
import networkx as nx
import time


class ExtractiveSummarizers:
    """
    Class containing multiple extractive summarization algorithms
    """

    def __init__(self, language: str = "english"):
        """
        Initialize extractive summarizers

        Args:
            language: Language for text processing
        """
        self.language = language
        self.stemmer = Stemmer(language)
        self.stop_words = get_stop_words(language)
        # lazy-loaded SBERT model holder
        self.sbert_model = None

    def _parse_text(self, text: str) -> PlaintextParser:
        """Parse input text"""
        return PlaintextParser.from_string(text, Tokenizer(self.language))

    # --- SBERT helper loader (lazy) ---
    def _load_embedding_model(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Lazy-load the SBERT model for semantic similarity.
        Default model is 'all-MiniLM-L6-v2' (fast & compact).
        For higher quality use 'paraphrase-mpnet-base-v2' or 'all-mpnet-base-v2'.
        """
        if not hasattr(self, "sbert_model") or self.sbert_model is None:
            try:
                # print only on load to avoid noisy logs in repeated calls
                print(f"Loading SBERT model: {model_name} ...")
                self.sbert_model = SentenceTransformer(model_name)
            except Exception as e:
                self.sbert_model = None
                raise RuntimeError(f"Could not load SBERT model '{model_name}': {e}")

    def textrank_summarize(self, text: str, sentence_count: int = 3) -> Dict:
        """
        TextRank algorithm for extractive summarization

        Args:
            text: Input text to summarize
            sentence_count: Number of sentences in summary

        Returns:
            Dictionary with summary and metadata
        """
        start_time = time.time()

        parser = self._parse_text(text)
        summarizer = TextRankSummarizer(self.stemmer)
        summarizer.stop_words = self.stop_words

        summary_sentences = summarizer(parser.document, sentence_count)
        summary = ' '.join([str(sentence) for sentence in summary_sentences])

        return {
            'algorithm': 'TextRank',
            'type': 'extractive',
            'summary': summary,
            'sentence_count': sentence_count,
            'execution_time': time.time() - start_time
        }

    def lexrank_summarize(self, text: str, sentence_count: int = 3) -> Dict:
        """
        LexRank algorithm for extractive summarization

        Args:
            text: Input text to summarize
            sentence_count: Number of sentences in summary

        Returns:
            Dictionary with summary and metadata
        """
        start_time = time.time()

        parser = self._parse_text(text)
        summarizer = LexRankSummarizer(self.stemmer)
        summarizer.stop_words = self.stop_words

        summary_sentences = summarizer(parser.document, sentence_count)
        summary = ' '.join([str(sentence) for sentence in summary_sentences])

        return {
            'algorithm': 'LexRank',
            'type': 'extractive',
            'summary': summary,
            'sentence_count': sentence_count,
            'execution_time': time.time() - start_time
        }

    def lsa_summarize(self, text: str, sentence_count: int = 3) -> Dict:
        """
        LSA (Latent Semantic Analysis) algorithm for extractive summarization

        Args:
            text: Input text to summarize
            sentence_count: Number of sentences in summary

        Returns:
            Dictionary with summary and metadata
        """
        start_time = time.time()

        parser = self._parse_text(text)
        summarizer = LsaSummarizer(self.stemmer)
        summarizer.stop_words = self.stop_words

        summary_sentences = summarizer(parser.document, sentence_count)
        summary = ' '.join([str(sentence) for sentence in summary_sentences])

        return {
            'algorithm': 'LSA',
            'type': 'extractive',
            'summary': summary,
            'sentence_count': sentence_count,
            'execution_time': time.time() - start_time
        }

    def tfidf_summarize(self, text: str, sentence_count: int = 3) -> Dict:
        """
        TF-IDF based extractive summarization

        Args:
            text: Input text to summarize
            sentence_count: Number of sentences in summary

        Returns:
            Dictionary with summary and metadata
        """
        start_time = time.time()

        # Split text into sentences
        parser = self._parse_text(text)
        sentences = [str(sentence) for sentence in parser.document.sentences]

        if len(sentences) <= sentence_count:
            summary = ' '.join(sentences)
        else:
            # Calculate TF-IDF scores
            vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
            try:
                tfidf_matrix = vectorizer.fit_transform(sentences)

                # Sum TF-IDF scores for each sentence
                sentence_scores = np.array(tfidf_matrix.sum(axis=1)).flatten()

                # Get top sentences by score
                top_indices = np.argsort(sentence_scores)[-sentence_count:]
                top_indices = np.sort(top_indices)  # Sort by original order

                summary = ' '.join([sentences[i] for i in top_indices])
            except:
                summary = ' '.join(sentences[:sentence_count])

        return {
            'algorithm': 'TF-IDF',
            'type': 'extractive',
            'summary': summary,
            'sentence_count': sentence_count,
            'execution_time': time.time() - start_time
        }

    def custom_textrank_summarize(self, text: str, sentence_count: int = 3) -> Dict:
        """
        Custom TextRank implementation from scratch

        Args:
            text: Input text to summarize
            sentence_count: Number of sentences in summary

        Returns:
            Dictionary with summary and metadata
        """
        start_time = time.time()

        parser = self._parse_text(text)
        sentences = [str(sentence) for sentence in parser.document.sentences]

        if len(sentences) <= sentence_count:
            summary = ' '.join(sentences)
        else:
            # Tokenize sentences
            tokenized_sentences = []
            for sentence in sentences:
                words = sentence.lower().split()
                words = [w for w in words if w.isalpha() and w not in self.stop_words]
                tokenized_sentences.append(set(words))

            # Build similarity graph
            similarity_matrix = np.zeros((len(sentences), len(sentences)))

            for i in range(len(sentences)):
                for j in range(len(sentences)):
                    if i != j:
                        # Calculate Jaccard similarity
                        intersection = len(tokenized_sentences[i] & tokenized_sentences[j])
                        union = len(tokenized_sentences[i] | tokenized_sentences[j])
                        similarity_matrix[i][j] = intersection / union if union > 0 else 0

            # Build graph and apply PageRank
            graph = nx.from_numpy_array(similarity_matrix)
            scores = nx.pagerank(graph)

            # Get top sentences
            top_indices = sorted(scores, key=scores.get, reverse=True)[:sentence_count]
            top_indices = sorted(top_indices)

            summary = ' '.join([sentences[i] for i in top_indices])

        return {
            'algorithm': 'Custom TextRank',
            'type': 'extractive',
            'summary': summary,
            'sentence_count': sentence_count,
            'execution_time': time.time() - start_time
        }

    def semantic_textrank_summarize(self, text: str, sentence_count: int = 3,
                                    model_name: str = "all-MiniLM-L6-v2",
                                    similarity_threshold: float = 0.0,
                                    top_k: int = None) -> Dict:
        """
        Semantic TextRank: compute SBERT embeddings for each sentence,
        build similarity graph and run PageRank to select top sentences.

        Args:
            text: Input text
            sentence_count: Desired number of sentences in summary
            model_name: SBERT model name (default 'all-MiniLM-L6-v2')
            similarity_threshold: minimum similarity to keep an edge (0 by default)
            top_k: optionally keep only top_k connections per node (to sparsify graph)

        Returns:
            dict with 'algorithm': 'Semantic TextRank', 'summary', ...
        """
        start_time = time.time()

        parser = self._parse_text(text)
        sentences = [str(s) for s in parser.document.sentences]

        if len(sentences) <= sentence_count:
            summary = ' '.join(sentences)
            return {
                'algorithm': 'Semantic TextRank',
                'type': 'extractive',
                'summary': summary,
                'sentence_count': sentence_count,
                'execution_time': time.time() - start_time
            }

        # Load SBERT
        try:
            if not hasattr(self, "sbert_model") or self.sbert_model is None:
                self._load_embedding_model(model_name=model_name)
            model = self.sbert_model
        except Exception as e:
            return {
                'algorithm': 'Semantic TextRank',
                'type': 'extractive',
                'error': f"Failed to load SBERT model: {str(e)}"
            }

        # Compute sentence embeddings (numpy)
        try:
            embeddings = model.encode(sentences, convert_to_numpy=True, show_progress_bar=False)
        except Exception as e:
            return {
                'algorithm': 'Semantic TextRank',
                'type': 'extractive',
                'error': f"Embedding computation failed: {str(e)}"
            }

        # Build cosine similarity matrix
        sim_matrix = cosine_similarity(embeddings)
        # remove self-similarity on diagonal
        np.fill_diagonal(sim_matrix, 0.0)

        # Optionally sparsify the graph (keep top_k edges per node)
        if top_k is not None and top_k > 0:
            for i in range(sim_matrix.shape[0]):
                row = sim_matrix[i]
                # zero out all but top_k highest values
                if np.count_nonzero(row) > top_k:
                    top_indices = np.argsort(row)[-top_k:]
                    mask = np.ones_like(row, dtype=bool)
                    mask[top_indices] = False
                    row[mask] = 0.0
                    sim_matrix[i] = row

        if similarity_threshold and similarity_threshold > 0.0:
            sim_matrix[sim_matrix < similarity_threshold] = 0.0

        # Build graph and apply PageRank
        try:
            graph = nx.from_numpy_array(sim_matrix)
            # Use weight='weight' so PageRank considers cosine similarities
            scores = nx.pagerank(graph, weight='weight')
        except Exception as e:
            return {
                'algorithm': 'Semantic TextRank',
                'type': 'extractive',
                'error': f"Graph/PageRank failed: {str(e)}"
            }

        # Get top sentence indices by score
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        top_indices = [idx for idx, score in ranked[:sentence_count]]
        top_indices = sorted(top_indices)  # keep original order for readability
        summary_sentences = [sentences[i] for i in top_indices]
        summary = ' '.join(summary_sentences)

        return {
            'algorithm': 'Semantic TextRank',
            'type': 'extractive',
            'summary': summary,
            'sentence_count': sentence_count,
            'model_name': model_name,
            'similarity_threshold': similarity_threshold,
            'top_k': top_k,
            'execution_time': time.time() - start_time
        }

    def embedding_lexrank_summarize(self, text: str, sentence_count: int = 3,
                                   model_name: str = "all-MiniLM-L6-v2",
                                   similarity_threshold: float = 0.0,
                                   top_k: Optional[int] = None) -> Dict:
        """
        Embedding-based LexRank: replace TF-IDF graph with sentence embeddings.
        Computes SBERT embeddings, builds cosine-similarity graph, runs PageRank.

        Args:
            text: Input text
            sentence_count: Desired number of sentences
            model_name: SBERT model name
            similarity_threshold: minimum similarity to keep an edge
            top_k: keep only top_k neighbors per node to sparsify graph

        Returns:
            dict with summary and metadata
        """
        start_time = time.time()

        parser = self._parse_text(text)
        sentences = [str(s) for s in parser.document.sentences]

        if len(sentences) <= sentence_count:
            return {
                'algorithm': 'Embedding LexRank',
                'type': 'extractive',
                'summary': ' '.join(sentences),
                'sentence_count': sentence_count,
                'execution_time': time.time() - start_time
            }

        # Load SBERT
        try:
            if not hasattr(self, "sbert_model") or self.sbert_model is None:
                self._load_embedding_model(model_name=model_name)
            model = self.sbert_model
        except Exception as e:
            return {
                'algorithm': 'Embedding LexRank',
                'type': 'extractive',
                'error': f"Failed to load SBERT model: {str(e)}"
            }

        try:
            embeddings = model.encode(sentences, convert_to_numpy=True, show_progress_bar=False)
        except Exception as e:
            return {
                'algorithm': 'Embedding LexRank',
                'type': 'extractive',
                'error': f"Embedding computation failed: {str(e)}"
            }

        # cosine similarity matrix
        sim_matrix = cosine_similarity(embeddings)
        np.fill_diagonal(sim_matrix, 0.0)

        # sparsify if requested
        if top_k is not None and top_k > 0:
            for i in range(sim_matrix.shape[0]):
                row = sim_matrix[i]
                if np.count_nonzero(row) > top_k:
                    top_indices = np.argsort(row)[-top_k:]
                    mask = np.ones_like(row, dtype=bool)
                    mask[top_indices] = False
                    row[mask] = 0.0
                    sim_matrix[i] = row

        if similarity_threshold and similarity_threshold > 0.0:
            sim_matrix[sim_matrix < similarity_threshold] = 0.0

        # Build graph and PageRank
        try:
            graph = nx.from_numpy_array(sim_matrix)
            scores = nx.pagerank(graph, weight='weight')
        except Exception as e:
            return {
                'algorithm': 'Embedding LexRank',
                'type': 'extractive',
                'error': f"Graph/PageRank failed: {str(e)}"
            }

        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        top_indices = [idx for idx, score in ranked[:sentence_count]]
        top_indices = sorted(top_indices)
        summary = ' '.join([sentences[i] for i in top_indices])

        return {
            'algorithm': 'Embedding LexRank',
            'type': 'extractive',
            'summary': summary,
            'sentence_count': sentence_count,
            'model_name': model_name,
            'similarity_threshold': similarity_threshold,
            'top_k': top_k,
            'execution_time': time.time() - start_time
        }

    def mmr_summarize(self, text: str, sentence_count: int = 3,
                      model_name: str = "all-MiniLM-L6-v2",
                      lambda_param: float = 0.7) -> Dict:
        """
        MMR (Maximal Marginal Relevance) summarizer using SBERT embeddings.
        Selects sentences to balance relevance (to document) and diversity (between selected).

        Args:
            text: Input text
            sentence_count: Number of sentences to select
            model_name: SBERT model name
            lambda_param: trade-off parameter between relevance and diversity (0<=lambda<=1)

        Returns:
            dict with 'algorithm':'MMR', 'summary', ...
        """
        start_time = time.time()

        parser = self._parse_text(text)
        sentences = [str(s) for s in parser.document.sentences]

        if len(sentences) <= sentence_count:
            return {
                'algorithm': 'MMR',
                'type': 'extractive',
                'summary': ' '.join(sentences),
                'sentence_count': sentence_count,
                'execution_time': time.time() - start_time
            }

        # load model
        try:
            if not hasattr(self, "sbert_model") or self.sbert_model is None:
                self._load_embedding_model(model_name=model_name)
            model = self.sbert_model
        except Exception as e:
            return {
                'algorithm': 'MMR',
                'type': 'extractive',
                'error': f"Failed to load SBERT model: {str(e)}"
            }

        try:
            embeddings = model.encode(sentences, convert_to_numpy=True, show_progress_bar=False)
        except Exception as e:
            return {
                'algorithm': 'MMR',
                'type': 'extractive',
                'error': f"Embedding computation failed: {str(e)}"
            }

        # Document embedding as mean of sentence embeddings
        doc_embedding = np.mean(embeddings, axis=0, keepdims=True)
        # relevance: similarity between sentence and document
        relevance = cosine_similarity(doc_embedding, embeddings)[0]  # shape (n_sentences,)

        # pairwise similarities among sentences
        pairwise_sim = cosine_similarity(embeddings)

        # Greedy MMR selection
        selected = []
        unselected = list(range(len(sentences)))

        # initialize by selecting sentence with highest relevance
        first = int(np.argmax(relevance))
        selected.append(first)
        unselected.remove(first)

        while len(selected) < sentence_count and unselected:
            mmr_scores = []
            for i in unselected:
                # diversity = max similarity to any selected sentence
                diversity = max(pairwise_sim[i][j] for j in selected) if selected else 0.0
                mmr_score = lambda_param * relevance[i] - (1 - lambda_param) * diversity
                mmr_scores.append((i, mmr_score))
            # pick sentence with highest mmr_score
            chosen, _ = max(mmr_scores, key=lambda x: x[1])
            selected.append(chosen)
            unselected.remove(chosen)

        # sort selected indexes by original order for coherent summary
        selected_sorted = sorted(selected)
        summary_sentences = [sentences[i] for i in selected_sorted]
        summary = ' '.join(summary_sentences)

        return {
            'algorithm': 'MMR',
            'type': 'extractive',
            'summary': summary,
            'sentence_count': sentence_count,
            'model_name': model_name,
            'lambda_param': lambda_param,
            'execution_time': time.time() - start_time
        }

    def summarize_all(self, text: str, sentence_count: int = 3) -> Dict[str, Dict]:
        """
        Run all extractive summarization algorithms

        Args:
            text: Input text to summarize
            sentence_count: Number of sentences in summary

        Returns:
            Dictionary with results from all algorithms
        """
        return {
            'tfidf': self.tfidf_summarize(text, sentence_count),
            'custom_textrank': self.custom_textrank_summarize(text, sentence_count),
            'sumy_textrank': self.textrank_summarize(text, sentence_count),
            'sumy_lexrank': self.lexrank_summarize(text, sentence_count),
            'sumy_lsa': self.lsa_summarize(text, sentence_count),
            'semantic_textrank': self.semantic_textrank_summarize(text, sentence_count),
            'embedding_lexrank': self.embedding_lexrank_summarize(text, sentence_count),
            'mmr': self.mmr_summarize(text, sentence_count)
        }
