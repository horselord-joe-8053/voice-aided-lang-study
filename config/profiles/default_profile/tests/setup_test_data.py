#!/usr/bin/env python3
"""
Setup script for test data.
Ensures all required test data files are available for testing.
"""

import pandas as pd
import json
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def create_test_dataframe():
    """Create a comprehensive test DataFrame."""
    return pd.DataFrame({
        'ID': ['F001', 'F002', 'F003', 'F004', 'F005'],
        'CUSTOMER_ID': ['CUST001', 'CUST002', 'CUST003', 'CUST004', 'CUST005'],
        'FRIDGE_MODEL': ['RF28K9070SG', 'GNE27JYMFS', 'KRFF507HPS', 'RF28K9070SG', 'GNE27JYMFS'],
        'BRAND': ['Samsung', 'GE', 'KitchenAid', 'Samsung', 'GE'],
        'CAPACITY_LITERS': [28, 27, 30, 28, 27],
        'PRICE': [1299.99, 899.99, 1899.99, 1299.99, 899.99],
        'SALES_DATE': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19'],
        'STORE_NAME': ['New York Store', 'Chicago Store', 'Los Angeles Store', 'New York Store', 'Chicago Store'],
        'STORE_ADDRESS': ['123 Broadway', '456 Michigan Ave', '789 Sunset Blvd', '123 Broadway', '456 Michigan Ave'],
        'CUSTOMER_FEEDBACK': ['Great fridge!', 'Good value', 'Excellent quality', 'Love it!', 'Works well'],
        'FEEDBACK_RATING': ['Positive', 'Neutral', 'Positive', 'Positive', 'Positive']
    })

def create_extended_test_dataframe():
    """Create an extended test DataFrame with more data."""
    base_data = create_test_dataframe()
    
    # Add more rows with different brands and scenarios
    additional_data = pd.DataFrame({
        'ID': ['F006', 'F007', 'F008', 'F009', 'F010'],
        'CUSTOMER_ID': ['CUST006', 'CUST007', 'CUST008', 'CUST009', 'CUST010'],
        'FRIDGE_MODEL': ['RF28K9070SG', 'GNE27JYMFS', 'KRFF507HPS', 'RF28K9070SG', 'GNE27JYMFS'],
        'BRAND': ['Samsung', 'GE', 'KitchenAid', 'Samsung', 'GE'],
        'CAPACITY_LITERS': [28, 27, 30, 28, 27],
        'PRICE': [1299.99, 899.99, 1899.99, 1299.99, 899.99],
        'SALES_DATE': ['2024-01-20', '2024-01-21', '2024-01-22', '2024-01-23', '2024-01-24'],
        'STORE_NAME': ['Miami Store', 'Seattle Store', 'Denver Store', 'Miami Store', 'Seattle Store'],
        'STORE_ADDRESS': ['321 Ocean Dr', '654 Pine St', '987 Mountain Ave', '321 Ocean Dr', '654 Pine St'],
        'CUSTOMER_FEEDBACK': ['Perfect!', 'Good quality', 'Amazing fridge', 'Highly recommend', 'Great purchase'],
        'FEEDBACK_RATING': ['Positive', 'Positive', 'Positive', 'Positive', 'Positive']
    })
    
    return pd.concat([base_data, additional_data], ignore_index=True)

def create_test_queries():
    """Create test queries for different scenarios."""
    return {
        "aggregation_queries": [
            "What is the average price of Samsung fridges?",
            "How many fridges were sold by each brand?",
            "What is the total revenue from fridge sales?",
            "Which store has the highest sales volume?"
        ],
        "filtering_queries": [
            "Show me all Samsung fridges",
            "Find fridges with price above $1000",
            "List fridges sold in New York",
            "Show fridges with positive customer feedback"
        ],
        "comparison_queries": [
            "Compare Samsung and GE fridge prices",
            "Which brand has better customer ratings?",
            "Compare sales performance across stores"
        ],
        "complex_queries": [
            "What is the average price of Samsung fridges sold in New York with positive feedback?",
            "Show me the most expensive fridge from each brand",
            "Find the store with the highest average fridge price"
        ]
    }

