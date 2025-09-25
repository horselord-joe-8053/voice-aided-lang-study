# Unified QueryRAG System

A **unified system** that combines the best of both **Text2Query** and **RAG (Retrieval-Augmented Generation)** approaches to answer natural language questions about structured data. This system intelligently routes between direct pandas DataFrame querying and vector-based retrieval to provide the most accurate and comprehensive answers.

## 🎯 Core Workflow

The system implements the requested workflow:

1. **Load test data** from the corresponding active profile to a pandas DataFrame
2. **Receive a natural language question**
3. **Try Text2Query functionality first** (direct pandas querying with intelligent method selection)
4. **If no result, fallback to RAG logic** (vector-based retrieval with LangChain)
5. **Return unified response** with method used, confidence, and sources

## 🚀 Key Features

### **Intelligent Method Selection**
- **Text2Query First**: Direct pandas DataFrame querying for structured questions
- **RAG Fallback**: Vector-based retrieval for complex analytical questions
- **Automatic Routing**: System intelligently chooses the best approach
- **Graceful Degradation**: Seamless fallback between methods

### **Profile-Agnostic Architecture**
- **Dynamic Profile Discovery**: Automatically discovers available data profiles
- **Zero-Code Profile Addition**: Add new profiles without code changes
- **Unified Configuration**: Single configuration system for both approaches
- **Schema-Agnostic Processing**: Works with any CSV data structure

### **Multiple Interfaces**
- **FastAPI REST API**: Full-featured web API with comprehensive endpoints
- **MCP Server**: Model Context Protocol integration for AI tool usage
- **Unified Response Format**: Consistent response structure across all interfaces

### **Advanced Capabilities**
- **Provider-Agnostic AI**: Support for Google Gemini, OpenAI, Anthropic
- **Automatic Data Sensitization**: Built-in sensitive data detection and anonymization
- **Report Generation**: Automatic PDF report generation for complex queries
- **Performance Tracking**: Monitor success rates and execution times

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Unified QueryRAG System                  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   FastAPI API   │    │        MCP Server              │ │
│  │                 │    │                                 │ │
│  │ • /ask          │    │ • ask_question                  │ │
│  │ • /search       │    │ • search_data                   │ │
│  │ • /stats        │    │ • get_stats                     │ │
│  │ • /profile      │    │ • get_profile_info              │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                Unified Query Engine                         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 1. Load Data from Profile → pandas DataFrame           │ │
│  │ 2. Try Text2Query (Direct Querying)                   │ │
│  │ 3. If No Result → Fallback to RAG                     │ │
│  │ 4. Return Unified Response                             │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐              ┌─────────────────────┐   │
│  │   Text2Query    │              │        RAG          │   │
│  │                 │              │                     │   │
│  │ • Traditional   │              │ • LangChain Agent   │   │
│  │ • LangChain     │              │ • Vector Store      │   │
│  │ • Direct Code   │              │ • Document Chunks   │   │
│  │ • Agent-based   │              │ • Similarity Search │   │
│  └─────────────────┘              └─────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Profile System                           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ • Dynamic Discovery  • Schema Validation               │ │
│  │ • Data Processing    • Sensitization Rules             │ │
│  │ • Provider Config    • Test Data Management            │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Directory Structure

```
ultra_plus_queryRagMcp/
├── config/                          # Configuration management
│   ├── settings.py                  # Unified system settings
│   ├── langchain_settings.py        # LangChain configuration
│   ├── logging_config.py            # Logging configuration
│   ├── profiles/                    # Profile system
│   │   ├── base_profile.py          # Base profile class
│   │   ├── profile_factory.py       # Profile discovery
│   │   ├── common_test_utils/       # Shared testing utilities
│   │   └── default_profile/         # Example profile
│   │       ├── profile_config.py    # Profile implementation
│   │       ├── provider_config.py   # Provider configuration
│   │       ├── config_api_keys.py   # API keys
│   │       └── test_data/           # Sample data
│   └── providers/                   # LLM provider system
│       ├── registry.py              # Provider factory
│       └── langchain_provider.py    # LangChain integration
├── core/                            # Core engine components
│   ├── unified_engine.py            # Main orchestration engine
│   ├── text2query/                  # Text2Query components
│   │   ├── engine.py                # Query synthesis engine
│   │   ├── synthesis/               # Synthesis methods
│   │   ├── execution/               # Query execution
│   │   ├── data/                    # Data management
│   │   └── response/                # Response building
│   └── rag/                         # RAG components
│       ├── generic_rag_agent.py     # RAG agent
│       ├── generic_data_processor.py # Data processing
│       └── generic_vector_store.py  # Vector store
├── api/                             # API layer
│   └── unified_api.py               # Unified FastAPI application
├── servers/                         # Server implementations
│   └── unified_mcp_server.py        # Unified MCP server
├── reports/                         # Report generation
│   └── generic_report_builder.py    # Report builder
├── censor_utils/                    # Data censoring
│   ├── censoring.py                 # Censoring service
│   └── future_enhanced_censoring.py # Advanced censoring
├── scripts/                         # Utility scripts
├── logs/                            # Application logs
├── requirements.txt                 # Dependencies
└── README.md                        # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to the project directory
cd ultra_plus_queryRagMcp

# Install dependencies
pip install -r requirements.txt

# Set up API keys (copy from template)
cp config/profiles/default_profile/config_api_keys_template.py config/profiles/default_profile/config_api_keys.py
# Edit config_api_keys.py with your actual API keys
```

