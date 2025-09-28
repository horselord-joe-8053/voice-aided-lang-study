import pytest
import tempfile
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from config.langchain_settings import LangChainConfig
from config.profiles.profile_factory import ProfileFactory
from rag.generic_data_processor import GenericDataProcessor, DataSchema
from rag.generic_vector_store import GenericVectorStore
from rag.generic_rag_agent import GenericRAGAgent

# Import shared test utilities
from config.profiles.common_test_utils import (
    create_mock_llm,
    create_mock_embeddings,
    create_mock_rag_agent,
    create_test_csv,
    cleanup_temp_file,
    BaseRAGAgentTest,
    BaseVectorStoreTest,
    BaseDataProcessorTest,
    MOCK_LLM_RESPONSE,
    MOCK_EMBEDDING
)

# =============================================================================
# TEST CONSTANTS AND SHARED DATA
# =============================================================================

# Default Profile specific test data (fridge sales)
DEFAULT_TEST_DATA = {
    "customer_id": "CUST001",
    "fridge_model": "RF28K9070SG",
    "brand": "Samsung",
    "capacity_liters": 28,
    "price": 1299.99,
    "store_name": "New York Store",
    "customer_feedback": "Absolutely thrilled with this purchase!"
}

# CSV headers for default profile (fridge sales)
DEFAULT_CSV_HEADERS = [
    "ID", "CUSTOMER_ID", "FRIDGE_MODEL", "BRAND", "CAPACITY_LITERS", 
    "PRICE", "SALES_DATE", "STORE_NAME", "STORE_ADDRESS", "CUSTOMER_FEEDBACK"
]

# Sample CSV row data
SAMPLE_CSV_ROW = [
    "F001", DEFAULT_TEST_DATA["customer_id"], DEFAULT_TEST_DATA["fridge_model"],
    DEFAULT_TEST_DATA["brand"], str(DEFAULT_TEST_DATA["capacity_liters"]),
    str(DEFAULT_TEST_DATA["price"]), "2024-01-15", DEFAULT_TEST_DATA["store_name"],
    "123 Broadway, New York, NY 10001", DEFAULT_TEST_DATA["customer_feedback"]
]

# Mock responses (using shared constants)
MOCK_DOCUMENT_CONTENT = f"Customer {DEFAULT_TEST_DATA['customer_id']} purchased {DEFAULT_TEST_DATA['fridge_model']} for ${DEFAULT_TEST_DATA['price']}"

