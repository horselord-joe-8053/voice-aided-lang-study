"""
Common test utilities for profile-aware testing.

This module provides shared utilities, constants, and base classes
to eliminate code duplication across profile test files.
"""

from .mock_utils import (
    create_mock_llm,
    create_mock_embeddings,
    create_mock_rag_agent,
    create_mock_rag_agent_with_error
)

from .test_constants import (
    MOCK_LLM_RESPONSE,
    MOCK_EMBEDDING,
    create_mock_answer_response,
    create_mock_search_response,
    create_mock_stats_response
)

from .test_helpers import (
    create_test_csv,
    get_test_data_schema,
    cleanup_temp_file
)

from .base_test_classes import (
    BaseRAGAgentTest,
    BaseVectorStoreTest,
    BaseDataProcessorTest
)

__all__ = [
    # Mock utilities
    'create_mock_llm',
    'create_mock_embeddings', 
    'create_mock_rag_agent',
    'create_mock_rag_agent_with_error',
    
    # Test constants
    'MOCK_LLM_RESPONSE',
    'MOCK_EMBEDDING',
    'create_mock_answer_response',
    'create_mock_search_response',
    'create_mock_stats_response',
    
    # Test helpers
    'create_test_csv',
    'get_test_data_schema',
    'cleanup_temp_file',
    
    # Base test classes
    'BaseRAGAgentTest',
    'BaseVectorStoreTest',
    'BaseDataProcessorTest'
]
