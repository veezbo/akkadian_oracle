from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from datasets import load_dataset


# This is my dataset on HuggingFace designed to be used as a cleaned English-translated Akkadian corpus.
# The dataset was generated using the code in this repo: https://github.com/veezbo/akkadian_english_corpus/
DATASET_NAME = "veezbo/akkadian_english_corpus"


def load_corpus() -> List[str]:
    """
    Retrieve a HuggingFace dataset and transform it into a list of sentence strings.

    Parameters:
    dataset_name (str): The name of the dataset to load.
    split (str): The split of the dataset to load (e.g., 'train', 'test').

    Returns:
    List[str]: The sentences in the dataset.
    """

    # Load the dataset
    dataset = load_dataset(DATASET_NAME, split="train", keep_in_memory=True)

    # Extract the sentences
    sentences = [item['text'] for item in dataset]

    return sentences


def retrieve_related_sentences(corpus: List[str], query: str, top_n: int) -> List[str]:
    """
    Retrieve the top_n most relevant sentences to a query from a corpus using TF-IDF and cosine similarity.

    Parameters:
    corpus (List[str]): The corpus of sentences.
    query (str): The query to find relevant sentences for.
    top_n (int): The number of sentences to retrieve. Default is 5.

    Returns:
    List[str]: The top_n most relevant sentences to the query.
    """

    # Create a TfidfVectorizer object with English stop words
    vectorizer = TfidfVectorizer(stop_words='english')

    # Convert the corpus to a matrix of TF-IDF features
    tfidf = vectorizer.fit_transform(corpus)

    # Convert the query to a matrix of TF-IDF features
    query_tfidf = vectorizer.transform([query])

    # Compute cosine similarity between the query and the corpus
    cosine_similarities = linear_kernel(query_tfidf, tfidf).flatten()

    # Get the indices of the top_n most similar sentences
    related_docs_indices = cosine_similarities.argsort()[:-top_n:-1]

    # Return the most similar sentences
    return [corpus[i] for i in related_docs_indices]
