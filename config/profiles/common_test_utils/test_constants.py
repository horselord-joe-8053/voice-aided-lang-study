"""
Test constants and response generators.

Provides standardized test constants and response generators to eliminate
duplication across test files.
"""

from typing import Dict, Any, List


# Common mock response data
MOCK_LLM_RESPONSE = "Test response from LLM"
MOCK_EMBEDDING = [0.1, 0.2, 0.3, 0.4, 0.5]  # 5-dimensional mock embedding


def create_mock_answer_response(
    answer: str = "Test answer from RAG agent",
    sources: List[Dict[str, Any]] = None,
    confidence: str = "high",
    timestamp: str = "2024-01-01T00:00:00"
) -> Dict[str, Any]:
    """
    Create a mock answer response with configurable fields.
    
    Args:
        answer: The answer text
        sources: List of source documents
        confidence: Confidence level
        timestamp: Response timestamp
        
    Returns:
        Dict: Mock answer response
    """
    if sources is None:
        sources = []
    
    return {
        "answer": answer,
        "sources": sources,
        "confidence": confidence,
        "timestamp": timestamp
    }


def create_mock_search_response(
    content: str = "Test search content",
    metadata: Dict[str, Any] = None,
    similarity: float = 0.95
) -> List[Dict[str, Any]]:
    """
    Create a mock search response with configurable fields.
    
    Args:
        content: The content text
        metadata: Document metadata
        similarity: Similarity score
        
    Returns:
        List[Dict]: Mock search response
    """
    if metadata is None:
        metadata = {}
    
    return [
        {
            "content": content,
            "metadata": metadata,
            "similarity": similarity
        }
    ]


def create_mock_stats_response(
    document_count: int = 100,
    total_records: int = 1000,
    total_mappings: int = 50,
    collection_name: str = "test_collection"
) -> Dict[str, Any]:
    """
    Create a mock stats response with configurable fields.
    
    Args:
        document_count: Number of documents in vectorstore
        total_records: Total number of data records
        total_mappings: Total number of sensitization mappings
        collection_name: Vectorstore collection name
        
    Returns:
        Dict: Mock stats response
    """
    return {
        "vectorstore": {
            "status": "initialized",
            "document_count": document_count,
            "collection_name": collection_name
        },
        "data": {
            "total_records": total_records,
            "sensitive_mappings": total_mappings
        },
        "sensitization": {
            "total_mappings": total_mappings
        }
    }


# Common test questions and queries
TEST_QUESTIONS = [
    "What is the average score?",
    "Which dealer has the highest performance?",
    "What are the most common issues?",
    "How many records were processed?"
]

TEST_QUERIES = [
    "customer feedback",
    "service quality", 
    "performance analysis",
    "issue resolution"
]
