import pytest
from src.services.tools.query_data import query_docs, _query_qdrant
from qdrant_client.http.exceptions import UnexpectedResponse
from openai import OpenAIError


def test_query_docs_with_consistent_tag():
    query = "What are the steps involved in a vasectomy procedure?"
    filter_keywords = ["vasectomy"]

    result = query_docs(query, filter_keywords=filter_keywords)

    assert "response" in result
    assert len(result["response"]) > 0
    assert (
        "The procedure involves isolating and dividing both the right and left vas deferens"
        in result["response"]
    )


def test_query_docs_with_consistent_and_specific_tags():
    query = "What should I do to care for the surgical site after a vasectomy?"
    filter_keywords = ["surgical care", "scrotal surgery"]

    result = query_docs(query, filter_keywords=filter_keywords)

    assert "response" in result
    assert len(result["response"]) > 0
    assert "Apply ice packs" in result["response"]
    assert (
        "You can shower tomorrow approximately 24 hours after your surgery"
        in result["response"]
    )


def test_query_docs_with_or_operation():
    query = "What are the symptoms of a urinary tract infection?"
    filter_keywords = [
        "urinary tract infection",
        "vasectomy",
    ]  # Intentionally including an unrelated tag

    result = query_docs(query, filter_keywords=filter_keywords)

    assert "response" in result
    assert len(result["response"]) > 0
    assert "A strong urge to urinate that doesn't go away" in result["response"]
    assert (
        "vasectomy" not in result["response"].lower()
    )  # Ensure vasectomy content is not included


def test_query_qdrant_metadata():
    query = "vasectomy procedure"
    try:
        results = _query_qdrant(query, "procedures")
        assert len(results) > 0

        for result in results:
            metadata = result.payload["metadata"]
            assert "procedure" in metadata
            assert "type" in metadata
            assert isinstance(metadata["chunk_index"], int)
            assert isinstance(metadata["total_chunks"], int)
            assert metadata["source_file"].endswith(".md")
            assert isinstance(metadata["consistent_tags"], list)
            assert isinstance(metadata["specific_tags"], list)
            assert len(metadata["consistent_tags"]) > 0
            assert len(metadata["specific_tags"]) > 0
    except (OpenAIError, UnexpectedResponse) as e:
        pytest.skip(f"Skipping due to connection error: {str(e)}")
