#!/usr/bin/env python3
"""
Default profile for generic data processing.
"""

from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

from ..base_profile import BaseProfile, ColumnDefinition, SensitizationRule, DocumentTemplate
from rag.generic_data_processor import DataSchema
from reports.generic_report_builder import ReportConfig


class DefaultProfile(BaseProfile):
    """Default profile for generic data processing."""
    
    def _initialize_profile(self):
        """Initialize default profile settings."""
        # Profile identification
        self.profile_name = "default_profile"
        
        # Language settings
        self.language = "en-US"
        self.locale = "en_US"
        
        # File paths
        self.data_file_path = str(Path(__file__).parent / "test_data" / "fridge_sales_without_rating.csv")
        self.test_data_path = str(Path(__file__).parent / "test_data")
        
        # Define required columns for fridge sales data
        self.required_columns = [
            'ID', 'CUSTOMER_ID', 'FRIDGE_MODEL', 'BRAND', 'CAPACITY_LITERS', 
            'PRICE', 'SALES_DATE', 'STORE_NAME', 'STORE_ADDRESS', 'CUSTOMER_FEEDBACK'
        ]
        
        # Define column definitions
        self.column_definitions = {
            'ID': ColumnDefinition('ID', 'string', True, "Product ID"),
            'CUSTOMER_ID': ColumnDefinition('CUSTOMER_ID', 'string', True, "Customer ID", sensitive=True),
            'FRIDGE_MODEL': ColumnDefinition('FRIDGE_MODEL', 'string', True, "Fridge Model"),
            'BRAND': ColumnDefinition('BRAND', 'string', True, "Brand"),
            'CAPACITY_LITERS': ColumnDefinition('CAPACITY_LITERS', 'int', True, "Capacity in Liters"),
            'PRICE': ColumnDefinition('PRICE', 'float', True, "Price"),
            'SALES_DATE': ColumnDefinition('SALES_DATE', 'datetime', True, "Sales Date"),
            'STORE_NAME': ColumnDefinition('STORE_NAME', 'string', True, "Store Name"),
            'STORE_ADDRESS': ColumnDefinition('STORE_ADDRESS', 'string', True, "Store Address"),
            'CUSTOMER_FEEDBACK': ColumnDefinition('CUSTOMER_FEEDBACK', 'string', True, "Customer Feedback", text_field=True)
        }
        
        # Define text columns
        self.text_columns = ['CUSTOMER_FEEDBACK']
        
        # Define sensitive columns
        self.sensitive_columns = ['CUSTOMER_ID']
        
        # Define sensitization rules (none by default)
        self.sensitization_rules = {}
        
        # Define document template (generic English)
        self.document_template = DocumentTemplate(
            template=(
                "Record {id} has a score of {score}. "
                "Date: {date}. "
                "Description: {description}. "
                "Category: {category}."
            ),
            metadata_fields=[
                "id", "score", "date", "category"
            ]
        )
    
    def get_prompt_template(self) -> str:
        """Get English prompt template for the RAG system."""
        return """
        You are a data analysis assistant.
        Your role is to answer questions based on the provided data.

        Context information:
        {context}

        Question: {question}

        Instructions:
        1. Use only the provided context information to answer the question.
        2. Be specific and cite relevant data when appropriate.
        3. If there is not enough information to answer, state that clearly.
        4. Always answer in English.
        5. When mentioning specific data, be precise.

        Answer:
        """
    
    def get_report_config(self) -> Dict[str, Any]:
        """Get English report generation configuration."""
        return {
            "title": "Data Report",
            "max_rows": 500,
            "date_column": "date",
            "score_column": "score",
            "dealer_column": "category",
            "repair_type_column": "category",
            "language": "en-US"
        }
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize data according to default profile rules."""
        # Clean text columns
        for col in self.text_columns:
            if col in df.columns:
                df[col] = df[col].fillna('')
        
        # Clean score column
        if 'score' in df.columns:
            score_num = pd.to_numeric(df['score'], errors='coerce')
            df['score'] = score_num.fillna(0).astype(float)
        
        # Clean date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        return df
    
    def create_document_metadata(self, row_data: Dict[str, Any], row_index: int) -> Dict[str, Any]:
        """Create document metadata with English field names."""
        metadata = {"row": row_index}
        
        # Map to English metadata field names
        field_mapping = {
            "id": "id",
            "score": "score", 
            "date": "date",
            "category": "category"
        }
        
        for metadata_field, csv_field in field_mapping.items():
            if csv_field in row_data:
                metadata[metadata_field] = row_data[csv_field]
        
        return metadata
    
    def get_test_directory(self) -> str:
        """Get the path to test directory for default profile."""
        return str(Path(__file__).parent / "tests")
    
    def get_data_schema(self) -> DataSchema:
        """Get the data schema for default profile (fridge sales)."""
        return DataSchema(
            required_columns=self.required_columns,
            sensitive_columns=self.sensitive_columns,
            date_columns=['SALES_DATE'],
            text_columns=self.text_columns,
            metadata_columns=['ID', 'FRIDGE_MODEL', 'BRAND', 'CAPACITY_LITERS', 'PRICE', 'STORE_NAME', 'STORE_ADDRESS'],
            id_column='ID',
            score_column='PRICE'  # Use price as the "score" for fridge sales
        )
    
    def get_report_config(self) -> ReportConfig:
        """Get the report configuration for default profile (fridge sales)."""
        return ReportConfig(
            title="Fridge Sales Report",
            date_columns=['SALES_DATE'],
            score_columns=['PRICE'],
            filter_columns=['STORE_NAME', 'BRAND', 'FRIDGE_MODEL'],
            display_columns=['ID', 'CUSTOMER_ID', 'FRIDGE_MODEL', 'BRAND', 'CAPACITY_LITERS', 'PRICE', 'SALES_DATE', 'STORE_NAME', 'CUSTOMER_FEEDBACK'],
            max_rows=500
        )

    def get_provider_config(self):
        """Delegate to provider_config module for provider settings."""
        from .provider_config import get_provider_config as _get
        return _get()
