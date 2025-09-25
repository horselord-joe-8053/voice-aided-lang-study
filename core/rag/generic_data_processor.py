import hashlib
from typing import List, Dict, Any, cast, Optional
from pathlib import Path
import pandas as pd
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from config.logging_config import get_logger

logger = get_logger(__name__)

class DataSchema:
    """Configuration for data processing schema."""
    
    def __init__(
        self,
        required_columns: List[str],
        sensitive_columns: List[str] = None,
        date_columns: List[str] = None,
        text_columns: List[str] = None,
        metadata_columns: List[str] = None,
        id_column: str = None,
        score_column: str = None
    ):
        self.required_columns = required_columns
        self.sensitive_columns = sensitive_columns or []
        self.date_columns = date_columns or []
        self.text_columns = text_columns or []
        self.metadata_columns = metadata_columns or []
        self.id_column = id_column
        self.score_column = score_column

class GenericDataProcessor:
    """Generic data processor that works with any CSV structure based on schema configuration."""
    
    def __init__(self, csv_path: str, schema: DataSchema, sample_size: int = None):
        self.csv_path = csv_path
        self.schema = schema
        self.sample_size = sample_size
        self.sensitive_mapping: Dict[str, str] = {}
        self.df = None
        self.df_sensitized = None
        
    def load_and_process_data(self) -> pd.DataFrame:
        """Load and clean CSV data based on schema."""
        df = pd.read_csv(self.csv_path)
        
        # Validate required columns
        missing = set(self.schema.required_columns) - set(df.columns)
        if missing:
            raise ValueError(f"CSV missing required columns: {missing}")
        
        # Apply sampling if specified
        if self.sample_size and len(df) > self.sample_size:
            logger.info(f"Sampling {self.sample_size} records from {len(df)} total records")
            # Sort by date column if available
            if self.schema.date_columns:
                date_col = self.schema.date_columns[0]  # Use first date column
                if date_col in df.columns:
                    df = df.sort_values(date_col, ascending=False)
            df = df.head(self.sample_size)
            logger.info(f"Using {len(df)} most recent records for processing")
        
        df = self._clean_data(df)
        self.df = df
        self.df_sensitized = self._sensify_data(df.copy())
        return self.df_sensitized
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize data."""
        # Convert date columns to datetime
        for date_col in self.schema.date_columns:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        # Clean text columns
        for text_col in self.schema.text_columns:
            if text_col in df.columns:
                df[text_col] = df[text_col].astype(str).fillna('')
        
        # Clean numeric columns (score column)
        if self.schema.score_column and self.schema.score_column in df.columns:
            df[self.schema.score_column] = pd.to_numeric(df[self.schema.score_column], errors='coerce')
        
        return df
    
    def _sensify_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply data sensitization to sensitive columns."""
        for col in self.schema.sensitive_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: self._sensify_value(x, col))
        return df
    
    def _sensify_value(self, value: Any, column_name: str) -> str:
        """Sensitize a single value."""
        if pd.isna(value) or value == '':
            return ''
        
        value_str = str(value)
        if value_str in self.sensitive_mapping:
            return self.sensitive_mapping[value_str]
        
        # Create hash-based sensitized value
        hash_obj = hashlib.md5(value_str.encode())
        hash_hex = hash_obj.hexdigest()[:8].upper()
        sensitized = f"{column_name.upper()}_{hash_hex}"
        
        self.sensitive_mapping[value_str] = sensitized
        return sensitized
    
    def create_documents(self) -> List[Document]:
        """Create LangChain documents from processed data."""
        if self.df_sensitized is None:
            raise ValueError("Data must be loaded and processed first")
        
        documents = []
        for _, row in self.df_sensitized.iterrows():
            # Create document content from text columns
            content_parts = []
            for text_col in self.schema.text_columns:
                if text_col in row and pd.notna(row[text_col]) and str(row[text_col]).strip():
                    content_parts.append(f"{text_col}: {row[text_col]}")
            
            # Add metadata
            metadata = {}
            for meta_col in self.schema.metadata_columns:
                if meta_col in row and pd.notna(row[meta_col]):
                    metadata[meta_col.lower()] = str(row[meta_col])
            
            # Add ID if available
            if self.schema.id_column and self.schema.id_column in row:
                metadata['id'] = str(row[self.schema.id_column])
            
            # Add score if available
            if self.schema.score_column and self.schema.score_column in row:
                metadata['score'] = float(row[self.schema.score_column]) if pd.notna(row[self.schema.score_column]) else None
            
            # Create document
            if content_parts:
                content = " | ".join(content_parts)
                doc = Document(page_content=content, metadata=metadata)
                documents.append(doc)
        
        logger.info(f"Created {len(documents)} documents from {len(self.df_sensitized)} records")
        return documents
    
    def create_chunks(self, documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
        """Split documents into chunks."""
        if not documents:
            return []
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " | ", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks
    
    def get_sensitive_mapping(self) -> Dict[str, str]:
        """Get the sensitive data mapping."""
        return self.sensitive_mapping.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        if self.df is None:
            return {"status": "not_processed"}
        
        stats = {
            "total_records": len(self.df),
            "sensitive_mappings": len(self.sensitive_mapping),
            "columns": list(self.df.columns)
        }
        
        # Add score statistics if available
        if self.schema.score_column and self.schema.score_column in self.df.columns:
            score_data = self.df[self.schema.score_column].dropna()
            if len(score_data) > 0:
                stats["score_stats"] = {
                    "count": len(score_data),
                    "mean": float(score_data.mean()),
                    "min": float(score_data.min()),
                    "max": float(score_data.max())
                }
        
        return stats
