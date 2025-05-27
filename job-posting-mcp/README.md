# Job Posting MCP Server

An MCP (Model Context Protocol) server that provides access to job posting data with search and filtering capabilities.

## Features

- Search jobs by title, company, location, or technology
- Filter by remote work availability
- Filter by visa sponsorship
- Filter by experience level
- Get detailed job information
- List all companies and technologies

## Installation

```bash
cd mcp-learning/job-posting-mcp
pip install -r requirements.txt
```

## Usage

### Running the Server

```bash
python server.py
```

### Available Tools

1. **search_jobs** - Search for jobs with optional filters
2. **get_job_details** - Get detailed information about a specific job
3. **list_all_jobs** - Get all available job postings
4. **get_companies** - Get list of all companies
5. **get_tech_stacks** - Get list of all technologies

### Example Usage

The server connects to the job data API and provides structured access to:
- 4 job postings from AI/ML companies in Europe
- Jobs in Berlin, Amsterdam, Dublin, and Munich
- Salary ranges from €55,000 to €100,000
- Mix of remote and on-site positions
- Various tech stacks including Python, TensorFlow, PyTorch, etc.

## Data Source

Job data is fetched from: `https://mocki.io/v1/5923b1db-516f-496c-a7e9-7a18b5104deb`

The server loads this data on-demand and provides structured access through MCP tools.