def create_test_responses():
    """Create mock test responses."""
    return {
        "text2query_success": {
            "answer": "The average price of Samsung fridges is $1,299.99",
            "sources": [{"brand": "Samsung", "price": 1299.99}],
            "confidence": "high",
            "query_type": "aggregation",
            "synthesis_method": "traditional"
        },
        "text2query_failure": {
            "error": "No results found",
            "query_type": "synthesis_error"
        },
        "rag_success": {
            "answer": "Based on the data, Samsung fridges have an average price of $1,299.99 with positive customer feedback.",
            "sources": [{"content": "Samsung fridge data", "metadata": {"brand": "Samsung"}}],
            "confidence": "medium"
        },
        "rag_failure": {
            "answer": "I couldn't find specific information about Samsung fridge prices.",
            "sources": [],
            "confidence": "low"
        }
    }

def setup_test_data():
    """Setup all test data files."""
    print("Setting up test data...")
    
    # Create test data directory
    test_data_dir = Path(__file__).parent / "test_data"
    test_data_dir.mkdir(exist_ok=True)
    
    # Create basic test DataFrame
    df_basic = create_test_dataframe()
    df_basic.to_csv(test_data_dir / "fridge_sales_basic.csv", index=False)
    print(f"✅ Created basic test data: {len(df_basic)} rows")
    
    # Create extended test DataFrame
    df_extended = create_extended_test_dataframe()
    df_extended.to_csv(test_data_dir / "fridge_sales_extended.csv", index=False)
    print(f"✅ Created extended test data: {len(df_extended)} rows")
    
    # Create test queries
    test_queries = create_test_queries()
    with open(test_data_dir / "test_queries.json", "w") as f:
        json.dump(test_queries, f, indent=2)
    print(f"✅ Created test queries: {sum(len(queries) for queries in test_queries.values())} queries")
    
    # Create test responses
    test_responses = create_test_responses()
    with open(test_data_dir / "test_responses.json", "w") as f:
        json.dump(test_responses, f, indent=2)
    print(f"✅ Created test responses: {len(test_responses)} response types")
    
    # Create test configuration
    test_config = {
        "test_data_files": {
            "basic": "fridge_sales_basic.csv",
            "extended": "fridge_sales_extended.csv"
        },
        "test_queries_file": "test_queries.json",
        "test_responses_file": "test_responses.json",
        "data_schema": {
            "required_columns": ["ID", "CUSTOMER_ID", "FRIDGE_MODEL", "BRAND", "PRICE"],
            "sensitive_columns": ["CUSTOMER_ID"],
            "date_columns": ["SALES_DATE"],
            "text_columns": ["CUSTOMER_FEEDBACK"],
            "numeric_columns": ["PRICE", "CAPACITY_LITERS"]
        }
    }
    
    with open(test_data_dir / "test_config.json", "w") as f:
        json.dump(test_config, f, indent=2)
    print("✅ Created test configuration")
    
    print()
    print("Test data setup complete!")
    print(f"Test data directory: {test_data_dir}")
    print()
    print("Available test files:")
    for file_path in test_data_dir.glob("*"):
        print(f"  - {file_path.name}")

def verify_test_data():
    """Verify that all test data files exist and are valid."""
    print("Verifying test data...")
    
    test_data_dir = Path(__file__).parent / "test_data"
    
    required_files = [
        "fridge_sales_basic.csv",
        "fridge_sales_extended.csv",
        "test_queries.json",
        "test_responses.json",
        "test_config.json"
    ]
    
    all_valid = True
    
    for file_name in required_files:
        file_path = test_data_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name} - Found")
            
            # Validate CSV files
            if file_name.endswith('.csv'):
                try:
                    df = pd.read_csv(file_path)
                    print(f"   - {len(df)} rows, {len(df.columns)} columns")
                except Exception as e:
                    print(f"   ❌ Error reading CSV: {e}")
                    all_valid = False
            
            # Validate JSON files
            elif file_name.endswith('.json'):
                try:
                    with open(file_path, 'r') as f:
                        json.load(f)
                    print(f"   - Valid JSON")
                except Exception as e:
                    print(f"   ❌ Error reading JSON: {e}")
                    all_valid = False
        else:
            print(f"❌ {file_name} - Missing")
            all_valid = False
    
    if all_valid:
        print()
        print("✅ All test data files are valid!")
    else:
        print()
        print("❌ Some test data files are invalid or missing!")
    
    return all_valid

def main():
    """Main setup function."""
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        return 0 if verify_test_data() else 1
    else:
        setup_test_data()
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
