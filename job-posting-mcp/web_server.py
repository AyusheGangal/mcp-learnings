#!/usr/bin/env python3
"""
Web wrapper for the MCP Job Posting Server
Exposes MCP functionality via HTTP API for Railway deployment
"""

import asyncio
import json
import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# Import the MCP server
from server import JobPostingServer

app = FastAPI(title="Job Posting API", version="1.0.0")

# Global server instance
job_server = None

@app.on_event("startup")
async def startup():
    global job_server
    job_server = JobPostingServer()
    await job_server._load_jobs_data()

@app.get("/")
async def root():
    return {"message": "Job Posting MCP Server API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/jobs")
async def list_jobs():
    """List all jobs"""
    try:
        result = await job_server._list_all_jobs()
        return json.loads(result[0].text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/search")
async def search_jobs(
    query: str = "",
    location: str = "",
    remote: bool = None,
    visa_sponsorship: bool = None,
    experience_level: str = ""
):
    """Search jobs with filters"""
    try:
        args = {"query": query}
        if location:
            args["location"] = location
        if remote is not None:
            args["remote"] = remote
        if visa_sponsorship is not None:
            args["visa_sponsorship"] = visa_sponsorship
        if experience_level:
            args["experience_level"] = experience_level
            
        result = await job_server._search_jobs(args)
        return json.loads(result[0].text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get specific job details"""
    try:
        result = await job_server._get_job_details({"job_id": job_id})
        return json.loads(result[0].text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/companies")
async def get_companies():
    """Get all companies"""
    try:
        result = await job_server._get_companies()
        return json.loads(result[0].text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/technologies")
async def get_technologies():
    """Get all technologies"""
    try:
        result = await job_server._get_tech_stacks()
        return json.loads(result[0].text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)