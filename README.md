# LinkedIn Job Scraper

A powerful tool that extracts LinkedIn job URLs from Gmail and scrapes complete job descriptions with full text content.

## ✨ Features

- 🔍 **Gmail Integration** - Extract job URLs from LinkedIn job alert emails
- 🌐 **LinkedIn Job Scraping** - Scrape complete job descriptions without authentication
- 🚀 **Full Content Extraction** - Handles "Show more" buttons to get complete job descriptions
- ⚡ **Fast & Reliable** - Fresh browser instances prevent conflicts and timeouts
- 📝 **Rich Data Extraction** - Job titles, companies, locations, full descriptions, and metadata
- 🛡️ **Popup Handling** - Automatically handles LinkedIn dialogs and modals
- 🔄 **Rate Limiting** - Built-in delays to avoid being blocked

## 🎯 Recent Success

✅ **Perfect Results**: Successfully scraped 3/3 real LinkedIn jobs  
✅ **Full Descriptions**: 3,226-7,211 characters per job (no truncation)  
✅ **Speed**: Fast processing with fresh browser instances  
✅ **Reliability**: 100% success rate with popup handling

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install
```

### 2. Gmail API Setup
1. Follow the detailed guide in `GMAIL_SETUP.md`
2. Download `credentials.json` from Google Cloud Console
3. Create `.env` file with your configuration

### 3. Create .env File
```env
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_DEFAULT_QUERY=from:linkedin.com
GMAIL_MAX_RESULTS=10
```

### 4. Extract Real Job URLs from Gmail
```bash
# Extract LinkedIn job URLs from your Gmail
python scraper_module/extract_and_save_real_urls.py
```

### 5. Test Job Scraping
```bash
# Test with real URLs from your Gmail
python scraper_module/test_with_real_urls.py

# View complete results
python scraper_module/show_full_results.py
```

## 📁 Project Structure

```
linkedin_matcher/
├── gmail_module/                 # Gmail API functionality
│   ├── __init__.py              # Gmail module exports
│   ├── gmail_api.py             # Gmail API: auth, email listing, URL extraction
│   └── tests/                   # Gmail-specific tests
├── scraper_module/              # LinkedIn job scraping
│   ├── __init__.py              # Scraper module exports  
│   ├── job_scraper.py           # Advanced LinkedIn scraper with Playwright
│   ├── extract_and_save_real_urls.py    # Extract URLs from Gmail
│   ├── test_with_real_urls.py           # Test scraper with real data
│   ├── show_full_results.py             # Display complete results
│   └── visible_urls/            # Scraped data and results
├── .env                         # Configuration (create this)
├── credentials.json             # Gmail API credentials (download from GCP)
├── token.json                   # OAuth token (auto-generated)
├── config.py                    # Configuration loader
├── GMAIL_SETUP.md              # Detailed Gmail setup guide
└── requirements.txt            # Python dependencies
```

## 🔧 Core Modules

### Gmail Module (`gmail_module/`)
- **Gmail API Integration** - OAuth2 authentication and email access
- **Job URL Extraction** - Parse LinkedIn job URLs from email content
- **Email Labeling** - Organize processed emails
- **Search & Filter** - Query emails with various criteria

### Scraper Module (`scraper_module/`)
- **Advanced LinkedIn Scraper** - Extracts complete job information
- **Guest URL Conversion** - Access LinkedIn jobs without authentication
- **Popup Handling** - Automatically closes dialogs and modals
- **Fresh Browser Strategy** - Prevents conflicts and timeouts
- **Full Content Extraction** - Handles "Show more" buttons
- **Rate Limiting** - Avoids being blocked by LinkedIn

## 📊 Sample Results

```json
{
  "title": "Senior Data Scientist, Ads Performance - Moloco Streaming Monetization",
  "company": "Moloco",
  "location": "Seoul, South Korea", 
  "description": "About Moloco: Moloco is a machine learning company...", // 7,211 characters
  "pageTitle": "Moloco hiring Senior Data Scientist...",
  "jobDetails": ["Mid-Senior level", "Full-time", "Engineering"],
  "url": "https://www.linkedin.com/comm/jobs/view/4267053111/...",
  "guest_url": "https://www.linkedin.com/jobs-guest/jobs/view/4267053111/",
  "scraped_at": "2025-07-18T22:49:50.391160"
}
```

## ⚙️ Configuration

Create a `.env` file with these variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `GMAIL_CREDENTIALS_FILE` | `credentials.json` | Google Cloud credentials file |
| `GMAIL_TOKEN_FILE` | `token.json` | OAuth token storage |
| `GMAIL_DEFAULT_QUERY` | `from:linkedin.com` | Default Gmail search query |
| `GMAIL_MAX_RESULTS` | `10` | Maximum emails per request |

**Example configurations:**
```env
# LinkedIn job alerts only
GMAIL_DEFAULT_QUERY=from:noreply@linkedin.com