### 2. Configuration

Edit `config/settings.py` to set your active profile:

```python
PROFILE = "default_profile"  # Change this to switch profiles
```

### 3. Run the System

#### Option A: FastAPI Server
```bash
python api/unified_api.py
# Server will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

#### Option B: MCP Server
```bash
python servers/unified_mcp_server.py
# MCP server will run on stdio for AI tool integration
```

### 4. Test the System

```bash
# Test with curl
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the average price of Samsung fridges?", "method": "auto"}'
```

## 📊 API Endpoints

### Core Endpoints

- **`POST /ask`** - Ask a question using the unified system
- **`POST /search`** - Search for relevant data chunks using RAG
- **`GET /stats`** - Get comprehensive system statistics
- **`GET /profile`** - Get current profile information
- **`GET /methods`** - Get available query methods
- **`POST /rebuild`** - Rebuild RAG vector store
- **`GET /health`** - Health check

### Request/Response Format

#### Ask Question Request
```json
{
  "question": "What is the average price of Samsung fridges?",
  "method": "auto"
}
```

#### Ask Question Response
```json
{
  "question": "What is the average price of Samsung fridges?",
  "answer": "The average price of Samsung fridges is $1,299.99...",
  "sources": [...],
  "confidence": "high",
  "method_used": "text2query",
  "execution_time": 1.23,
  "timestamp": "2024-01-15T10:30:00Z",
  "profile": "default_profile"
}
```

## 🔧 MCP Tools

The system provides the following MCP tools for AI integration:

- **`ask_question`** - Ask questions with automatic method selection
- **`search_data`** - Search for relevant data chunks
- **`get_stats`** - Get system statistics
- **`get_profile_info`** - Get profile information
- **`get_available_methods`** - List available methods
- **`rebuild_rag_index`** - Rebuild vector store

## 🎯 Method Selection Logic

The system uses intelligent heuristics to select the best approach:

### Text2Query (Direct Querying)
- **Simple filtering queries**: "Show me all Samsung fridges"
- **Aggregation queries**: "What is the average price by brand?"
- **Numerical comparisons**: "Find fridges over $1000"
- **Date range queries**: "Sales in January 2024"

### RAG (Vector Retrieval)
- **Complex analytical questions**: "What are the main complaints about noisy fridges?"
- **Semantic search**: "Find fridges with good customer satisfaction"
- **Contextual questions**: "Which brands have the best reviews?"
- **Fallback for failed Text2Query**: When direct querying yields no results

## 📈 Performance & Monitoring

The system tracks performance metrics for both approaches:

- **Success rates** for each method
- **Execution times** and performance trends
- **Method selection accuracy**
- **Fallback frequency** and reasons

## 🔒 Security & Privacy

- **Automatic Data Sensitization**: Sensitive columns are automatically detected and anonymized
- **Profile-Specific Rules**: Each profile defines its own censoring rules
- **API Key Management**: Secure API key handling through profile configurations
- **Audit Logging**: Complete logging of all operations

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=core --cov=api --cov=servers

# Run specific test categories
pytest tests/test_text2query.py
pytest tests/test_rag.py
pytest tests/test_unified_engine.py
```

## 🔄 Extensibility

### Adding New Profiles
1. Create a new directory in `config/profiles/`
2. Implement the required profile methods
3. Add test data and configuration
4. Update profile discovery

### Adding New Query Methods
1. Extend the synthesis methods in `core/text2query/synthesis/`
2. Update the unified engine to include the new method
3. Add method selection logic

### Adding New Providers
1. Implement provider interface in `config/providers/`
2. Add provider configuration
3. Update provider factory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

This unified system combines the strengths of:
- **ultra_plus_text2query**: Direct pandas DataFrame querying with intelligent method selection
- **ultra_plus_rag_mcp**: Vector-based RAG with LangChain integration

The combination provides a robust, intelligent solution that leverages the best of both approaches while maintaining profile-agnostic architecture and comprehensive testing capabilities.
