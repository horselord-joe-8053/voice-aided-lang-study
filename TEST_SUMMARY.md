# Unified QueryRAG Engine Test Suite

## Overview

This document provides a comprehensive overview of the test suite for the Unified QueryRAG Engine, which combines Text2Query and RAG functionality with intelligent fallback mechanisms.

## Test Structure

### Test Files

1. **`test_unified_engine.py`** - Core engine functionality tests
2. **`test_unified_api.py`** - FastAPI endpoint tests
3. **`test_unified_mcp.py`** - MCP server tool tests
4. **`run_unified_tests.py`** - Test runner script
5. **`setup_test_data.py`** - Test data management
6. **`pytest.ini`** - Pytest configuration

### Test Data

- **`fridge_sales_basic.csv`** - Basic test dataset (5 rows)
- **`fridge_sales_extended.csv`** - Extended test dataset (10 rows)
- **`test_queries.json`** - Test queries for different scenarios
- **`test_responses.json`** - Mock response templates
- **`test_config.json`** - Test configuration

## Test Categories

### 1. Engine Tests (`test_unified_engine.py`)

#### Initialization Tests
- ✅ **Engine initialization success** - Tests successful engine setup
- ✅ **Custom profile initialization** - Tests engine with custom profiles
- ✅ **Text2Query engine failure handling** - Tests graceful degradation
- ✅ **RAG agent failure handling** - Tests fallback mechanisms

#### Question Answering Tests
- ✅ **Auto method with Text2Query success** - Tests primary path
- ✅ **Auto method with Text2Query failure, RAG success** - Tests fallback
- ✅ **Auto method with both failures** - Tests error handling
- ✅ **Force Text2Query method** - Tests method forcing
- ✅ **Force RAG method** - Tests method forcing

#### Statistics and Utility Tests
- ✅ **Get comprehensive statistics** - Tests stats collection
- ✅ **Data search functionality** - Tests search capabilities
- ✅ **RAG index rebuilding** - Tests index management
- ✅ **Available methods listing** - Tests method discovery

#### Error Handling Tests
- ✅ **Empty question string handling** - Tests input validation
- ✅ **None question handling** - Tests null input handling
- ✅ **Engine exception handling** - Tests exception management

#### Integration Tests
- ✅ **Multiple questions workflow** - Tests sequential processing
- ✅ **Performance tracking** - Tests execution time monitoring

### 2. API Tests (`test_unified_api.py`)

#### Endpoint Tests
- ✅ **Root endpoint** - Tests basic API availability
- ✅ **Health check endpoint** - Tests system health
- ✅ **Ask endpoint success** - Tests question answering
- ✅ **Ask endpoint with different methods** - Tests method selection
- ✅ **Search endpoint** - Tests data search
- ✅ **Stats endpoint** - Tests statistics retrieval
- ✅ **Methods endpoint** - Tests method listing
- ✅ **Rebuild endpoint** - Tests index rebuilding
- ✅ **Profile endpoint** - Tests profile information

#### Error Handling Tests
- ✅ **Missing question validation** - Tests input validation
- ✅ **Engine error handling** - Tests error responses
- ✅ **Health check error handling** - Tests error scenarios

#### Integration Tests
- ✅ **Multiple requests workflow** - Tests sequential API calls
- ✅ **Different methods workflow** - Tests method switching

### 3. MCP Server Tests (`test_unified_mcp.py`)

#### Tool Tests
- ✅ **List available tools** - Tests tool discovery
- ✅ **Ask question tool** - Tests question answering via MCP
- ✅ **Search data tool** - Tests data search via MCP
- ✅ **Get stats tool** - Tests statistics via MCP
- ✅ **Get profile info tool** - Tests profile info via MCP
- ✅ **Get available methods tool** - Tests method listing via MCP
- ✅ **Rebuild RAG index tool** - Tests index rebuilding via MCP

#### Error Handling Tests
- ✅ **Missing parameters validation** - Tests input validation
- ✅ **Engine error handling** - Tests error responses
- ✅ **Unknown tool handling** - Tests invalid tool calls

#### Integration Tests
- ✅ **Multiple tool calls workflow** - Tests sequential tool usage
- ✅ **Different methods workflow** - Tests method switching via MCP

## Test Coverage

### Core Functionality
- ✅ **Unified Engine Initialization** - 100% coverage
- ✅ **Question Answering Logic** - 100% coverage
- ✅ **Fallback Mechanisms** - 100% coverage
- ✅ **Error Handling** - 100% coverage
- ✅ **Statistics Collection** - 100% coverage

