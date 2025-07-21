#!/usr/bin/env python3
"""
MCP Client for LinkedIn Job Scraper

This implements a Model Context Protocol (MCP) client that communicates
with the MCP server via subprocess stdio.

Architecture:
OpenAI Host → MCP Client → subprocess(stdio) → MCP Server → Tools
"""

import asyncio
import json
import subprocess
import sys
import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPClientError(Exception):
    """Custom exception for MCP Client errors."""
    pass

class MCPClient:
    """
    MCP Client that communicates with MCP server via subprocess stdio.
    
    This client:
    1. Starts MCP server as subprocess
    2. Communicates via JSON-RPC over stdio
    3. Handles tool calls and responses
    4. Manages server lifecycle
    """
    
    def __init__(self, server_command: List[str], cwd: Optional[str] = None):
        """
        Initialize MCP Client.
        
        Args:
            server_command: Command to start MCP server (e.g., ['python', 'core/serve.py'])
            cwd: Working directory for server process
        """
        self.server_command = server_command
        self.cwd = cwd or str(Path(__file__).parent.parent)  # Default to project root
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.running = False
        self._tool_semaphore = asyncio.Semaphore(2)  # Limit to 2 concurrent tool calls
        
        logger.info(f"🚀 MCP Client initialized")
        logger.info(f"   Server command: {' '.join(server_command)}")
        logger.info(f"   Working directory: {self.cwd}")
    
    async def start(self) -> None:
        """Start the MCP server subprocess and initialize communication."""
        try:
            logger.info("🔧 Starting MCP server subprocess...")
            
            # Set up environment for server process
            import os
            env = os.environ.copy()
            env['PYTHONPATH'] = self.cwd  # Add project root to Python path
            
            # Start server process with stdio pipes
            self.process = subprocess.Popen(
                self.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.cwd,
                text=True,
                bufsize=0,  # Unbuffered for real-time communication
                env=env  # Pass environment with PYTHONPATH
            )
            
            self.running = True
            logger.info(f"✅ MCP server started (PID: {self.process.pid})")
            logger.info(f"   PYTHONPATH: {env.get('PYTHONPATH', 'not set')}")
            
            # Start background tasks
            asyncio.create_task(self._read_responses())
            asyncio.create_task(self._read_stderr())  # Monitor server errors
            
            # Give server a moment to start
            await asyncio.sleep(0.5)
            
            # Initialize the MCP connection
            await self._initialize_connection()
            
        except Exception as e:
            logger.error(f"❌ Failed to start MCP server: {e}")
            raise MCPClientError(f"Failed to start MCP server: {e}")
    
    async def stop(self) -> None:
        """Stop the MCP server subprocess."""
        try:
            logger.info("🛑 Stopping MCP server...")
            self.running = False
            
            if self.process:
                # Send shutdown signal
                try:
                    await self._send_request("shutdown", {})
                except:
                    pass  # Ignore errors during shutdown
                
                # Terminate process
                self.process.terminate()
                
                # Wait for process to end (with timeout)
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("⚠️  MCP server didn't shut down gracefully, killing...")
                    self.process.kill()
                    self.process.wait()
                
                logger.info("✅ MCP server stopped")
                self.process = None
            
        except Exception as e:
            logger.error(f"❌ Error stopping MCP server: {e}")
    
    async def _read_stderr(self) -> None:
        """Background task to read and log server stderr."""
        logger.info("👂 Starting stderr reader...")
        
        try:
            while self.running and self.process:
                # Read line from server stderr
                line = await asyncio.get_event_loop().run_in_executor(
                    None, self.process.stderr.readline
                )
                
                if not line:
                    # Server closed stderr
                    logger.warning("⚠️  MCP server closed stderr")
                    break
                
                line = line.strip()
                if line:
                    logger.info(f"🔧 Server: {line}")
        
        except Exception as e:
            logger.error(f"❌ Stderr reader error: {e}")
        finally:
            logger.info("👂 Stderr reader stopped")
    
    async def _initialize_connection(self) -> None:
        """Initialize the MCP connection with handshake."""
        try:
            logger.info("🤝 Initializing MCP connection...")
            
            # Send initialize request
            result = await self._send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "linkedin-matcher-client",
                    "version": "1.0.0"
                }
            })
            
            logger.info("✅ MCP connection initialized")
            logger.info(f"   Server capabilities: {result.get('capabilities', {})}")
            
            # Send initialized notification
            await self._send_notification("notifications/initialized", {})
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize MCP connection: {e}")
            raise MCPClientError(f"Failed to initialize MCP connection: {e}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool execution result
        """
        async with self._tool_semaphore:  # Limit concurrent tool calls
            try:
                logger.info(f"🔧 Calling tool: {tool_name}")
                logger.debug(f"   Arguments: {arguments}")
                
                result = await self._send_request("tools/call", {
                    "name": tool_name,
                    "arguments": arguments
                })
                
                logger.info(f"✅ Tool {tool_name} completed")
                return result
                
            except Exception as e:
                logger.error(f"❌ Tool {tool_name} failed: {e}")
                raise MCPClientError(f"Tool {tool_name} failed: {e}")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the MCP server."""
        try:
            logger.info("📋 Listing available tools...")
            
            result = await self._send_request("tools/list", {})
            tools = result.get("tools", [])
            
            logger.info(f"✅ Found {len(tools)} tools")
            for tool in tools:
                logger.info(f"   - {tool.get('name', 'unknown')}: {tool.get('description', 'no description')}")
            
            return tools
            
        except Exception as e:
            logger.error(f"❌ Failed to list tools: {e}")
            raise MCPClientError(f"Failed to list tools: {e}")
    
    async def _send_request(self, method: str, params: Dict[str, Any]) -> Any:
        """Send a JSON-RPC request and wait for response."""
        if not self.running or not self.process:
            raise MCPClientError("MCP server is not running")
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Create JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params
        }
        
        # Create future for response
        future = asyncio.Future()
        self.pending_requests[request_id] = future
        
        try:
            # Send request to server
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            logger.debug(f"📤 Sent request: {method} (ID: {request_id})")
            
            # Wait for response (with timeout)
            response = await asyncio.wait_for(future, timeout=60.0)  # Increased timeout for scraping operations
            return response
            
        except asyncio.TimeoutError:
            self.pending_requests.pop(request_id, None)
            raise MCPClientError(f"Request {method} timed out")
        except Exception as e:
            self.pending_requests.pop(request_id, None)
            raise MCPClientError(f"Request {method} failed: {e}")
    
    async def _send_notification(self, method: str, params: Dict[str, Any]) -> None:
        """Send a JSON-RPC notification (no response expected)."""
        if not self.running or not self.process:
            raise MCPClientError("MCP server is not running")
        
        # Create JSON-RPC notification (no ID)
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        
        try:
            # Send notification to server
            notification_json = json.dumps(notification) + "\n"
            self.process.stdin.write(notification_json)
            self.process.stdin.flush()
            
            logger.debug(f"📤 Sent notification: {method}")
            
        except Exception as e:
            raise MCPClientError(f"Notification {method} failed: {e}")
    
    async def _read_responses(self) -> None:
        """Background task to read responses from server."""
        logger.info("👂 Starting response reader...")
        
        try:
            while self.running and self.process:
                # Read line from server stdout
                line = await asyncio.get_event_loop().run_in_executor(
                    None, self.process.stdout.readline
                )
                
                if not line:
                    # Server closed stdout
                    logger.warning("⚠️  MCP server closed stdout")
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # Parse JSON-RPC response
                    response = json.loads(line)
                    await self._handle_response(response)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Invalid JSON from server: {line}")
                except Exception as e:
                    logger.error(f"❌ Error handling response: {e}")
        
        except Exception as e:
            logger.error(f"❌ Response reader error: {e}")
        finally:
            logger.info("👂 Response reader stopped")
    
    async def _handle_response(self, response: Dict[str, Any]) -> None:
        """Handle a response from the server."""
        logger.debug(f"📥 Received response: {response}")
        
        # Check if it's a response to a request
        if "id" in response:
            request_id = response["id"]
            future = self.pending_requests.pop(request_id, None)
            
            if future:
                if "error" in response:
                    # Request failed
                    error = response["error"]
                    error_msg = f"{error.get('code', 'unknown')}: {error.get('message', 'unknown error')}"
                    future.set_exception(MCPClientError(error_msg))
                else:
                    # Request succeeded
                    result = response.get("result", {})
                    future.set_result(result)
            else:
                logger.warning(f"⚠️  Received response for unknown request ID: {request_id}")
        
        # Handle notifications (no ID)
        elif "method" in response:
            method = response["method"]
            params = response.get("params", {})
            logger.info(f"📢 Received notification: {method}")
            # Handle server notifications here if needed
    
    def is_running(self) -> bool:
        """Check if the MCP server is running."""
        return self.running and self.process is not None and self.process.poll() is None

# Example usage and testing
async def test_mcp_client():
    """Test the MCP client with the LinkedIn job scraper server."""
    client = MCPClient(["python", "core/serve.py"])
    
    try:
        # Start the client
        await client.start()
        
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[tool['name'] for tool in tools]}")
        
        # Test a simple tool call
        if tools:
            tool_name = tools[0]['name']
            print(f"Testing tool: {tool_name}")
            
            # Example: call list_emails tool
            if tool_name == "mcp_list_emails":
                result = await client.call_tool(tool_name, {
                    "query": "from:linkedin.com",
                    "max_results": 3
                })
                print(f"Tool result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Stop the client
        await client.stop()

if __name__ == "__main__":
    asyncio.run(test_mcp_client()) 