class TestGenericDataProcessor:
    """Test the generic data processor with default profile data (fridge sales)."""

    def create_test_csv(self, rows=None, headers=None):
        """Helper to create a temporary CSV file."""
        if headers is None:
            headers = DEFAULT_CSV_HEADERS
        if rows is None:
            rows = [SAMPLE_CSV_ROW]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(",".join(f'"{header}"' for header in headers) + "\n")
            for row in rows:
                f.write(",".join(f'"{str(cell)}"' for cell in row) + "\n")
            return f.name

    def get_default_data_schema(self):
        """Get default profile data schema (fridge sales)."""
        return DataSchema(
            required_columns=DEFAULT_CSV_HEADERS,
            sensitive_columns=['CUSTOMER_ID'],
            date_columns=['SALES_DATE'],
            text_columns=['CUSTOMER_FEEDBACK'],
            metadata_columns=['ID', 'FRIDGE_MODEL', 'BRAND', 'CAPACITY_LITERS', 'PRICE', 'STORE_NAME', 'STORE_ADDRESS'],
            id_column='ID',
            score_column='PRICE'  # Use price as the "score" for fridge sales
        )

    def test_data_processor_initialization(self):
        """Test data processor initialization."""
        temp_csv = self.create_test_csv()
        try:
            schema = self.get_default_data_schema()
            processor = GenericDataProcessor(temp_csv, schema)
            assert processor.csv_path == temp_csv
            assert processor.schema == schema
            assert "ID" in processor.schema.required_columns
            assert "PRICE" in processor.schema.required_columns
        finally:
            cleanup_temp_file(temp_csv)

    def test_data_processor_initialization_invalid_file(self):
        """Test data processor initialization with invalid file."""
        schema = self.get_default_data_schema()
        processor = GenericDataProcessor("nonexistent_file.csv", schema)
        with pytest.raises((FileNotFoundError, pd.errors.EmptyDataError)):
            processor.load_and_process_data()

    def test_data_loading_and_processing(self):
        """Test data loading and processing with default profile data (fridge sales)."""
        temp_csv = self.create_test_csv()
        
        try:
            schema = self.get_default_data_schema()
            processor = GenericDataProcessor(temp_csv, schema)
            df = processor.load_and_process_data()
            
            assert len(df) == 1
            assert str(df.iloc[0]['ID']) == "F001"
            assert df.iloc[0]['PRICE'] == DEFAULT_TEST_DATA["price"]
            # Customer ID will be sensitized
            assert 'CUSTOMER_ID_' in df.iloc[0]['CUSTOMER_ID']
            
            # Check sensitization
            assert 'CUSTOMER_ID_' in df.iloc[0]['CUSTOMER_ID']  # Should be sensitized
        finally:
            cleanup_temp_file(temp_csv)

    def test_data_processing_multiple_rows(self):
        """Test data processing with multiple rows."""
        rows = [
            SAMPLE_CSV_ROW,
            ["F002", "CUST002", "GNE27JYMFS", "GE", "27", "899.99", "2024-01-16", "Chicago Store", "456 Michigan Ave, Chicago, IL 60601", "It's a fridge."]
        ]
        temp_csv = self.create_test_csv(rows=rows)
        
        try:
            schema = self.get_default_data_schema()
            processor = GenericDataProcessor(temp_csv, schema)
            df = processor.load_and_process_data()
            
            assert len(df) == 2
            assert str(df.iloc[0]['ID']) == "F001"
            assert str(df.iloc[1]['ID']) == "F002"
            
            # Check that both customer IDs are sensitized
            assert 'CUSTOMER_ID_' in df.iloc[0]['CUSTOMER_ID']
            assert 'CUSTOMER_ID_' in df.iloc[1]['CUSTOMER_ID']
            # And they should be different
            assert df.iloc[0]['CUSTOMER_ID'] != df.iloc[1]['CUSTOMER_ID']
        finally:
            cleanup_temp_file(temp_csv)

    def test_document_creation(self):
        """Test document creation from processed data."""
        temp_csv = self.create_test_csv()
        
        try:
            schema = self.get_default_data_schema()
            processor = GenericDataProcessor(temp_csv, schema)
            df = processor.load_and_process_data()
            documents = processor.create_documents()
            
            assert len(documents) == 1
            document = documents[0]
            
            # Check document content contains text fields
            assert DEFAULT_TEST_DATA["customer_feedback"] in document.page_content
            
            # Check metadata
            assert 'id' in document.metadata
            assert 'price' in document.metadata
            assert document.metadata['id'] == "F001"
            assert float(document.metadata['price']) == DEFAULT_TEST_DATA["price"]
            
            # Check sensitized fields in metadata
            if 'customer_id' in document.metadata:
                assert 'CUSTOMER_ID_' in document.metadata['customer_id']
        finally:
            cleanup_temp_file(temp_csv)

    def test_document_creation_multiple_documents(self):
        """Test document creation with multiple records."""
        rows = [
            SAMPLE_CSV_ROW,
            ["F002", "CUST002", "GNE27JYMFS", "GE", "27", "899.99", "2024-01-16", "Chicago Store", "456 Michigan Ave, Chicago, IL 60601", "It's a fridge."]
        ]
        temp_csv = self.create_test_csv(rows=rows)
        
        try:
            schema = self.get_default_data_schema()
            processor = GenericDataProcessor(temp_csv, schema)
            df = processor.load_and_process_data()
            documents = processor.create_documents()
            
            assert len(documents) == 2
            
            # Check both documents have different content
            assert documents[0].page_content != documents[1].page_content
            assert documents[0].metadata['id'] != documents[1].metadata['id']
        finally:
            cleanup_temp_file(temp_csv)

    def test_chunk_creation(self):
        """Test chunk creation from documents."""
        temp_csv = self.create_test_csv()
        
        try:
            schema = self.get_default_data_schema()
            processor = GenericDataProcessor(temp_csv, schema)
            df = processor.load_and_process_data()
            documents = processor.create_documents()
            chunks = processor.create_chunks(documents)
            
            assert len(chunks) >= 1  # At least one chunk
            assert all(isinstance(chunk, type(documents[0])) for chunk in chunks)
        finally:
            cleanup_temp_file(temp_csv)

    def test_sensitive_mapping(self):
        """Test sensitive data mapping functionality."""
        temp_csv = self.create_test_csv()
        
        try:
            schema = self.get_default_data_schema()
            processor = GenericDataProcessor(temp_csv, schema)
            df = processor.load_and_process_data()
            mapping = processor.get_sensitive_mapping()
            
            # Should have mappings for sensitive columns
            assert len(mapping) > 0
            # Original values should be in mapping keys
            assert DEFAULT_TEST_DATA["customer_id"] in mapping
        finally:
            cleanup_temp_file(temp_csv)

    def test_get_stats(self):
        """Test getting processing statistics."""
        temp_csv = self.create_test_csv()
        
        try:
            schema = self.get_default_data_schema()
            processor = GenericDataProcessor(temp_csv, schema)
            df = processor.load_and_process_data()
            stats = processor.get_stats()
            
            assert stats["total_records"] == 1
            assert stats["sensitive_mappings"] > 0
            assert "score_stats" in stats
            assert stats["score_stats"]["mean"] == DEFAULT_TEST_DATA["price"]
        finally:
            cleanup_temp_file(temp_csv)

