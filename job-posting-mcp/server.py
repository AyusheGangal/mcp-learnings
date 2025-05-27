#!/usr/bin/env python3
"""
MCP Server for Job Posting Site
Provides access to job listings with search and filter capabilities
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from mcp.types import ServerCapabilities
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("job-posting-mcp")

# Job data source
JOBS_API_URL = "https://mocki.io/v1/5923b1db-516f-496c-a7e9-7a18b5104deb"

class JobPostingServer:
    def __init__(self):
        self.server = Server("job-posting-mcp")
        self.jobs_data = []
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
            """Handle tool calls"""
            await self._load_jobs_data()
            
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

    async def _load_jobs_data(self):
        """Load jobs data from the API"""
        if not self.jobs_data:
            try:
                response = requests.get(JOBS_API_URL, timeout=10)
                response.raise_for_status()
                data = response.json()
                self.jobs_data = data.get("jobs", [])
                logger.info(f"Loaded {len(self.jobs_data)} jobs")
            except Exception as e:
                logger.error(f"Failed to load jobs data: {e}")
                raise

    async def _search_jobs(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Search for jobs based on criteria"""
        query = arguments.get("query", "").lower()
        location_filter = arguments.get("location", "").lower()
        remote_filter = arguments.get("remote")
        visa_filter = arguments.get("visa_sponsorship")
        experience_filter = arguments.get("experience_level", "").lower()

        filtered_jobs = []
        
        for job in self.jobs_data:
            # Text search in title, company, location, tech stack
            if query:
                searchable_text = f"{job['title']} {job['company']} {job['location']} {' '.join(job['tech_stack'])}".lower()
                if query not in searchable_text:
                    continue
            
            # Location filter
            if location_filter and location_filter not in job['location'].lower():
                continue
            
            # Remote filter
            if remote_filter is not None and job['remote'] != remote_filter:
                continue
            
            # Visa sponsorship filter
            if visa_filter is not None and job['visa_sponsorship'] != visa_filter:
                continue
            
            # Experience level filter
            if experience_filter and experience_filter not in job['experience_level'].lower():
                continue
            
            filtered_jobs.append(job)

        result = {
            "total_results": len(filtered_jobs),
            "jobs": filtered_jobs
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    async def _get_job_details(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get details for a specific job"""
        job_id = arguments.get("job_id")
        if not job_id:
            raise ValueError("job_id is required")
        
        job = next((j for j in self.jobs_data if j["id"] == job_id), None)
        if not job:
            return [types.TextContent(
                type="text",
                text=f"Job with ID '{job_id}' not found"
            )]
        
        return [types.TextContent(
            type="text",
            text=json.dumps(job, indent=2)
        )]

    async def _list_all_jobs(self) -> List[types.TextContent]:
        """List all available jobs"""
        result = {
            "total_jobs": len(self.jobs_data),
            "jobs": self.jobs_data
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    async def _get_companies(self) -> List[types.TextContent]:
        """Get list of all companies"""
        companies = list(set(job["company"] for job in self.jobs_data))
        companies.sort()
        
        result = {
            "total_companies": len(companies),
            "companies": companies
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    async def _get_tech_stacks(self) -> List[types.TextContent]:
        """Get list of all technologies"""
        all_techs = set()
        for job in self.jobs_data:
            all_techs.update(job["tech_stack"])
        
        techs = sorted(list(all_techs))
        
        result = {
            "total_technologies": len(techs),
            "technologies": techs
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="job-posting-mcp",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(
                        tools={"list_changed": False},
                    ),
                ),
            )

async def main():
    """Main entry point"""
    server = JobPostingServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())