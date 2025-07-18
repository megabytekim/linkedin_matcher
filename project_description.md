Gmail MCP Server — FastMCP One-Page Project Brief

## Purpose
Build a Gmail MCP server that a GPT-based host can call to ★ list recent LinkedIn emails ★ read full content ★ (optionally) scrape external job pages ★ label matching mails Important, after explicit user OK.

The project showcases how the Model Context Protocol cleanly separates read-only resources from side-effect tools, and how FastMCP turns plain Python functions into an MCP server with almost no boilerplate.

## Technology Stack

| Layer        | Choice                                                   | Reason                                                                   |
| ------------ | -------------------------------------------------------- | ------------------------------------------------------------------------ |
| MCP Server   | **FastMCP 2.x**                                          | Decorators + auto-schema; now ships OpenAI/Claude bridge helpers.        |
| LLM Host     | GPT-4o (function calling) **OR** Claude Desktop (native) | GPT shows bridge workflow; Claude demonstrates zero-glue auto-discovery. |
| Gmail Access | **Gmail REST API** via `google-api-python-client`        | Easiest OAuth flow, rich label API.                                      |
| Job Scraping | **Playwright** + **BeautifulSoup**                       | Robust browser automation + HTML parsing for LinkedIn job pages.         |
| Local Dev    | **Cursor** IDE                                           | Python-first, fast AI-assist coding.                                     |

## Architecture

```
┌──────────┐     JSON-RPC        ┌────────────────┐
│ GPT Host │  ↔ (bridge if GPT) ↔│ FastMCP Server │
└──────────┘                     │  server.py     │
      ▲                          └───────▲────────┘
      │ tool call                       │ 
      ▼                                 ▼
   User chat                   ┌─────────────────┐
                               │ Internal Modules│
                               │ - gmail_module/ │
                               │ - scraper_module│
                               └─────────────────┘
```

## MCP Interface Specification

| URI / Name                          | Type         | Params                                | Description                                                               |
| ----------------------------------- | ------------ | ------------------------------------- | ------------------------------------------------------------------------- |
| `gmail://inbox{?query,max_results}` | **Resource** | `query` (Gmail search), `max_results` | List message IDs + subject/sender/date/snippet.                           |
| `gmail://message/{id}`              | **Resource** | `id`                                  | Return plain-text body.                                                   |
| `gmail://message/{id}/job_page`     | **Resource** | `id`                                  | Follow first "View job" link; scrape first ≈2 kB text.                    |
| `user://profile`                    | **Resource** | –                                     | Static JSON/text of user skills & prefs.                                  |
| `label_email`                       | **Tool**     | `email_id`, `label="Important"`       | Add Gmail label **after user confirmation**. *(Only mutating op exposed)* |
| `extract_job_urls`                  | **Tool**     | `email_id`                            | Extract job URLs from email content.                                      |
| `scrape_job_page`                   | **Tool**     | `job_url`, `max_content_length`       | Scrape LinkedIn job page for detailed information.                        |

## Implementation Status
- ✅ **Phase 1**: Gmail API integration complete
- ✅ **Phase 2**: Job URL extraction and scraping working
- ✅ **Phase 3**: FastMCP server structure implemented
- 🔄 **Phase 4**: Testing and LLM host integration
- 🔄 **Phase 5**: User profile matching logic

