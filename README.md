# LinkedIn Job Matcher

An AI-powered job search assistant that automatically finds, extracts, and analyzes LinkedIn job opportunities from your Gmail inbox using GPT-4 and advanced web scraping.

## 🚀 Features

- **AI-Powered Analysis**: GPT-4 processes natural language queries about job search
- **Gmail Integration**: Automatically searches and processes LinkedIn job alert emails  
- **LinkedIn Scraping**: Extracts complete job details from LinkedIn URLs
- **Dual Architecture**: 
  - **Local Mode**: Direct function calls (faster, development)
  - **MCP Mode**: Client-Server architecture (scalable, production)
- **Smart Workflow**: Automated email → URL extraction → job scraping pipeline
- **Session Memory**: Maintains context across conversations
- **CI/CD Ready**: GitHub Actions for automated testing

## 🏗️ Architecture

### Local Mode (Direct)
```
User ↔ OpenAI GPT-4 ↔ Local Tools (Gmail + Scraper)
```

### MCP Mode (Client-Server)
```
User ↔ OpenAI GPT-4 ↔ MCP Client ↔ subprocess(stdio) ↔ MCP Server ↔ Tools
```

## 🛠️ Quick Start

### 1. Installation

```bash
git clone <repository-url>
cd linkedin_matcher
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# Set your OpenAI API key
export OPENAI_API_KEY='sk-your-openai-key'

# Set up Gmail API (optional but recommended)
# 1. Go to Google Cloud Console
# 2. Enable Gmail API  
# 3. Download credentials.json
# 4. Place in project root
```

### 3. Run the Application

```bash
# Local mode (recommended for development)
python main.py --mode local

# MCP Client-Server mode (recommended for production)
python main.py --mode mcp

# Run tests
python main.py --test

# Get help
python main.py --help
```

## 📋 Usage Examples

```bash
🗣️  You: Find data science jobs in my emails
🤖 AI Assistant: I'll search your Gmail for data science job opportunities...

🗣️  You: What are the latest machine learning positions?
🤖 AI Assistant: Let me look for machine learning jobs and scrape the details...

🗣️  You: Scrape and summarize the 5 most recent job postings
🤖 AI Assistant: I'll find recent job emails, extract URLs, and provide summaries...
```

## 🔧 Advanced Usage

### Testing Both Architectures

```bash
# Run comprehensive integration tests
python test_mcp_integration.py

# Test individual components
python run_tests.py
```

### Manual Tool Testing

```bash
# Test MCP server directly
python core/serve.py

# Test MCP client
python host/mcp_client.py
```

## 📁 Project Structure

```
linkedin_matcher/
├── main.py                    # Main launcher (NEW)
├── host/
│   ├── openai_host.py        # GPT-4 host with dual backend support
│   └── mcp_client.py         # MCP Client for subprocess communication
├── core/
│   ├── serve.py              # MCP Server launcher
│   ├── server_app.py         # FastMCP application
│   └── tools/
│       ├── gmail.py          # Pure Gmail data extraction tools
│       ├── scraper.py        # Pure LinkedIn scraping tools
│       └── scraper_gmail.py  # Combined scraper+gmail integration tools
├── scraper_module/           # Scraper components
│   ├── job_scraper.py        # Core scraping functionality
│   └── tools/                # Scraper integration tools
│       ├── __init__.py
│       └── gmail_scraper.py  # Gmail+scraper workflows
├── gmail_module/             # Gmail components
│   ├── gmail_api.py          # Gmail API interface
│   └── tests/                # Gmail-specific tests
├── test_mcp_integration.py   # Integration tests
├── run_tests.py              # Test runner
└── requirements.txt          # Dependencies
```

## 🔄 Migration Guide

### From Old Version
If you were using the old direct architecture:

```python
# OLD (still works)
from host.openai_host import OpenAILLMHost
host = OpenAILLMHost(use_mcp_client=False)

# NEW (recommended)
python main.py --mode local
```

### Choosing Architecture

