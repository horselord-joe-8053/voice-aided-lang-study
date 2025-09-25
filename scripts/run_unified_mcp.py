#!/usr/bin/env python3
"""
Startup script for the Unified QueryRAG System MCP Server.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import asyncio
    from servers.unified_mcp_server import main
    
    print("Starting Unified QueryRAG System MCP Server...")
    print("MCP server will run on stdio for AI tool integration")
    
    asyncio.run(main())
