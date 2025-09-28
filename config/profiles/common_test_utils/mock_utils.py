"""
Mock utilities for testing.

Provides standardized mock creation functions to eliminate duplication
across test files.
"""

from unittest.mock import Mock
from typing import Dict, Any, List
from langchain_core.runnables import Runnable


# Common mock response data
MOCK_LLM_RESPONSE = "Test response from LLM"
MOCK_EMBEDDING = [0.1, 0.2, 0.3, 0.4, 0.5]  # 5-dimensional mock embedding


def create_mock_llm() -> Mock:
    """
    Create a mock LLM compatible with LangChain's Runnable interface.
    
    Returns:
        Mock: A properly configured mock LLM with all required methods
    """
    mock_llm = Mock(spec=Runnable)
    mock_llm.invoke = Mock(return_value=Mock(content=MOCK_LLM_RESPONSE))
    mock_llm.stream = Mock(return_value=[Mock(content=MOCK_LLM_RESPONSE)])
    mock_llm.ainvoke = Mock(return_value=Mock(content=MOCK_LLM_RESPONSE))
    mock_llm.astream = Mock(return_value=[Mock(content=MOCK_LLM_RESPONSE)])
    mock_llm.batch = Mock(return_value=[Mock(content=MOCK_LLM_RESPONSE)])
    mock_llm.abatch = Mock(return_value=[Mock(content=MOCK_LLM_RESPONSE)])
    # Needed by create_tool_calling_agent
    mock_llm.bind_tools = Mock(return_value=mock_llm)
    return mock_llm


def create_mock_embeddings() -> Mock:
    """
    Create a mock embeddings model.
    
    Returns:
        Mock: A properly configured mock embeddings model
    """
    mock_embeddings = Mock()
    mock_embeddings.embed_documents = Mock(return_value=[MOCK_EMBEDDING])
    mock_embeddings.embed_query = Mock(return_value=MOCK_EMBEDDING)
    return mock_embeddings


def create_mock_rag_agent(
    answer_response: Dict[str, Any] = None,
    search_response: List[Dict[str, Any]] = None,
    stats_response: Dict[str, Any] = None
) -> Mock:
    """
    Create a mock RAG agent with configurable responses.
    
    Args:
        answer_response: Mock response for answer_question method
        search_response: Mock response for search_relevant_chunks method  
        stats_response: Mock response for get_stats method
        
    Returns:
        Mock: A properly configured mock RAG agent
    """
    agent = Mock()
    
    # Default responses
    default_answer = {
        "answer": "Test answer from RAG agent",
        "sources": [],
        "confidence": "high",
        "timestamp": "2024-01-01T00:00:00"
    }
    
    default_search = []
    
    default_stats = {
        "vectorstore": {"document_count": 100},
        "data": {"total_records": 1000},
        "sensitization": {"total_mappings": 50}
    }
    
    agent.answer_question.return_value = answer_response or default_answer
    agent.search_relevant_chunks.return_value = search_response or default_search
    agent.get_stats.return_value = stats_response or default_stats
    agent.rebuild_vectorstore.return_value = True
    agent.get_sensitization_stats.return_value = {"total_mappings": 50}
    
    return agent


def create_mock_rag_agent_with_error() -> Mock:
    """
    Create a mock RAG agent that raises exceptions.
    
    Returns:
        Mock: A mock RAG agent that raises errors for all methods
    """
    agent = Mock()
    agent.answer_question.side_effect = Exception("RAG agent error")
    agent.search_relevant_chunks.side_effect = Exception("Search error")
    agent.get_stats.side_effect = Exception("Stats error")
    agent.rebuild_vectorstore.side_effect = Exception("Rebuild error")
    agent.get_sensitization_stats.side_effect = Exception("Sensitization stats error")
    return agent
