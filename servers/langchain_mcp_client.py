from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Tuple

from config.langchain_settings import load_langchain_config
from config.logging_config import get_logger

try:
    # FastMCP async client
    from fastmcp import Client  # type: ignore
except Exception:  # pragma: no cover
    Client = None  # type: ignore

logger = get_logger(__name__)

class LangChainMCPClient:
    """LangChain-compatible MCP client for tool calling."""
    
    def __init__(self, base_url: Optional[str] = None):
        self.config = load_langchain_config()
        env_url = os.getenv("MCP_HTTP_URL") or os.getenv("MCP_BASE_URL")
        primary = base_url or env_url or f"http://127.0.0.1:{self.config.mcp_port}"
        fallback = f"http://127.0.0.1:{self.config.mcp_port}"
        
        # Ensure /mcp suffix
        if not primary.rstrip("/").endswith("/mcp"):
            primary = primary.rstrip("/") + "/mcp"
        if not fallback.rstrip("/").endswith("/mcp"):
            fallback = fallback.rstrip("/") + "/mcp"
        
        self.primary_url = primary
        self.fallback_url = fallback

    def call_generate_report(self, question: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Call the generate_report tool on the MCP server."""
        if Client is None:
            logger.error("FastMCP Client not available")
            return None, None
        
        urls = [self.primary_url]
        if self.fallback_url not in urls:
            urls.append(self.fallback_url)
        
        try:
            async def _run() -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
                for url in urls:
                    try:
                        logger.info(f"Calling MCP server at {url}")
                        async with Client(url) as client:  # type: ignore
                            result = await client.call_tool("generate_report", {"question": question})
                            
                            # Parse the result
                            payload: Optional[Dict[str, Any]] = None
                            for item in getattr(result, "content", []) or []:
                                j = getattr(item, "json", None)
                                if isinstance(j, dict):
                                    payload = j
                                    break
                                t = getattr(item, "text", None)
                                if isinstance(t, str):
                                    try:
                                        payload = json.loads(t)
                                        break
                                    except Exception:
                                        pass
                            
                            if not isinstance(payload, Dict):
                                logger.warning(f"No valid payload received from {url}")
                                continue
                            
                            if not payload.get("ok"):
                                logger.warning(f"Tool call failed: {payload.get('error', 'Unknown error')}")
                                continue
                            
                            meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else None
                            path = payload.get("path") if isinstance(payload.get("path"), str) else None
                            
                            logger.info(f"Report generated successfully: {path}")
                            return path, meta
                            
                    except Exception as e:
                        logger.warning(f"Failed to call MCP server at {url}: {e}")
                        continue
                
                logger.error("All MCP server URLs failed")
                return None, None

            import asyncio
            return asyncio.run(_run())
            
        except Exception as e:
            logger.error(f"Error calling MCP server: {e}")
            return None, None

    def call_get_stats(self) -> Optional[Dict[str, Any]]:
        """Call the get_system_stats tool on the MCP server."""
        if Client is None:
            logger.error("FastMCP Client not available")
            return None
        
        urls = [self.primary_url]
        if self.fallback_url not in urls:
            urls.append(self.fallback_url)
        
        try:
            async def _run() -> Optional[Dict[str, Any]]:
                for url in urls:
                    try:
                        logger.info(f"Calling MCP server stats at {url}")
                        async with Client(url) as client:  # type: ignore
                            result = await client.call_tool("get_system_stats", {})
                            
                            # Parse the result
                            payload: Optional[Dict[str, Any]] = None
                            for item in getattr(result, "content", []) or []:
                                j = getattr(item, "json", None)
                                if isinstance(j, dict):
                                    payload = j
                                    break
                                t = getattr(item, "text", None)
                                if isinstance(t, str):
                                    try:
                                        payload = json.loads(t)
                                        break
                                    except Exception:
                                        pass
                            
                            if not isinstance(payload, Dict):
                                logger.warning(f"No valid payload received from {url}")
                                continue
                            
                            if not payload.get("ok"):
                                logger.warning(f"Stats call failed: {payload.get('error', 'Unknown error')}")
                                continue
                            
                            stats = payload.get("stats")
                            logger.info("System stats retrieved successfully")
                            return stats
                            
                    except Exception as e:
                        logger.warning(f"Failed to call MCP server stats at {url}: {e}")
                        continue
                
                logger.error("All MCP server URLs failed for stats")
                return None

            import asyncio
            return asyncio.run(_run())
            
        except Exception as e:
            logger.error(f"Error calling MCP server for stats: {e}")
            return None

    def call_rebuild_vectorstore(self) -> bool:
        """Call the rebuild_vectorstore tool on the MCP server."""
        if Client is None:
            logger.error("FastMCP Client not available")
            return False
        
        urls = [self.primary_url]
        if self.fallback_url not in urls:
            urls.append(self.fallback_url)
        
        try:
            async def _run() -> bool:
                for url in urls:
                    try:
                        logger.info(f"Calling MCP server rebuild at {url}")
                        async with Client(url) as client:  # type: ignore
                            result = await client.call_tool("rebuild_vectorstore", {})
                            
                            # Parse the result
                            payload: Optional[Dict[str, Any]] = None
                            for item in getattr(result, "content", []) or []:
                                j = getattr(item, "json", None)
                                if isinstance(j, dict):
                                    payload = j
                                    break
                                t = getattr(item, "text", None)
                                if isinstance(t, str):
                                    try:
                                        payload = json.loads(t)
                                        break
                                    except Exception:
                                        pass
                            
                            if not isinstance(payload, Dict):
                                logger.warning(f"No valid payload received from {url}")
                                continue
                            
                            if not payload.get("ok"):
                                logger.warning(f"Rebuild call failed: {payload.get('error', 'Unknown error')}")
                                continue
                            
                            logger.info("Vector store rebuild completed successfully")
                            return True
                            
                    except Exception as e:
                        logger.warning(f"Failed to call MCP server rebuild at {url}: {e}")
                        continue
                
                logger.error("All MCP server URLs failed for rebuild")
                return False

            import asyncio
            return asyncio.run(_run())
            
        except Exception as e:
            logger.error(f"Error calling MCP server for rebuild: {e}")
            return False

# Singleton instance
_mcp_client: Optional[LangChainMCPClient] = None

def get_mcp_client() -> LangChainMCPClient:
    """Get the singleton MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = LangChainMCPClient()
    return _mcp_client
