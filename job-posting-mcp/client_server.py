#!/usr/bin/env python3
"""
MCP Client for deployed Job Posting API
Connects Claude to the Railway-deployed job posting service
"""

import asyncio
import json
import logging
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from mcp.types import ServerCapabilities
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("job-posting-client")

# Railway API URL
API_BASE_URL = "https://fortunate-determination-production.up.railway.app"

class JobPostingClient:
    def __init__(self):
        self.server = Server("job-posting-client")
        self._setup_handlers()
    
    def _setup_handlers(self):
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools for job search and management"""
            return [
                types.Tool(
                    name="search_jobs",
                    description="Search for jobs by title, company, location, or tech stack",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (can be job title, company, location, or technology)"
                            },
                            "location": {
                                "type": "string",
                                "description": "Filter by location (optional)"
                            },
                            "remote": {
                                "type": "boolean",
                                "description": "Filter by remote work availability (optional)"
                            },
                            "visa_sponsorship": {
                                "type": "boolean",
                                "description": "Filter by visa sponsorship availability (optional)"
                            },
                            "experience_level": {
                                "type": "string",
                                "description": "Filter by experience level (Entry, Mid, Mid-Senior, Senior) (optional)"
                            }
                        },
                        "required": []
                    }
                ),
                types.Tool(
                    name="get_job_details",
                    description="Get detailed information about a specific job by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "job_id": {
                                "type": "string",
                                "description": "The unique job ID"
                            }
                        },
                        "required": ["job_id"]
                    }
                ),
                types.Tool(
                    name="list_all_jobs",
                    description="Get a list of all available job postings",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="get_companies",
                    description="Get a list of all companies with job postings",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="get_tech_stacks",
                    description="Get a list of all technologies mentioned in job postings",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None
        ) -> List[types.TextContent]:
            """Handle tool calls by making HTTP requests to Railway API"""
            
            try:
                if name == "search_jobs":
                    return await self._search_jobs(arguments or {})
                elif name == "get_job_details":
                    return await self._get_job_details(arguments or {})
                elif name == "list_all_jobs":
                    return await self._list_all_jobs()
                elif name == "get_companies":
                    return await self._get_companies()
                elif name == "get_tech_stacks":
                    return await self._get_tech_stacks()
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]

    async def _search_jobs(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Search for jobs via API"""
        params = {}
        if arguments.get("query"):
            params["query"] = arguments["query"]
        if arguments.get("location"):
            params["location"] = arguments["location"]
        if arguments.get("remote") is not None:
            params["remote"] = arguments["remote"]
        if arguments.get("visa_sponsorship") is not None:
            params["visa_sponsorship"] = arguments["visa_sponsorship"]
        if arguments.get("experience_level"):
            params["experience_level"] = arguments["experience_level"]
        
        response = requests.get(f"{API_BASE_URL}/jobs/search", params=params, timeout=10)
        response.raise_for_status()
        
        return [types.TextContent(
            type="text",
            text=json.dumps(response.json(), indent=2)
        )]

    async def _get_job_details(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get job details via API"""
        job_id = arguments.get("job_id")
        if not job_id:
            raise ValueError("job_id is required")
        
        response = requests.get(f"{API_BASE_URL}/jobs/{job_id}", timeout=10)
        response.raise_for_status()
        
        return [types.TextContent(
            type="text",
            text=json.dumps(response.json(), indent=2)
        )]

    async def _list_all_jobs(self) -> List[types.TextContent]:
        """List all jobs via API"""
        response = requests.get(f"{API_BASE_URL}/jobs", timeout=10)
        response.raise_for_status()
        
        return [types.TextContent(
            type="text",
            text=json.dumps(response.json(), indent=2)
        )]

    async def _get_companies(self) -> List[types.TextContent]:
        """Get companies via API"""
        response = requests.get(f"{API_BASE_URL}/companies", timeout=10)
        response.raise_for_status()
        
        return [types.TextContent(
            type="text",
            text=json.dumps(response.json(), indent=2)
        )]

    async def _get_tech_stacks(self) -> List[types.TextContent]:
        """Get tech stacks via API"""
        response = requests.get(f"{API_BASE_URL}/technologies", timeout=10)
        response.raise_for_status()
        
        return [types.TextContent(
            type="text",
            text=json.dumps(response.json(), indent=2)
        )]

    async def run(self):
        """Run the MCP client server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="job-posting-client",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(
                        tools={"list_changed": False},
                    ),
                ),
            )

async def main():
    """Main entry point"""
    client = JobPostingClient()
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())