**Use Local Mode when:**
- Development and debugging
- Single-user scenarios
- Need fastest response times
- Simple deployment

**Use MCP Mode when:**
- Production environments
- Multi-user scenarios  
- Need process isolation
- Scalable architecture
- Network boundary separation

## 🧪 Testing

```bash
# Run all tests
python main.py --test

# Run CI/CD tests
python run_tests.py

# Test specific components
python test_mcp_integration.py
```

## 🔧 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=sk-your-key      # Required
OPENAI_MODEL=gpt-4o             # Optional (default: gpt-4o)
```

### Gmail API Setup
1. Visit [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Gmail API
4. Create credentials (OAuth 2.0)
5. Download `credentials.json` to project root

## 🛠️ Tools Architecture

### Pure Data Extraction Tools
**Gmail Tools** (`core/tools/gmail.py`)
- `mcp_list_emails` - Search and list Gmail messages
- `mcp_extract_job_urls` - Extract LinkedIn URLs from emails
- `mcp_get_message_content` - Get full email content
- `mcp_add_label` - Apply labels to emails

### Pure Scraping Tools  
**Scraper Tools** (`core/tools/scraper.py`)
- `mcp_scrape_job` - Scrape single LinkedIn job posting
- `mcp_scrape_multiple_jobs` - Batch scrape multiple jobs
- `mcp_validate_linkedin_url` - Validate LinkedIn job URLs
- `mcp_convert_to_guest_url` - Convert to guest URLs
- `mcp_get_job_summary` - Quick job summary extraction

### Integrated Workflow Tools
**Scraper+Gmail Tools** (`core/tools/scraper_gmail.py`)
- `mcp_get_job_details_from_email` - Extract URLs from email + scrape
- `mcp_scrape_jobs_from_email_urls` - Scrape jobs with email context
- `mcp_scrape_jobs_from_url_list` - Batch scrape with optional context
- `mcp_process_linkedin_emails` - Full email workflow processing

### How LLM Uses Tools
1. **Data Extraction**: `list_emails` → Extract email data
2. **URL Extraction**: `extract_job_urls` → Get LinkedIn URLs  
3. **Web Scraping**: `scrape_job` → Get job details
4. **Working Memory**: Results stored for next tool calls
5. **Context Building**: LLM combines results intelligently

Example workflow:
```
User: "Find recent ML jobs and get details"
│
├─ list_emails(query="machine learning", max_results=5)
├─ extract_job_urls(email_id) for each email  
├─ scrape_job(url) for each URL
└─ Present combined results to user
```

## 🔧 CI/CD

The project includes GitHub Actions for:
- ✅ Unit testing
- ✅ Integration testing  
- ✅ Code quality checks
- ✅ Dependency validation

Push to `main` branch triggers full CI/CD pipeline.

## 🎯 Key Improvements in This Version

1. **Dual Architecture**: Choose between Local and MCP modes
2. **Simplified Launcher**: Single `main.py` entry point
3. **Better Testing**: Comprehensive integration tests
4. **Process Isolation**: MCP server runs in separate subprocess
5. **Network Boundary**: JSON-RPC communication protocol
6. **Resource Management**: Proper cleanup and lifecycle management
7. **Error Handling**: Robust error recovery and logging

## 🔮 Future Enhancements

- [ ] WebSocket-based MCP communication
- [ ] Multi-server MCP deployment
- [ ] Advanced job matching algorithms
- [ ] Email classification and labeling
- [ ] Job application tracking
- [ ] Calendar integration for interviews

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

---

🔗 **Architecture Comparison**

| Feature | Local Mode | MCP Mode |
|---------|------------|-----------|
| Speed | ⚡ Fastest | 🚀 Fast |
| Scalability | 📊 Limited | 📈 High |
| Debugging | 🔍 Easy | 🔧 Moderate |
| Isolation | ❌ None | ✅ Process |
| Network | ❌ No | ✅ JSON-RPC |
| Production | ⚠️ Basic | ✅ Ready | 