# Gmail API Setup Guide

This guide will help you set up Gmail API access for the LinkedIn Matcher project.

## Step 1: Google Cloud Console Setup

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create or Select a Project**
   - Create a new project or select an existing one
   - Project name suggestion: "LinkedIn Email Matcher"

3. **Enable Gmail API**
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click on "Gmail API" and press "Enable"

## Step 2: Create Credentials

1. **Go to Credentials**
   - Navigate to "APIs & Services" > "Credentials"

2. **Create OAuth 2.0 Client ID**
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Desktop application"
   - Name: "LinkedIn Matcher Gmail Client"

3. **Download Credentials**
   - After creating, click the download button (⬇️)
   - Save the file as `credentials.json` in your project root directory

## Step 3: Configure Environment Variables

Create a `.env` file in your project root with the following content:

```env
# Gmail API Configuration
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json
GMAIL_DEFAULT_QUERY=from:linkedin.com
GMAIL_MAX_RESULTS=10
```

**Optional configurations:**
- **GMAIL_CREDENTIALS_FILE**: Path to credentials.json (default: `credentials.json`)
- **GMAIL_TOKEN_FILE**: Path to store OAuth token (default: `token.json`)
- **GMAIL_DEFAULT_QUERY**: Default search query (default: `from:linkedin.com`)
- **GMAIL_MAX_RESULTS**: Max emails per request (default: `10`)

**Alternative query examples:**
```env
# For LinkedIn notifications only
GMAIL_DEFAULT_QUERY=from:noreply@linkedin.com

# For job-related emails from any sender
GMAIL_DEFAULT_QUERY=subject:job

# For recent LinkedIn emails (last 7 days)
GMAIL_DEFAULT_QUERY=from:linkedin.com newer_than:7d
```

## Step 4: OAuth Consent Screen (if needed)

If you haven't set up the OAuth consent screen:

1. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" > "OAuth consent screen"
   - User Type: "External" (unless you have G Suite)
   - Fill in required fields:
     - App name: "LinkedIn Email Matcher"
     - User support email: your email
     - Developer contact: your email

2. **Add Scopes** (optional for testing)
   - You can skip this for now as we'll use default scopes

3. **Add Test Users**
   - Add your Gmail account as a test user
   - This allows you to test the app before it's verified

## Step 5: File Structure

Your project should have this structure:
```
linkedin_matcher/
├── .env                     # ← Create this with your configuration
├── credentials.json          # ← Download this from Google Cloud Console
├── token.json               # ← Will be created automatically after first auth
├── config.py
├── src/
│   └── gmail_api.py
├── tests/
│   ├── test_list_emails.py
│   └── test_read_email.py
└── requirements.txt
```

## Step 6: Test the Setup

1. **Run the email listing test:**
   ```bash
   python tests/test_list_emails.py
   ```

2. **First time authentication:**
   - A browser window will open
   - Sign in with your Gmail account
   - Grant permissions to the app
   - You should see "The authentication flow has completed"

3. **Run the email reading test:**
   ```bash
   python tests/test_read_email.py
   ```

## Important Notes

- **credentials.json**: Keep this file secure and don't commit it to version control
- **token.json**: Will be created automatically after first successful authentication
- **.env**: Contains your configuration - also keep secure and don't commit
- **Scopes**: We're using readonly access by default for safety
- **Rate Limits**: Gmail API has usage quotas - be mindful during development

## Troubleshooting

### "credentials.json not found"
- Make sure you downloaded the credentials file from Google Cloud Console
- Ensure it's named correctly and the path in `.env` is correct
- Check that `GMAIL_CREDENTIALS_FILE` in `.env` points to the right location

### "Access blocked: This app's request is invalid"
- Check that Gmail API is enabled in your Google Cloud project
- Verify OAuth consent screen is configured

### "Token has been expired or revoked"
- Delete `token.json` and run the test again
- You'll need to re-authenticate in the browser

### "No module named 'dotenv'"
- Make sure you installed all dependencies: `pip install -r requirements.txt`

## Next Steps

Once Gmail API is working:
1. ✅ List emails from Gmail
2. ✅ Read email content  
3. 🔄 Add job page scraping functionality
4. 🔄 Create FastMCP server
5. 🔄 Add user profile matching

## Security Notes

- The app requests minimal permissions (readonly + labels)
- Tokens are stored locally in `token.json`
- All sensitive data should be in `.env` (excluded from version control)
- Consider using environment variables for production deployment 