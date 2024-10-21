import re
import os
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http import models
import traceback
from typing import Optional, List, Dict, Union, Any
import logging
import time
from functools import wraps

# Load environment variables
load_dotenv()

print(f"API Key: {os.getenv('OPENAI_API_KEY')[:5]}...")
client = OpenAI()

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_SERVICE_API_KEY = os.getenv("QDRANT_SERVICE_API_KEY")

# print out the env variables
print(f"QDRANT_HOST: {QDRANT_HOST}")
print(f"QDRANT_SERVICE_API_KEY: {QDRANT_SERVICE_API_KEY}")

# Initialize Qdrant client
# Initialize Qdrant client
if QDRANT_SERVICE_API_KEY:
    qdrant = QdrantClient(
        host=QDRANT_HOST,
        api_key=QDRANT_SERVICE_API_KEY,
        prefer_grpc=False,
        verify=False,
        https=False,
    )
else:
    qdrant = QdrantClient(host=QDRANT_HOST, prefer_grpc=False, verify=False)

# Set embedding model
EMBEDDING_MODEL = "text-embedding-3-large"
collection_name = "procedures"


def _query_qdrant(
    query, collection_name, vector_name="document", top_k=5, filter_keywords=None
):
    logging.info(f"Starting _query_qdrant with query: {query}")
    logging.info(f"Collection name: {collection_name}")
    logging.info(f"Top k: {top_k}")
    logging.info(f"Filter keywords: {filter_keywords}")

    try:
        start_time = time.time()
        embedded_query = client.embeddings.create(
            input=query,
            model=EMBEDDING_MODEL,
        )
        embedding_time = time.time() - start_time
        logging.info(f"Embedding created in {embedding_time:.2f} seconds")

        vector = embedded_query.data[0].embedding

        search_filter = None
        if filter_keywords:
            search_filter = models.Filter(
                should=[
                    models.FieldCondition(
                        key="metadata.consistent_tags",
                        match=models.MatchAny(any=filter_keywords),
                    ),
                    models.FieldCondition(
                        key="metadata.specific_tags",
                        match=models.MatchAny(any=filter_keywords),
                    ),
                ]
            )
            logging.info(f"Search filter created: {search_filter}")

        start_time = time.time()
        query_results = qdrant.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=top_k,
            query_filter=search_filter,
            with_payload=True,
            with_vectors=False,
        )
        qdrant_search_time = time.time() - start_time
        logging.info(f"Qdrant search completed in {qdrant_search_time:.2f} seconds")
        logging.info(f"Number of results: {len(query_results)}")
        logging.debug(f"Qdrant query results: {query_results}")
        return query_results
    except Exception as e:
        logging.error(f"Error in _query_qdrant: {str(e)}")
        logging.error(f"Error type: {type(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        raise


def query_docs(
    query: str,
    filter_keywords: Optional[List[str]] = None,
    max_results: int = 5,
    **kwargs,
) -> Dict[str, Union[str, List[Dict[str, Any]]]]:
    """
    Query the knowledge base for relevant documents based on the given query.

    This tool searches the Qdrant vector database using the provided query and
    optional filter keywords. It returns the most relevant document snippets
    along with their metadata.

    Args:
        query (str): The search query to find relevant documents.
        filter_keywords (Optional[List[str]]): A list of keywords to filter the results.
        max_results (int): The maximum number of results to return. Defaults to 5.

    Returns:
        Dict[str, Union[str, List[Dict[str, Any]]]]: A dictionary containing:
            - 'response': A string summarizing the search results.
            - 'documents': A list of dictionaries, each containing:
                - 'text': The relevant text snippet.
                - 'metadata': Additional metadata about the document.

    Raises:
        Exception: If there's an error querying the database or processing results.
    """
    print(f"Searching knowledge base with query: {query}")
    try:
        query_results = _query_qdrant(
            query,
            collection_name=collection_name,
            filter_keywords=filter_keywords,
            top_k=max_results,
        )
        documents = []

        for item in query_results:
            documents.append(
                {
                    "text": item.payload["text"],
                    "metadata": {k: v for k, v in item.payload.items() if k != "text"},
                }
            )

        if documents:
            response = f"Found {len(documents)} relevant document(s)."
            print(f"Query response: {response}")
            return {"response": response, "documents": documents}
        else:
            print("No results")
            return {"response": "No results found.", "documents": []}
    except Exception as e:
        error_message = f"Error querying Qdrant: {str(e)}"
        print(error_message)
        print(f"Error type: {type(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            "response": "An error occurred while searching the knowledge base.",
            "documents": [],
        }
