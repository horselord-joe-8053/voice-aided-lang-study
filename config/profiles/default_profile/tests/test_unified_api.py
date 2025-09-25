#!/usr/bin/env python3
"""
Test cases for the Unified API integration.
Tests the FastAPI endpoints with the unified engine.
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from api.unified_api import app
from core.unified_engine import UnifiedQueryEngine

# =============================================================================
# TEST CONSTANTS
# =============================================================================

TEST_QUESTION = "What is the average price of Samsung fridges?"
TEST_METHOD = "auto"
TEST_QUERY = "Samsung fridges"

MOCK_UNIFIED_RESPONSE = {
    "question": TEST_QUESTION,
    "answer": "The average price of Samsung fridges is $1,299.99",
    "sources": [{"brand": "Samsung", "price": 1299.99}],
    "confidence": "high",
    "method_used": "text2query",
    "execution_time": 1.23,
    "timestamp": "2024-01-15T10:30:00Z",
    "profile": "default_profile"
}

MOCK_SEARCH_RESPONSE = [
    {
        "content": "Samsung fridge data",
        "metadata": {"brand": "Samsung"},
        "similarity": 0.95
    }
]

MOCK_STATS_RESPONSE = {
    "profile": "default_profile",
    "data": {"total_records": 100},
    "engines": {"text2query_available": True, "rag_available": True},
    "text2query": {"total_records": 100},
    "rag": {"vectorstore": {"status": "ready"}}
}

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_unified_engine():
    """Create a mock unified engine."""
    engine = Mock(spec=UnifiedQueryEngine)
    engine.answer_question.return_value = MOCK_UNIFIED_RESPONSE
    engine.search_data.return_value = MOCK_SEARCH_RESPONSE
    engine.get_stats.return_value = MOCK_STATS_RESPONSE
    engine.get_available_methods.return_value = ["text2query", "rag"]
    engine.rebuild_rag_index.return_value = True
    return engine

@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)

# =============================================================================
# API ENDPOINT TESTS
# =============================================================================

class TestUnifiedAPIEndpoints:
    """Test the unified API endpoints."""
    
    @patch('api.unified_api.get_unified_engine')
    def test_root_endpoint(self, mock_get_engine, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Unified QueryRAG System API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
    
    @patch('api.unified_api.get_unified_engine')
    def test_health_check(self, mock_get_engine, client, mock_unified_engine):
        """Test the health check endpoint."""
        mock_get_engine.return_value = mock_unified_engine
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "profile" in data
        assert "engines" in data
    
    @patch('api.unified_api.get_unified_engine')
    def test_ask_endpoint_success(self, mock_get_engine, client, mock_unified_engine):
        """Test the ask endpoint with successful response."""
        mock_get_engine.return_value = mock_unified_engine
        
        payload = {
            "question": TEST_QUESTION,
            "method": TEST_METHOD
        }
        
        response = client.post("/ask", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["question"] == TEST_QUESTION
        assert data["answer"] == MOCK_UNIFIED_RESPONSE["answer"]
        assert data["method_used"] == "text2query"
        assert data["confidence"] == "high"
        assert "execution_time" in data
        assert "timestamp" in data
        assert "profile" in data
        
        # Verify engine was called
        mock_unified_engine.answer_question.assert_called_once_with(TEST_QUESTION, TEST_METHOD)
    
    @patch('api.unified_api.get_unified_engine')
    def test_ask_endpoint_auto_method(self, mock_get_engine, client, mock_unified_engine):
        """Test the ask endpoint with auto method (default)."""
        mock_get_engine.return_value = mock_unified_engine
        
        payload = {"question": TEST_QUESTION}
        
        response = client.post("/ask", json=payload)
        assert response.status_code == 200
        
        # Verify engine was called with default method
        mock_unified_engine.answer_question.assert_called_once_with(TEST_QUESTION, "auto")
    
    @patch('api.unified_api.get_unified_engine')
    def test_ask_endpoint_text2query_method(self, mock_get_engine, client, mock_unified_engine):
        """Test the ask endpoint with text2query method."""
        mock_get_engine.return_value = mock_unified_engine
        
        payload = {
            "question": TEST_QUESTION,
            "method": "text2query"
        }
        
        response = client.post("/ask", json=payload)
        assert response.status_code == 200
        
        # Verify engine was called with text2query method
        mock_unified_engine.answer_question.assert_called_once_with(TEST_QUESTION, "text2query")
    
    @patch('api.unified_api.get_unified_engine')
    def test_ask_endpoint_rag_method(self, mock_get_engine, client, mock_unified_engine):
        """Test the ask endpoint with rag method."""
        mock_get_engine.return_value = mock_unified_engine
        
        payload = {
            "question": TEST_QUESTION,
            "method": "rag"
        }
        
        response = client.post("/ask", json=payload)
        assert response.status_code == 200
        
        # Verify engine was called with rag method
        mock_unified_engine.answer_question.assert_called_once_with(TEST_QUESTION, "rag")
    
    @patch('api.unified_api.get_unified_engine')
    def test_ask_endpoint_missing_question(self, mock_get_engine, client, mock_unified_engine):
        """Test the ask endpoint with missing question."""
        mock_get_engine.return_value = mock_unified_engine
        
        payload = {"method": "auto"}
        
        response = client.post("/ask", json=payload)
        assert response.status_code == 422  # Validation error
    
    @patch('api.unified_api.get_unified_engine')
    def test_ask_endpoint_engine_error(self, mock_get_engine, client, mock_unified_engine):
        """Test the ask endpoint when engine raises an error."""
        mock_get_engine.return_value = mock_unified_engine
        mock_unified_engine.answer_question.side_effect = Exception("Engine error")
        
        payload = {"question": TEST_QUESTION}
        
        response = client.post("/ask", json=payload)
        assert response.status_code == 500
        assert "Error processing question" in response.json()["detail"]
    
    @patch('api.unified_api.get_unified_engine')
    def test_search_endpoint(self, mock_get_engine, client, mock_unified_engine):
        """Test the search endpoint."""
        mock_get_engine.return_value = mock_unified_engine
        
        payload = {
            "query": TEST_QUERY,
            "top_k": 10
        }
        
        response = client.post("/search", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["query"] == TEST_QUERY
        assert data["results"] == MOCK_SEARCH_RESPONSE
        assert data["total_found"] == 1
        
        # Verify engine was called
        mock_unified_engine.search_data.assert_called_once_with(TEST_QUERY, 10)
    
    @patch('api.unified_api.get_unified_engine')
    def test_search_endpoint_default_top_k(self, mock_get_engine, client, mock_unified_engine):
        """Test the search endpoint with default top_k."""
        mock_get_engine.return_value = mock_unified_engine
        
        payload = {"query": TEST_QUERY}
        
        response = client.post("/search", json=payload)
        assert response.status_code == 200
        
        # Verify engine was called with default top_k
        mock_unified_engine.search_data.assert_called_once_with(TEST_QUERY, 10)
    
    @patch('api.unified_api.get_unified_engine')
    def test_stats_endpoint(self, mock_get_engine, client, mock_unified_engine):
        """Test the stats endpoint."""
        mock_get_engine.return_value = mock_unified_engine
        
        response = client.get("/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["profile"] == "default_profile"
        assert "data" in data
        assert "engines" in data
        assert "text2query" in data
        assert "rag" in data
        
        # Verify engine was called
        mock_unified_engine.get_stats.assert_called_once()
    
    @patch('api.unified_api.get_unified_engine')
    def test_methods_endpoint(self, mock_get_engine, client, mock_unified_engine):
        """Test the methods endpoint."""
        mock_get_engine.return_value = mock_unified_engine
        
        response = client.get("/methods")
        assert response.status_code == 200
        
        data = response.json()
        assert data["available_methods"] == ["text2query", "rag"]
        assert data["current_profile"] == "default_profile"
        
        # Verify engine was called
        mock_unified_engine.get_available_methods.assert_called_once()
        mock_unified_engine.get_stats.assert_called_once()
    
    @patch('api.unified_api.get_unified_engine')
    def test_rebuild_endpoint_success(self, mock_get_engine, client, mock_unified_engine):
        """Test the rebuild endpoint with success."""
        mock_get_engine.return_value = mock_unified_engine
        
        response = client.post("/rebuild")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "rebuilt successfully" in data["message"]
        
        # Verify engine was called
        mock_unified_engine.rebuild_rag_index.assert_called_once()
    
    @patch('api.unified_api.get_unified_engine')
    def test_rebuild_endpoint_failure(self, mock_get_engine, client, mock_unified_engine):
        """Test the rebuild endpoint with failure."""
        mock_get_engine.return_value = mock_unified_engine
        mock_unified_engine.rebuild_rag_index.return_value = False
        
        response = client.post("/rebuild")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "error"
        assert "Failed to rebuild" in data["message"]
    
    @patch('api.unified_api.get_unified_engine')
    def test_rebuild_endpoint_error(self, mock_get_engine, client, mock_unified_engine):
        """Test the rebuild endpoint with exception."""
        mock_get_engine.return_value = mock_unified_engine
        mock_unified_engine.rebuild_rag_index.side_effect = Exception("Rebuild error")
        
        response = client.post("/rebuild")
        assert response.status_code == 500
        assert "Error rebuilding RAG vector store" in response.json()["detail"]
    
    @patch('api.unified_api.get_unified_engine')
    def test_profile_endpoint(self, mock_get_engine, client, mock_unified_engine):
        """Test the profile endpoint."""
        mock_get_engine.return_value = mock_unified_engine
        
        response = client.get("/profile")
        assert response.status_code == 200
        
        data = response.json()
        assert "active_profile" in data
        assert "profile_name" in data
        assert "language" in data
        assert "data_schema" in data
        assert "engines" in data

# =============================================================================
# BACKWARD COMPATIBILITY TESTS
# =============================================================================

class TestBackwardCompatibility:
    """Test backward compatibility endpoints."""
    
    @patch('api.unified_api.get_unified_engine')
    def test_ask_api_endpoint(self, mock_get_engine, client, mock_unified_engine):
        """Test the backward compatibility ask-api endpoint."""
        mock_get_engine.return_value = mock_unified_engine
        
        payload = {"question": TEST_QUESTION}
        
        response = client.post("/ask-api", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["question"] == TEST_QUESTION
        assert data["answer"] == MOCK_UNIFIED_RESPONSE["answer"]
        
        # Verify engine was called
        mock_unified_engine.answer_question.assert_called_once_with(TEST_QUESTION, "auto")

# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestErrorHandling:
    """Test error handling in API endpoints."""
    
    @patch('api.unified_api.get_unified_engine')
    def test_health_check_error(self, mock_get_engine, client, mock_unified_engine):
        """Test health check with engine error."""
        mock_get_engine.return_value = mock_unified_engine
        mock_unified_engine.get_stats.side_effect = Exception("Stats error")
        
        response = client.get("/health")
        assert response.status_code == 500
        assert "Health check failed" in response.json()["detail"]
    
    @patch('api.unified_api.get_unified_engine')
    def test_stats_endpoint_error(self, mock_get_engine, client, mock_unified_engine):
        """Test stats endpoint with engine error."""
        mock_get_engine.return_value = mock_unified_engine
        mock_unified_engine.get_stats.side_effect = Exception("Stats error")
        
        response = client.get("/stats")
        assert response.status_code == 500
        assert "Error getting stats" in response.json()["detail"]
    
    @patch('api.unified_api.get_unified_engine')
    def test_search_endpoint_error(self, mock_get_engine, client, mock_unified_engine):
        """Test search endpoint with engine error."""
        mock_get_engine.return_value = mock_unified_engine
        mock_unified_engine.search_data.side_effect = Exception("Search error")
        
        payload = {"query": TEST_QUERY}
        
        response = client.post("/search", json=payload)
        assert response.status_code == 500
        assert "Error searching data" in response.json()["detail"]
    
    @patch('api.unified_api.get_unified_engine')
    def test_methods_endpoint_error(self, mock_get_engine, client, mock_unified_engine):
        """Test methods endpoint with engine error."""
        mock_get_engine.return_value = mock_unified_engine
        mock_unified_engine.get_available_methods.side_effect = Exception("Methods error")
        
        response = client.get("/methods")
        assert response.status_code == 500
        assert "Error getting methods" in response.json()["detail"]
    
    @patch('api.unified_api.get_unified_engine')
    def test_profile_endpoint_error(self, mock_get_engine, client, mock_unified_engine):
        """Test profile endpoint with engine error."""
        mock_get_engine.return_value = mock_unified_engine
        mock_unified_engine.get_stats.side_effect = Exception("Profile error")
        
        response = client.get("/profile")
        assert response.status_code == 500
        assert "Error getting profile info" in response.json()["detail"]

# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Test integration scenarios."""
    
    @patch('api.unified_api.get_unified_engine')
    def test_multiple_requests_workflow(self, mock_get_engine, client, mock_unified_engine):
        """Test handling multiple requests in sequence."""
        mock_get_engine.return_value = mock_unified_engine
        
        # Test health check
        response = client.get("/health")
        assert response.status_code == 200
        
        # Test ask question
        response = client.post("/ask", json={"question": TEST_QUESTION})
        assert response.status_code == 200
        
        # Test search
        response = client.post("/search", json={"query": TEST_QUERY})
        assert response.status_code == 200
        
        # Test stats
        response = client.get("/stats")
        assert response.status_code == 200
        
        # Test methods
        response = client.get("/methods")
        assert response.status_code == 200
        
        # Verify all engine methods were called
        assert mock_unified_engine.get_stats.call_count >= 2
        assert mock_unified_engine.answer_question.call_count == 1
        assert mock_unified_engine.search_data.call_count == 1
        assert mock_unified_engine.get_available_methods.call_count == 1
    
    @patch('api.unified_api.get_unified_engine')
    def test_different_methods_workflow(self, mock_get_engine, client, mock_unified_engine):
        """Test using different methods for the same question."""
        mock_get_engine.return_value = mock_unified_engine
        
        # Test auto method
        response = client.post("/ask", json={"question": TEST_QUESTION, "method": "auto"})
        assert response.status_code == 200
        
        # Test text2query method
        response = client.post("/ask", json={"question": TEST_QUESTION, "method": "text2query"})
        assert response.status_code == 200
        
        # Test rag method
        response = client.post("/ask", json={"question": TEST_QUESTION, "method": "rag"})
        assert response.status_code == 200
        
        # Verify engine was called with different methods
        assert mock_unified_engine.answer_question.call_count == 3
        calls = mock_unified_engine.answer_question.call_args_list
        assert calls[0][0][1] == "auto"
        assert calls[1][0][1] == "text2query"
        assert calls[2][0][1] == "rag"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