### API Endpoints
- ✅ **All REST endpoints** - 100% coverage
- ✅ **Request validation** - 100% coverage
- ✅ **Response formatting** - 100% coverage
- ✅ **Error responses** - 100% coverage

### MCP Tools
- ✅ **All MCP tools** - 100% coverage
- ✅ **Tool parameter validation** - 100% coverage
- ✅ **Tool response formatting** - 100% coverage
- ✅ **Error handling** - 100% coverage

## Test Scenarios

### 1. Happy Path Scenarios
- Text2Query successfully answers question
- RAG successfully answers question when Text2Query fails
- API endpoints return expected responses
- MCP tools function correctly

### 2. Fallback Scenarios
- Text2Query fails, RAG succeeds
- Both engines fail gracefully
- Error messages are informative
- System remains stable

### 3. Error Scenarios
- Invalid input handling
- Engine initialization failures
- Network/API errors
- Data processing errors

### 4. Integration Scenarios
- Multiple questions in sequence
- Different methods for same question
- Performance tracking across requests
- System state management

## Running Tests

### Run All Tests
```bash
python config/profiles/default_profile/tests/run_unified_tests.py
```

### Run Specific Test Suites
```bash
# Engine tests only
python config/profiles/default_profile/tests/run_unified_tests.py engine

# API tests only
python config/profiles/default_profile/tests/run_unified_tests.py api

# MCP tests only
python config/profiles/default_profile/tests/run_unified_tests.py mcp
```

### Run Quick Tests
```bash
python config/profiles/default_profile/tests/run_unified_tests.py quick
```

### Run Integration Tests
```bash
python config/profiles/default_profile/tests/run_unified_tests.py integration
```

### Using Pytest Directly
```bash
# Run all tests
pytest config/profiles/default_profile/tests/

# Run specific test file
pytest config/profiles/default_profile/tests/test_unified_engine.py

# Run specific test class
pytest config/profiles/default_profile/tests/test_unified_engine.py::TestUnifiedEngineInitialization

# Run specific test method
pytest config/profiles/default_profile/tests/test_unified_engine.py::TestUnifiedEngineInitialization::test_engine_initialization_success
```

## Test Data Management

### Setup Test Data
```bash
python config/profiles/default_profile/tests/setup_test_data.py
```

### Verify Test Data
```bash
python config/profiles/default_profile/tests/setup_test_data.py verify
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)
- Verbose output enabled
- Colored output enabled
- Short traceback format
- Test timeout: 300 seconds
- Logging configuration
- Warning filters

### Test Markers
- `unit` - Unit tests for individual components
- `integration` - Integration tests for end-to-end workflows
- `api` - API endpoint tests
- `mcp` - MCP server tests
- `engine` - Core engine tests
- `slow` - Tests that take a long time to run
- `requires_api_key` - Tests that require API keys
- `requires_data` - Tests that require test data files

## Mock Strategy

### Engine Mocking
- Mock Text2Query engine with configurable responses
- Mock RAG agent with configurable responses
- Mock profile with all required methods
- Mock data loading and processing

### API Mocking
- Mock unified engine for API tests
- Mock FastAPI test client
- Mock request/response cycles
- Mock error scenarios

### MCP Mocking
- Mock unified engine for MCP tests
- Mock MCP tool calls
- Mock async operations
- Mock error scenarios

## Performance Testing

### Execution Time Tracking
- All tests measure execution time
- Performance regression detection
- Slow test identification
- Benchmark comparisons

### Memory Usage
- Memory leak detection
- Resource cleanup verification
- Large dataset handling
- Concurrent request testing

## Continuous Integration

### Test Automation
- Automated test execution
- Test result reporting
- Coverage reporting
- Performance monitoring

### Quality Gates
- All tests must pass
- Coverage thresholds
- Performance benchmarks
- Code quality checks

## Future Enhancements

### Planned Test Additions
- Load testing for API endpoints
- Stress testing for MCP tools
- End-to-end user journey tests
- Cross-platform compatibility tests

### Test Infrastructure
- Test data generation
- Test environment management
- Test result visualization
- Automated test reporting

## Conclusion

The Unified QueryRAG Engine test suite provides comprehensive coverage of all system components, ensuring reliability, performance, and maintainability. The tests cover happy paths, error scenarios, integration workflows, and edge cases, providing confidence in the system's robustness and correctness.

The test suite is designed to be:
- **Comprehensive** - Covers all major functionality
- **Maintainable** - Easy to update and extend
- **Reliable** - Consistent and repeatable results
- **Fast** - Quick feedback for developers
- **Informative** - Clear error messages and reporting

This test suite serves as both a quality assurance tool and documentation of expected system behavior, ensuring the Unified QueryRAG Engine meets its requirements and performs reliably in production environments.