class TestGenericVectorStore(BaseVectorStoreTest):
    """Test the generic vector store."""

    def test_vector_store_initialization(self):
        """Test vector store initialization."""
        self._test_vector_store_initialization(GenericVectorStore, "/tmp/test", "test_collection")

    def test_vector_store_initialization_with_custom_collection(self):
        """Test vector store initialization with custom collection name."""
        self._test_vector_store_initialization_with_custom_collection(GenericVectorStore, "/tmp/test")

    def test_get_stats_not_initialized(self):
        """Test getting stats when vector store is not initialized."""
        self._test_get_stats_not_initialized(GenericVectorStore, "/tmp/test")

class TestGenericRAGAgent(BaseRAGAgentTest):
    """Test the generic RAG agent with default profile data (fridge sales)."""
    
    def get_default_data_schema(self):
        """Get default profile data schema (fridge sales)."""
        return DataSchema(
            required_columns=DEFAULT_CSV_HEADERS,
            sensitive_columns=['CUSTOMER_ID'],
            date_columns=['SALES_DATE'],
            text_columns=['CUSTOMER_FEEDBACK'],
            metadata_columns=['ID', 'FRIDGE_MODEL', 'BRAND', 'CAPACITY_LITERS', 'PRICE', 'STORE_NAME', 'STORE_ADDRESS'],
            id_column='ID',
            score_column='PRICE'  # Use price as the "score" for fridge sales
        )

    def create_test_csv(self):
        """Helper to create a temporary CSV file."""
        return create_test_csv(DEFAULT_CSV_HEADERS, [SAMPLE_CSV_ROW])

    @pytest.mark.slow
    @pytest.mark.external
    @patch('config.providers.registry.ChatGoogleGenerativeAI')
    @patch('config.providers.registry.GoogleGenerativeAIEmbeddings')
    def test_rag_agent_initialization_success(self, mock_embeddings, mock_llm):
        if os.getenv('RUN_EXTERNAL') != '1':
            pytest.skip('external smoke test disabled (set RUN_EXTERNAL=1 to enable)')
        """Test successful RAG agent initialization."""
        temp_csv = self.create_test_csv()
        
        try:
            mock_llm.return_value = create_mock_llm()
            mock_embeddings.return_value = create_mock_embeddings()
            
            # Create a mock config object
            config = Mock()
            config.csv_file = temp_csv
            config.vector_store_path = '/tmp/test_vectorstore'
            config.generation_model = 'gemini-pro'
            config.embedding_model = 'embedding-001'
            config.temperature = 0.7
            config.max_tokens = 1000
            config.sample_size = None
            
            schema = self.get_default_data_schema()
            agent = GenericRAGAgent(config, schema, "test_collection")
            assert agent.config == config
            assert agent.data_schema == schema
            assert agent.collection_name == "test_collection"
            assert agent.llm is not None
            assert agent.embeddings is not None
            assert agent.data_processor is not None
            assert agent.vectorstore is not None
        finally:
            cleanup_temp_file(temp_csv)

    @pytest.mark.skip(reason="Complex mocking issues with LangChain validation")
    @pytest.mark.slow
    @pytest.mark.external
    @patch('config.providers.registry.ChatGoogleGenerativeAI')
    @patch('config.providers.registry.GoogleGenerativeAIEmbeddings')
    def test_rag_agent_answer_question(self, mock_embeddings, mock_llm):
        if os.getenv('RUN_EXTERNAL') != '1':
            pytest.skip('external smoke test disabled (set RUN_EXTERNAL=1 to enable)')
        """Test RAG agent question answering."""
        temp_csv = self.create_test_csv()
        
        try:
            mock_llm.return_value = create_mock_llm()
            mock_embeddings.return_value = create_mock_embeddings()
            
            # Create a mock config object
            config = Mock()
            config.csv_file = temp_csv
            config.vector_store_path = '/tmp/test_vectorstore'
            config.generation_model = 'gemini-pro'
            config.embedding_model = 'embedding-001'
            config.temperature = 0.7
            config.max_tokens = 1000
            config.sample_size = None
            
            schema = self.get_default_data_schema()
            agent = GenericRAGAgent(config, schema, "test_collection")
            
            # Mock the QA chain
            mock_qa_chain = Mock()
            mock_qa_chain.return_value = {
                "result": "Test answer about fridge sales",
                "source_documents": []
            }
            agent.qa_chain = mock_qa_chain
            
            result = agent.answer_question("What is the average price of fridges?")
            
            assert "answer" in result
            assert "sources" in result
            assert "confidence" in result
            assert "timestamp" in result
        finally:
            cleanup_temp_file(temp_csv)

    @pytest.mark.skip(reason="Complex mocking issues with LangChain validation")
    @pytest.mark.slow
    @pytest.mark.external
    @patch('config.providers.registry.ChatGoogleGenerativeAI')
    @patch('config.providers.registry.GoogleGenerativeAIEmbeddings')
    def test_rag_agent_search_relevant_chunks(self, mock_embeddings, mock_llm):
        if os.getenv('RUN_EXTERNAL') != '1':
            pytest.skip('external smoke test disabled (set RUN_EXTERNAL=1 to enable)')
        """Test RAG agent chunk searching."""
        temp_csv = self.create_test_csv()
        
        try:
            mock_llm.return_value = create_mock_llm()
            mock_embeddings.return_value = create_mock_embeddings()
            
            # Create a mock config object
            config = Mock()
            config.csv_file = temp_csv
            config.vector_store_path = '/tmp/test_vectorstore'
            config.generation_model = 'gemini-pro'
            config.embedding_model = 'embedding-001'
            config.temperature = 0.7
            config.max_tokens = 1000
            config.sample_size = None
            
            schema = self.get_default_data_schema()
            agent = GenericRAGAgent(config, schema, "test_collection")
            
            # Mock the vector store
            mock_vectorstore = Mock()
            mock_vectorstore.similarity_search_with_score = Mock(return_value=[])
            agent.vectorstore = mock_vectorstore
            
            results = agent.search_relevant_chunks("customer feedback", 5)
            
            assert isinstance(results, list)
        finally:
            cleanup_temp_file(temp_csv)

    @pytest.mark.skip(reason="Complex mocking issues with LangChain validation")
    @pytest.mark.slow
    @pytest.mark.external
    @patch('config.providers.registry.ChatGoogleGenerativeAI')
    @patch('config.providers.registry.GoogleGenerativeAIEmbeddings')
    def test_rag_agent_get_stats(self, mock_embeddings, mock_llm):
        if os.getenv('RUN_EXTERNAL') != '1':
            pytest.skip('external smoke test disabled (set RUN_EXTERNAL=1 to enable)')
        """Test RAG agent statistics."""
        temp_csv = self.create_test_csv()
        
        try:
            mock_llm.return_value = create_mock_llm()
            mock_embeddings.return_value = create_mock_embeddings()
            
            # Create a mock config object
            config = Mock()
            config.csv_file = temp_csv
            config.vector_store_path = '/tmp/test_vectorstore'
            config.generation_model = 'gemini-pro'
            config.embedding_model = 'embedding-001'
            config.temperature = 0.7
            config.max_tokens = 1000
            config.sample_size = None
            
            schema = self.get_default_data_schema()
            agent = GenericRAGAgent(config, schema, "test_collection")
            
            stats = agent.get_stats()
            
            assert "vectorstore" in stats
            assert "data" in stats
            assert "sensitization" in stats
        finally:
            cleanup_temp_file(temp_csv)
