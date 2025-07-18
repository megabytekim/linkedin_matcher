#!/usr/bin/env python3
"""Test script for listing Gmail emails."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gmail_module.gmail_api import GmailAPI
from config import DEFAULT_QUERY, DEFAULT_MAX_RESULTS


def test_list_emails():
    """Test listing emails from Gmail."""
    print("🔍 Testing Gmail Email Listing...")
    print("=" * 50)
    
    try:
        # Initialize Gmail API
        gmail = GmailAPI()
        
        # Test 1: List all recent emails (no filter)
        print("\n📧 Test 1: List recent emails (any sender)")
        print("-" * 40)
        recent_emails = gmail.list_messages(query="", max_results=5)
        
        for i, email in enumerate(recent_emails, 1):
            print(f"{i}. From: {email['from']}")
            print(f"   Subject: {email['subject']}")
            print(f"   Date: {email['date']}")
            print(f"   Snippet: {email['snippet'][:100]}...")
            print()
        
        # Test 2: List LinkedIn emails specifically
        print("\n🔗 Test 2: List LinkedIn emails")
        print("-" * 40)
        linkedin_emails = gmail.list_messages(query=DEFAULT_QUERY, max_results=DEFAULT_MAX_RESULTS)
        
        if linkedin_emails:
            for i, email in enumerate(linkedin_emails, 1):
                print(f"{i}. From: {email['from']}")
                print(f"   Subject: {email['subject']}")
                print(f"   Date: {email['date']}")
                print(f"   ID: {email['id']}")
                print(f"   Snippet: {email['snippet'][:100]}...")
                print()
        else:
            print("No LinkedIn emails found. You may need to:")
            print("- Check if you have emails from LinkedIn")
            print("- Modify the query in config.py")
            print("- Make sure your Gmail account has some job-related emails")
        
        # Test 3: Custom query test
        print("\n🔍 Test 3: Custom query - emails with 'job' in subject")
        print("-" * 40)
        job_emails = gmail.list_messages(query="subject:job", max_results=3)
        
        for i, email in enumerate(job_emails, 1):
            print(f"{i}. From: {email['from']}")
            print(f"   Subject: {email['subject']}")
            print(f"   Date: {email['date']}")
            print()
        
        print("✅ Email listing tests completed successfully!")
        
        # Return first LinkedIn email ID for further testing
        if linkedin_emails:
            return linkedin_emails[0]['id']
        elif recent_emails:
            return recent_emails[0]['id']
        else:
            return None
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return None


if __name__ == "__main__":
    test_email_id = test_list_emails()
    if test_email_id:
        print(f"\n📋 Sample email ID for further testing: {test_email_id}")
    else:
        print("\n⚠️ No emails found for further testing") 