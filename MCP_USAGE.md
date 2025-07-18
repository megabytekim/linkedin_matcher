# LinkedIn Job Scraper MCP Usage Guide

## 🎯 What is MCP?

**Model Context Protocol (MCP)** allows AI assistants to use your LinkedIn job scraper as tools. Instead of just chatting, the AI can:
- 📧 **Search your Gmail** for job emails
- 🔗 **Extract LinkedIn URLs** from emails  
- 🌐 **Scrape job postings** for complete details
- 🔄 **Run complete workflows** automatically

## 🚀 Quick Start

### 1. Test Your MCP Tools
```bash
# Test all MCP tools work correctly
python test_mcp.py
```

### 2. Start MCP Server
```bash
# Start the MCP server (keeps running)
python mcp_client.py
```

### 3. Configure AI Assistant
Add this to your AI assistant's MCP configuration:
```json
{
  "mcpServers": {
    "linkedin-job-scraper": {
      "command": "python",
      "args": ["mcp_client.py"],
      "cwd": "/path/to/linkedin_matcher"
    }
  }
}
```

## 🛠️ Available MCP Tools

### 📧 Gmail Tools
- **`list_emails(query, max_results)`** - Search Gmail for job emails
- **`extract_job_urls(email_id)`** - Get LinkedIn URLs from an email
- **`get_email_content(email_id)`** - Read full email text
- **`label_email(email_id, label)`** - Add label to email
- **`get_job_details_from_email(email_id)`** - Complete email → job data

### 🌐 Scraper Tools  
- **`scrape_job(url)`** - Scrape single LinkedIn job posting
- **`scrape_multiple_jobs(urls)`** - Batch scrape with rate limiting
- **`convert_to_guest_url(url)`** - Convert to guest URL (no login)
- **`validate_linkedin_url(url)`** - Check if URL is valid
- **`get_job_summary(url)`** - Quick job overview

### 🔄 Workflow Tools
- **`full_workflow(query, max_emails, max_jobs)`** - Complete pipeline

## 💬 Example AI Conversations

### Find Recent Job Opportunities
```
User: "Find me recent data science jobs from my LinkedIn emails"

AI: I'll search your Gmail for recent LinkedIn emails and extract job postings related to data science.

[Uses list_emails("from:linkedin.com data science", 10)]
[Uses extract_job_urls() for each email]
[Uses scrape_job() for each URL]

Found 8 data science opportunities:
1. Senior Data Scientist at Google - $180k-220k
2. ML Engineer at Netflix - Remote, $160k-200k
...
```

### Analyze Specific Email
```
User: "What jobs are in email ID abc123?"

AI: [Uses get_job_details_from_email("abc123")]

This email contains 3 job opportunities:
- Software Engineer at Meta (Menlo Park, CA)
- Backend Developer at Stripe (San Francisco, CA) 
- Full Stack Engineer at Airbnb (Remote)
```

### Complete Job Search Workflow
```
User: "Run a complete job search for machine learning positions"

AI: [Uses full_workflow("from:linkedin.com machine learning", 10, 5)]

Workflow Results:
✅ Found 12 emails with ML keywords
✅ Extracted 23 job URLs
✅ Successfully scraped 5 complete job postings
✅ Jobs saved with full descriptions and details
```

## 🔧 Configuration

### Environment Variables (.env)
```env
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_DEFAULT_QUERY=from:linkedin.com
GMAIL_MAX_RESULTS=10
```

### MCP Server Settings
- **Default delays**: 2-5 seconds between scrapes
- **Rate limiting**: Built-in to avoid LinkedIn blocking
- **Fresh browsers**: New instance per job for reliability
- **Guest URLs**: No LinkedIn login required

## 🧪 Testing

### Test Individual Tools
```python
# Test Gmail tools
from mcp.gmail_tools import list_emails, extract_job_urls
emails = list_emails("from:linkedin.com", 5)
urls = extract_job_urls(emails[0]['id'])

# Test scraper tools  
from mcp.scraper_tools import scrape_job, validate_linkedin_url
is_valid = validate_linkedin_url("https://linkedin.com/jobs/view/123")
job_data = scrape_job("https://linkedin.com/jobs-guest/jobs/view/123")
```

### Run Full Test Suite
```bash
python test_mcp.py
```

## 🔄 Architecture

```
AI Assistant
    ↓ (MCP Protocol)
mcp_client.py (MCP Server)
    ↓
├── mcp/gmail_tools.py → gmail_module/gmail_api.py
└── mcp/scraper_tools.py → scraper_module/job_scraper.py
```

The `mcp_client.py` acts as a **protocol bridge** that:
1. **Receives tool calls** from AI assistant via MCP
2. **Routes calls** to appropriate modules (gmail/scraper)
3. **Returns results** back to AI assistant
4. **Handles errors** and provides consistent interfaces

## 🛡️ Security & Privacy

- ✅ **Local data only** - No data sent to external services
- ✅ **OAuth2 Gmail access** - Secure authentication
- ✅ **Guest URL scraping** - No LinkedIn login required
- ✅ **Rate limited** - Respects LinkedIn's limits
- ✅ **Error handling** - Graceful failures

## 🚨 Troubleshooting

### MCP Server Won't Start
```bash
# Check dependencies
pip install -r requirements.txt

# Test imports
python -c "from mcp_client import app; print('OK')"
```

### Gmail Tools Fail
```bash
# Check Gmail setup
python gmail_module/tests/test_gmail_api_unit.py

# Re-authenticate
rm token.json
python test_mcp.py
```

### Scraper Tools Fail
```bash
# Install browsers
playwright install

# Test scraper
python scraper_module/test_with_real_urls.py
```

### AI Assistant Can't Connect
1. Check `mcp_config.json` path is correct
2. Ensure MCP server is running: `python mcp_client.py`
3. Check AI assistant MCP configuration
4. Look for error messages in server output

## 📈 Performance Tips

- **Use specific queries** for faster Gmail searches
- **Limit max_results** to avoid timeouts
- **Use get_job_summary()** for quick overviews
- **Batch process** with scrape_multiple_jobs()
- **Cache results** to avoid re-scraping same jobs

---

🎉 **Your LinkedIn job scraper is now ready for AI assistant integration!** 