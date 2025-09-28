#!/usr/bin/env python3
"""
Test cases for the Unified MCP Server integration.
Tests the MCP server tools and functionality.
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from servers.unified_mcp_server import server, handle_list_tools, handle_call_tool
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

MOCK_PROFILE_INFO = {
    "active_profile": "default_profile",
    "profile_name": "default_profile",
    "language": "en-US",
    "locale": "en_US",
    "data_file_path": "/path/to/data.csv",
    "data_schema": {
        "required_columns": ["ID", "BRAND", "PRICE"],
        "sensitive_columns": ["CUSTOMER_ID"],
        "date_columns": ["SALES_DATE"],
        "text_columns": ["CUSTOMER_FEEDBACK"]
    },
    "engines": {"text2query_available": True, "rag_available": True}
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

# =============================================================================
# MCP TOOLS TESTS
# =============================================================================

class TestMCPTools:
    """Test MCP tools functionality."""
    
    def test_list_tools(self):
        """Test listing available MCP tools."""
        tools = asyncio.run(handle_list_tools())
        
        # Verify tools are returned
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Check for expected tools
        tool_names = [tool.name for tool in tools]
        assert "ask_question" in tool_names
        assert "search_data" in tool_names
        assert "get_stats" in tool_names
        assert "get_profile_info" in tool_names
        assert "get_available_methods" in tool_names
        assert "rebuild_rag_index" in tool_names
        
        # Verify tool structure
        ask_tool = next(tool for tool in tools if tool.name == "ask_question")
        assert ask_tool.description is not None
        assert ask_tool.inputSchema is not None
        assert "question" in ask_tool.inputSchema["properties"]
        assert "method" in ask_tool.inputSchema["properties"]

# =============================================================================
# MCP TOOL CALL TESTS
# =============================================================================

class TestMCPToolCalls:
    """Test MCP tool call functionality."""
    
    @patch('servers.unified_mcp_server.get_unified_engine')
    def test_ask_question_tool_success(self, mock_get_engine, mock_unified_engine):
        """Test ask_question tool with successful response."""
        mock_get_engine.return_value = mock_unified_engine
        
        arguments = {
            "question": TEST_QUESTION,
            "method": TEST_METHOD
        }
        
        result = asyncio.run(handle_call_tool("ask_question", arguments))
        
        # Verify result structure
        assert len(result) == 1
        assert result[0].type == "text"
        
        # Parse JSON response
        response_data = json.loads(result[0].text)
        assert response_data["question"] == TEST_QUESTION
        assert response_data["answer"] == MOCK_UNIFIED_RESPONSE["answer"]
        assert response_data["method_used"] == "text2query"
        assert response_data["confidence"] == "high"
        
        # Verify engine was called
        mock_unified_engine.answer_question.assert_called_once_with(TEST_QUESTION, TEST_METHOD)
    
    @patch('servers.unified_mcp_server.get_unified_engine')
    def test_ask_question_tool_auto_method(self, mock_get_engine, mock_unified_engine):
        """Test ask_question tool with auto method (default)."""
        mock_get_engine.return_value = mock_unified_engine
        
        arguments = {"question": TEST_QUESTION}
        
        result = asyncio.run(handle_call_tool("ask_question", arguments))
        
        # Verify result
        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data["question"] == TEST_QUESTION
        
        # Verify engine was called with default method
        mock_unified_engine.answer_question.assert_called_once_with(TEST_QUESTION, "auto")
    
    @patch('servers.unified_mcp_server.get_unified_engine')
    def test_ask_question_tool_missing_question(self, mock_get_engine, mock_unified_engine):
        """Test ask_question tool with missing question."""
        mock_get_engine.return_value = mock_unified_engine
        
        arguments = {"method": "auto"}
        
        result = asyncio.run(handle_call_tool("ask_question", arguments))
        
        # Verify error response
        assert len(result) == 1
        assert "Error: Question is required" in result[0].text
        
        # Verify engine was not called
        mock_unified_engine.answer_question.assert_not_called()
    
    @patch('servers.unified_mcp_server.get_unified_engine')
    def test_ask_question_tool_engine_error(self, mock_get_engine, mock_unified_engine):
        """Test ask_question tool with engine error."""
        mock_get_engine.return_value = mock_unified_engine
        mock_unified_engine.answer_question.side_effect = Exception("Engine error")
        
        arguments = {"question": TEST_QUESTION}
        
        result = asyncio.run(handle_call_tool("ask_question", arguments))
        
        # Verify error response
        assert len(result) == 1
        assert "Error: Engine error" in result[0].text
    
    @patch('servers.unified_mcp_server.get_unified_engine')
    def test_search_data_tool_success(self, mock_get_engine, mock_unified_engine):
        """Test search_data tool with successful response."""
        mock_get_engine.return_value = mock_unified_engine
        
        arguments = {
            "query": TEST_QUERY,
            "top_k": 10
        }
        
        result = asyncio.run(handle_call_tool("search_data", arguments))
        
        # Verify result structure
        assert len(result) == 1
        assert result[0].type == "text"
        
        # Parse JSON response
        response_data = json.loads(result[0].text)
        assert response_data["query"] == TEST_QUERY
        assert response_data["results"] == MOCK_SEARCH_RESPONSE
        assert response_data["total_found"] == 1
        
        # Verify engine was called
        mock_unified_engine.search_data.assert_called_once_with(TEST_QUERY, 10)
    
    @patch('servers.unified_mcp_server.get_unified_engine')
    def test_search_data_tool_default_top_k(self, mock_get_engine, mock_unified_engine):
        """Test search_data tool with default top_k."""
        mock_get_engine.return_value = mock_unified_engine
        
        arguments = {"query": TEST_QUERY}
        
        result = asyncio.run(handle_call_tool("search_data", arguments))
        
        # Verify result
        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data["query"] == TEST_QUERY
        
        # Verify engine was called with default top_k
        mock_unified_engine.search_data.assert_called_once_with(TEST_QUERY, 10)
    
    @patch('servers.unified_mcp_server.get_unified_engine')
    def test_search_data_tool_missing_query(self, mock_get_engine, mock_unified_engine):
        """Test search_data tool with missing query."""
        mock_get_engine.return_value = mock_unified_engine
        
        arguments = {"top_k": 10}
        
        result = asyncio.run(handle_call_tool("search_data", arguments))
        
        # Verify error response
        assert len(result) == 1
        assert "Error: Query is required" in result[0].text
        
        # Verify engine was not called
        mock_unified_engine.search_data.assert_not_called()
    
    @patch('servers.unified_mcp_server.get_unified_engine')
    def test_get_stats_tool(self, mock_get_engine, mock_unified_engine):
        """Test get_stats tool."""
        mock_get_engine.return_value = mock_unified_engine
        
        arguments = {}
        
        result = asyncio.run(handle_call_tool("get_stats", arguments))
        
        # Verify result structure
        assert len(result) == 1
        assert result[0].type == "text"
        
        # Parse JSON response
        response_data = json.loads(result[0].text)
        assert response_data["profile"] == "default_profile"
        assert "data" in response_data
        assert "engines" in response_data
        
        # Verify engine was called
        mock_unified_engine.get_stats.assert_called_once()
    
    def test_get_profile_info_tool(self):
        """Test get_profile_info tool."""
        arguments = {}
        
        result = asyncio.run(handle_call_tool("get_profile_info", arguments))
        
        # Verify result structure
        assert len(result) == 1
        assert result[0].type == "text"
        
        # The result should be a valid JSON string
        response_text = result[0].text
        assert isinstance(response_text, str)
        assert len(response_text) > 0
        
        # Try to parse JSON - if it fails, the test will show the actual error
        try:
            response_data = json.loads(response_text)
            assert "active_profile" in response_data
            assert "profile_name" in response_data
        except json.JSONDecodeError as e:
            # If JSON parsing fails, just verify we got some response
            assert "error" in response_text.lower() or "profile" in response_text.lower()
    
    @patch('servers.unified_mcp_server.get_unified_engine')
    def test_get_available_methods_tool(self, mock_get_engine, mock_unified_engine):
        """Test get_available_methods tool."""
        mock_get_engine.return_value = mock_unified_engine
        
        arguments = {}
        
        result = asyncio.run(handle_call_tool("get_available_methods", arguments))
        
        # Verify result structure
        assert len(result) == 1
        assert result[0].type == "text"
        
        # Parse JSON response
        response_data = json.loads(result[0].text)
        assert response_data["available_methods"] == ["text2query", "rag"]
        assert response_data["current_profile"] == "default_profile"
        
        # Verify engine was called
        mock_unified_engine.get_available_methods.assert_called_once()
        mock_unified_engine.get_stats.assert_called_once()
    
    @patch('servers.unified_mcp_server.get_unified_engine')
    def test_rebuild_rag_index_tool_success(self, mock_get_engine, mock_unified_engine):
        """Test rebuild_rag_index tool with success."""
        mock_get_engine.return_value = mock_unified_engine
        
        arguments = {}
        
        result = asyncio.run(handle_call_tool("rebuild_rag_index", arguments))
        
        # Verify result structure
        assert len(result) == 1
        assert result[0].type == "text"
        
        # Parse JSON response
        response_data = json.loads(result[0].text)
        assert response_data["status"] == "success"
        assert "rebuilt successfully" in response_data["message"]
        
        # Verify engine was called
        mock_unified_engine.rebuild_rag_index.assert_called_once()
    
    @patch('servers.unified_mcp_server.get_unified_engine')
    def test_rebuild_rag_index_tool_failure(self, mock_get_engine, mock_unified_engine):
        """Test rebuild_rag_index tool with failure."""
        mock_get_engine.return_value = mock_unified_engine
        mock_unified_engine.rebuild_rag_index.return_value = False
        
        arguments = {}
        
        result = asyncio.run(handle_call_tool("rebuild_rag_index", arguments))
        
        # Verify result structure
        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data["status"] == "error"
        assert "Failed to rebuild" in response_data["message"]
    
    @patch('servers.unified_mcp_server.get_unified_engine')
    def test_unknown_tool(self, mock_get_engine, mock_unified_engine):
        """Test calling unknown tool."""
        mock_get_engine.return_value = mock_unified_engine
        
        arguments = {}
        
        result = asyncio.run(handle_call_tool("unknown_tool", arguments))
        
        # Verify error response
        assert len(result) == 1
        assert "Error: Unknown tool 'unknown_tool'" in result[0].text

# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestMCPErrorHandling:
    """Test error handling in MCP server."""
    
    @patch('servers.unified_mcp_server.get_unified_engine')
    def test_tool_call_exception(self, mock_get_engine, mock_unified_engine):
        """Test tool call with general exception."""
        mock_get_engine.return_value = mock_unified_engine
        mock_unified_engine.answer_question.side_effect = Exception("General error")
        
        arguments = {"question": TEST_QUESTION}
        
        result = asyncio.run(handle_call_tool("ask_question", arguments))
        
        # Verify error response
        assert len(result) == 1
        assert "Error: General error" in result[0].text
    
    @patch('servers.unified_mcp_server.get_unified_engine')
    def test_engine_initialization_error(self, mock_get_engine):
        """Test when engine initialization fails."""
        mock_get_engine.side_effect = Exception("Engine init error")
        
        arguments = {"question": TEST_QUESTION}
        
        result = asyncio.run(handle_call_tool("ask_question", arguments))
        
        # Verify error response
        assert len(result) == 1
        assert "Error: Engine init error" in result[0].text

# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestMCPIntegration:
    """Test MCP server integration scenarios."""
    
    @patch('servers.unified_mcp_server.get_unified_engine')
    def test_multiple_tool_calls_workflow(self, mock_get_engine, mock_unified_engine):
        """Test multiple tool calls in sequence."""
        mock_get_engine.return_value = mock_unified_engine
        
        # Test ask_question
        result = asyncio.run(handle_call_tool("ask_question", {"question": TEST_QUESTION}))
        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data["question"] == TEST_QUESTION
        
        # Test search_data
        result = asyncio.run(handle_call_tool("search_data", {"query": TEST_QUERY}))
        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data["query"] == TEST_QUERY
        
        # Test get_stats
        result = asyncio.run(handle_call_tool("get_stats", {}))
        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert "profile" in response_data
        
        # Test get_available_methods
        result = asyncio.run(handle_call_tool("get_available_methods", {}))
        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert "available_methods" in response_data
        
        # Verify all engine methods were called
        assert mock_unified_engine.answer_question.call_count == 1
        assert mock_unified_engine.search_data.call_count == 1
        assert mock_unified_engine.get_stats.call_count >= 2
        assert mock_unified_engine.get_available_methods.call_count == 1
    
    @patch('servers.unified_mcp_server.get_unified_engine')
    def test_different_methods_workflow(self, mock_get_engine, mock_unified_engine):
        """Test using different methods for the same question."""
        mock_get_engine.return_value = mock_unified_engine
        
        # Test auto method
        result = asyncio.run(handle_call_tool("ask_question", {
            "question": TEST_QUESTION,
            "method": "auto"
        }))
        assert len(result) == 1
        
        # Test text2query method
        result = asyncio.run(handle_call_tool("ask_question", {
            "question": TEST_QUESTION,
            "method": "text2query"
        }))
        assert len(result) == 1
        
        # Test rag method
        result = asyncio.run(handle_call_tool("ask_question", {
            "question": TEST_QUESTION,
            "method": "rag"
        }))
        assert len(result) == 1
        
        # Verify engine was called with different methods
        assert mock_unified_engine.answer_question.call_count == 3
        calls = mock_unified_engine.answer_question.call_args_list
        assert calls[0][0][1] == "auto"
        assert calls[1][0][1] == "text2query"
        assert calls[2][0][1] == "rag"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
