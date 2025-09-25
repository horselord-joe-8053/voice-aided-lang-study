"""
Base test classes for common testing patterns.

Provides base test classes to eliminate duplication across test files.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any, List

from .mock_utils import create_mock_llm, create_mock_embeddings, create_mock_rag_agent
from .test_helpers import create_test_csv, cleanup_temp_file
from .test_constants import MOCK_LLM_RESPONSE, MOCK_EMBEDDING


class BaseRAGAgentTest:
    """Base class for RAG agent tests with common setup and utilities."""
    
    def create_mock_llm(self) -> Mock:
        """Create a mock LLM for testing."""
        return create_mock_llm()
    
    def create_mock_embeddings(self) -> Mock:
        """Create mock embeddings for testing."""
        return create_mock_embeddings()
    
    def create_mock_rag_agent(self, **kwargs) -> Mock:
        """Create a mock RAG agent for testing."""
        return create_mock_rag_agent(**kwargs)
    
    def create_test_csv(self, headers: List[str], rows: List[List[str]] = None) -> str:
        """Create a temporary CSV file for testing."""
        return create_test_csv(headers, rows)
    
    def cleanup_temp_file(self, file_path: str) -> None:
        """Clean up a temporary file."""
        cleanup_temp_file(file_path)


class BaseVectorStoreTest:
    """Base class for vector store tests with common setup and utilities."""
    
    def create_mock_embeddings(self) -> Mock:
        """Create mock embeddings for testing."""
        return create_mock_embeddings()
    
    def _test_vector_store_initialization(self, vectorstore_class, test_dir: str, collection_name: str = "test_collection"):
        """Test vector store initialization."""
        mock_embeddings = self.create_mock_embeddings()
        vectorstore = vectorstore_class(test_dir, mock_embeddings, collection_name)
        
        assert vectorstore.persist_directory == Path(test_dir)
        assert vectorstore.embeddings == mock_embeddings
        assert vectorstore.collection_name == collection_name
    
    def _test_vector_store_initialization_with_custom_collection(self, vectorstore_class, test_dir: str):
        """Test vector store initialization with custom collection name."""
        mock_embeddings = self.create_mock_embeddings()
        custom_collection = "custom_collection"
        vectorstore = vectorstore_class(test_dir, mock_embeddings, custom_collection)
        
        assert vectorstore.collection_name == custom_collection
    
    def _test_get_stats_not_initialized(self, vectorstore_class, test_dir: str):
        """Test getting stats when vector store is not initialized."""
        mock_embeddings = self.create_mock_embeddings()
        vectorstore = vectorstore_class(test_dir, mock_embeddings, "test_collection")
        
        stats = vectorstore.get_stats()
        assert stats["status"] == "not_initialized"
        assert stats["collection_name"] == "test_collection"


class BaseDataProcessorTest:
    """Base class for data processor tests with common setup and utilities."""
    
    def create_test_csv(self, headers: List[str], rows: List[List[str]] = None) -> str:
        """Create a temporary CSV file for testing."""
        return create_test_csv(headers, rows)
    
    def cleanup_temp_file(self, file_path: str) -> None:
        """Clean up a temporary file."""
        cleanup_temp_file(file_path)
    
    def test_data_processor_initialization(self, processor_class, csv_file: str, schema):
        """Test data processor initialization."""
        processor = processor_class(csv_file, schema)
        assert processor.csv_file == Path(csv_file)
        assert processor.data_schema == schema
    
    def test_data_processor_load_data(self, processor_class, csv_file: str, schema):
        """Test data processor data loading."""
        processor = processor_class(csv_file, schema)
        data = processor.load_data()
        assert data is not None
        assert len(data) > 0
    
    def test_data_processor_get_stats(self, processor_class, csv_file: str, schema):
        """Test data processor stats generation."""
        processor = processor_class(csv_file, schema)
        stats = processor.get_stats()
        assert "total_records" in stats
        assert "sensitive_mappings" in stats
        assert stats["total_records"] > 0