# All job-related emails  
GMAIL_DEFAULT_QUERY=subject:job

# Recent LinkedIn emails
GMAIL_DEFAULT_QUERY=from:linkedin.com newer_than:7d
```

## 🔍 Usage Examples

### Extract URLs from Gmail
```python
from gmail_module.gmail_api import GmailAPI

gmail = GmailAPI()
emails = gmail.list_messages(query="from:linkedin.com", max_results=20)

for email in emails:
    job_urls = gmail.extract_job_urls(email['id'])
    print(f"Found {len(job_urls)} job URLs in email")
```

### Scrape LinkedIn Jobs
```python
from scraper_module.job_scraper import JobScraper
import asyncio

async def scrape_jobs():
    urls = ["https://www.linkedin.com/jobs-guest/jobs/view/4267369043/"]
    
    async with JobScraper() as scraper:
        results = await scraper.scrape_multiple_jobs(urls)
        
    for job in results:
        print(f"Title: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Description: {len(job['description'])} characters")

asyncio.run(scrape_jobs())
```

## 🛡️ Technical Features

### Advanced Scraping Strategy
- **Fresh Browser Instances** - New browser for each job prevents state pollution
- **Popup Auto-Handling** - Detects and closes LinkedIn dialogs automatically
- **Smart "Show More" Logic** - Expands truncated job descriptions
- **Guest URL Conversion** - Scrapes without LinkedIn authentication
- **Optimized Timeouts** - Fast loading with graceful fallbacks

### Rate Limiting & Reliability
- **Conservative Delays** - 1-2 second delays between requests
- **Error Recovery** - Multiple fallback strategies for page loading
- **Browser Cleanup** - Automatic cleanup prevents memory leaks
- **Stealth Settings** - User agent and viewport configuration

## 🔬 Testing

### Run Tests
```bash
# Test Gmail functionality
python gmail_module/tests/

# Extract real URLs from your Gmail
python scraper_module/extract_and_save_real_urls.py

# Test scraper with real LinkedIn URLs
python scraper_module/test_with_real_urls.py

# View complete results and analysis
python scraper_module/show_full_results.py
```

### View Results
After running tests, check these files:
- `scraper_module/visible_urls/real_job_urls.json` - All extracted URLs
- `scraper_module/visible_urls/real_scraping_results.json` - Complete job data
- `scraper_module/visible_urls/real_urls_summary.txt` - Human-readable summary

## 🐛 Troubleshooting

### Gmail Issues
- **Missing credentials.json** → Download from Google Cloud Console
- **Authentication errors** → Delete `token.json` and re-authenticate  
- **No emails found** → Check `.env` GMAIL_DEFAULT_QUERY setting

### Scraping Issues
- **Browser not installed** → Run `playwright install`
- **Popup blocking scraper** → Fresh browser instances should handle this
- **Incomplete descriptions** → "Show more" handling extracts full content
- **Rate limiting** → Built-in delays prevent blocking

### Common Gmail Queries
```bash
# LinkedIn job alerts
GMAIL_DEFAULT_QUERY="from:noreply@linkedin.com subject:hiring"

# All LinkedIn emails
GMAIL_DEFAULT_QUERY="from:linkedin.com"

# Recent job emails
GMAIL_DEFAULT_QUERY="subject:job newer_than:3d"

# Specific companies
GMAIL_DEFAULT_QUERY="from:linkedin.com (Google OR Apple OR Microsoft)"
```

## 📈 Performance Metrics

Based on recent testing:
- ✅ **Success Rate**: 100% (3/3 jobs scraped successfully)
- ⚡ **Speed**: ~10-15 seconds per job (including popup handling)
- 📝 **Content Quality**: 3,226-7,211 characters per job description
- 🛡️ **Reliability**: No timeouts or conflicts with fresh browser strategy

## 🔒 Security & Privacy

- **OAuth2 Authentication** - Secure Gmail access with minimal scopes
- **Guest Mode Scraping** - No LinkedIn login required
- **Local Data Storage** - All data stays on your machine
- **No External APIs** - Direct scraping without third-party services
- **Credential Security** - Sensitive files excluded from Git

## 📝 License

This project is for educational and personal use. Please respect LinkedIn's terms of service and rate limits.

---

**Ready to extract and analyze your LinkedIn job opportunities!** 🚀 