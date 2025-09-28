from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import pandas as pd
from datetime import datetime

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document

from config.langchain_settings import LangChainConfig
from config.providers.registry import ProviderConfig, LLMFactory, EmbeddingsFactory
from config.logging_config import get_logger
from .generic_data_processor import GenericDataProcessor, DataSchema
from .generic_vector_store import GenericVectorStore

logger = get_logger(__name__)

class GenericRAGAgent:
    """Generic RAG agent that works with any data structure based on configuration."""
    
    def __init__(self, config: LangChainConfig, data_schema: DataSchema, collection_name: str = "data_collection", provider_config: ProviderConfig | None = None):
        self.config = config
        self.data_schema = data_schema
        self.collection_name = collection_name
        self.llm = None
        self.embeddings = None
        self.vectorstore = None
        self.retriever = None
        self.qa_chain = None
        self.agent = None
        self.data_processor = None
        self.sensitive_mapping = {}
        
        self._initialize_components(provider_config)
    
    def _initialize_components(self, provider_config: ProviderConfig | None = None):
        """Initialize all LangChain components."""
        logger.info("Initializing generic RAG components...")
        
        # Initialize LLM and embeddings via provider-agnostic factories
        if provider_config is None:
            # Resolve from active profile to avoid leaking provider details here
            try:
                from config.settings import PROFILE
                from config.profiles.profile_factory import ProfileFactory
                profile = ProfileFactory.create_profile(PROFILE)
                provider_config = profile.get_provider_config()
            except Exception:
                # As a last resort, construct from LangChainConfig values (still generic fields)
                provider_config = ProviderConfig(
                    provider="google",  # default only if profile lookup fails
                    generation_model=self.config.generation_model,
                    embedding_model=self.config.embedding_model,
                    credentials={"api_key": self.config.google_api_key},
                    extras={"temperature": self.config.temperature, "max_tokens": self.config.max_tokens},
                )
        self.llm = LLMFactory.create(provider_config)
        self.embeddings = EmbeddingsFactory.create(provider_config)
        
        # Initialize data processor
        self.data_processor = GenericDataProcessor(
            csv_path=self.config.csv_file,
            schema=self.data_schema,
            sample_size=self.config.sample_size
        )
        
        # Initialize vector store
        self.vectorstore = GenericVectorStore(
            persist_directory=self.config.vector_store_path,
            embeddings=self.embeddings,
            collection_name=self.collection_name
        )
        
        # Load and process data
        self._load_and_process_data()
        
        # Initialize QA chain
        self._initialize_qa_chain()
        
        # Initialize agent
        self._initialize_agent()
        
        logger.info("Generic RAG components initialized successfully")
    
    def _load_and_process_data(self):
        """Load and process data, then build vector store."""
        logger.info("Loading and processing data...")
        
        # Load and process data
        df = self.data_processor.load_and_process_data()
        
        # Create documents
        documents = self.data_processor.create_documents()
        
        # Create chunks
        chunks = self.data_processor.create_chunks(documents)
        
        # Build vector store
        self.vectorstore.build_vectorstore(chunks)
        
        # Get sensitive mapping
        self.sensitive_mapping = self.data_processor.get_sensitive_mapping()
        
        logger.info(f"Data processing complete: {len(documents)} documents, {len(chunks)} chunks")
    
    def _initialize_qa_chain(self):
        """Initialize the QA chain."""
        # Create retriever
        self.retriever = self.vectorstore.get_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        # Create prompt template
        prompt_template = self._get_prompt_template()
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": prompt_template},
            return_source_documents=True
        )
        
        logger.info("QA chain initialized")
    
    def _get_prompt_template(self) -> PromptTemplate:
        """Get the prompt template for QA."""
        template = """You are a helpful assistant that answers questions based on the provided context.

Context:
{context}

Question: {question}

Please provide a comprehensive answer based on the context above. If the context doesn't contain enough information to answer the question, please say so.

Answer:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def _initialize_agent(self):
        """Initialize the agent with tools."""
        # Create tools
        tools = [
            Tool(
                name="search_data",
                description="Search through the data to find relevant information",
                func=self._search_tool
            ),
            Tool(
                name="get_stats",
                description="Get statistics about the data",
                func=self._stats_tool
            )
        ]
        
        # Create agent prompt
        agent_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant that can search through data and provide statistics. Use the available tools to answer questions."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        # Create agent
        self.agent = create_tool_calling_agent(self.llm, tools, agent_prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=tools, verbose=True)
        
        logger.info("Agent initialized")
    
    def _search_tool(self, query: str) -> str:
        """Tool for searching data."""
        try:
            results = self.vectorstore.similarity_search(query, k=3)
            if not results:
                return "No relevant information found."
            
            response = "Found relevant information:\n"
            for i, doc in enumerate(results, 1):
                response += f"{i}. {doc.page_content[:200]}...\n"
            
            return response
        except Exception as e:
            logger.error(f"Search tool error: {e}")
            return f"Error searching data: {e}"
    
    def _stats_tool(self, query: str) -> str:
        """Tool for getting statistics."""
        try:
            stats = self.data_processor.get_stats()
            vectorstore_stats = self.vectorstore.get_stats()
            
            response = "Data Statistics:\n"
            response += f"- Total records: {stats.get('total_records', 0)}\n"
            response += f"- Sensitive mappings: {stats.get('sensitive_mappings', 0)}\n"
            response += f"- Vector store documents: {vectorstore_stats.get('document_count', 0)}\n"
            
            if 'score_stats' in stats:
                score_stats = stats['score_stats']
                response += f"- Score statistics: mean={score_stats.get('mean', 0):.2f}, min={score_stats.get('min', 0)}, max={score_stats.get('max', 0)}\n"
            
            return response
        except Exception as e:
            logger.error(f"Stats tool error: {e}")
            return f"Error getting statistics: {e}"
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a question using the RAG system."""
        try:
            logger.info(f"Answering question: {question}")
            
            # Use QA chain
            result = self.qa_chain({"query": question})
            
            # Extract sources
            sources = []
            for doc in result.get("source_documents", []):
                source = {
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                }
                sources.append(source)
            
            # Determine confidence based on source quality
            confidence = "high" if len(sources) >= 3 else "medium" if len(sources) >= 1 else "low"
            
            return {
                "answer": result["result"],
                "sources": sources,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                "answer": f"Error processing question: {e}",
                "sources": [],
                "confidence": "low",
                "timestamp": datetime.now().isoformat()
            }
    
    def search_relevant_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant chunks."""
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=top_k)
            
            chunks = []
            for doc, score in results:
                chunk = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity": float(score)
                }
                chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error searching chunks: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        try:
            data_stats = self.data_processor.get_stats()
            vectorstore_stats = self.vectorstore.get_stats()
            
            return {
                "vectorstore": vectorstore_stats,
                "data": data_stats,
                "sensitization": {
                    "total_mappings": len(self.sensitive_mapping)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "vectorstore": {"status": "error", "error": str(e)},
                "data": {"status": "error", "error": str(e)},
                "sensitization": {"total_mappings": 0}
            }
    
    def rebuild_vectorstore(self) -> bool:
        """Rebuild the vector store."""
        try:
            logger.info("Rebuilding vector store...")
            
            # Reload and process data
            df = self.data_processor.load_and_process_data()
            documents = self.data_processor.create_documents()
            chunks = self.data_processor.create_chunks(documents)
            
            # Rebuild vector store
            success = self.vectorstore.rebuild_vectorstore(chunks)
            
            if success:
                # Reinitialize QA chain
                self._initialize_qa_chain()
                logger.info("Vector store rebuilt successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Error rebuilding vector store: {e}")
            return False
    
    def get_sensitization_stats(self) -> Dict[str, Any]:
        """Get sensitization statistics."""
        return {
            "total_mappings": len(self.sensitive_mapping),
            "mapping_sample": dict(list(self.sensitive_mapping.items())[:5])  # Show first 5 mappings
        }
