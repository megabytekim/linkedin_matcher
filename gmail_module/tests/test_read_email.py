#!/usr/bin/env python3
"""Test script for reading Gmail email content."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from gmail_module.gmail_api import GmailAPI
from config import DEFAULT_QUERY


def test_read_email():
    """Test reading email content from Gmail."""
    print("📖 Testing Gmail Email Content Reading...")
    print("=" * 50)
    
    try:
        # Initialize Gmail API
        gmail = GmailAPI()
        
        # First, get some emails to read
        print("\n🔍 Step 1: Finding emails to read...")
        emails = gmail.list_messages(query=DEFAULT_QUERY, max_results=3)
        
        if not emails:
            # Fallback to any recent emails
            print("No LinkedIn emails found, trying recent emails...")
            emails = gmail.list_messages(query="", max_results=3)
        
        if not emails:
            print("❌ No emails found to test reading functionality")
            return
        
        # Test reading content for each email
        for i, email in enumerate(emails, 1):
            print(f"\n📧 Test {i}: Reading email content")
            print("-" * 40)
            print(f"From: {email['from']}")
            print(f"Subject: {email['subject']}")
            print(f"Email ID: {email['id']}")
            print()
            
            # Get full content
            content = gmail.get_message_content(email['id'])
            
            if content:
                print(f"✅ Successfully retrieved content ({len(content)} characters)")
                print("\n📄 First 500 characters of content:")
                print("-" * 40)
                print(content[:500])
                if len(content) > 500:
                    print("\n... (content truncated)")
                print()
                
                # Basic content analysis
                print("📊 Content Analysis:")
                print(f"- Total characters: {len(content)}")
                print(f"- Lines: {len(content.splitlines())}")
                print(f"- Words: {len(content.split())}")
                
                # Look for job-related keywords
                job_keywords = ['job', 'position', 'role', 'opportunity', 'career', 'hiring', 'interview']
                found_keywords = [kw for kw in job_keywords if kw.lower() in content.lower()]
                if found_keywords:
                    print(f"- Job-related keywords found: {', '.join(found_keywords)}")
                else:
                    print("- No job-related keywords found")
                
            else:
                print("❌ Failed to retrieve email content")
            
            print("\n" + "=" * 50)
        
        print("\n✅ Email reading tests completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")


def test_read_specific_email(email_id: str):
    """Test reading a specific email by ID."""
    print(f"\n📖 Testing reading specific email: {email_id}")
    print("-" * 50)
    
    try:
        gmail = GmailAPI()
        content = gmail.get_message_content(email_id)
        
        if content:
            print(f"✅ Content retrieved successfully!")
            print(f"📄 Content preview (first 200 chars):")
            print(content[:200])
            if len(content) > 200:
                print("...")
            return content
        else:
            print("❌ Failed to retrieve content")
            return None
            
    except Exception as e:
        print(f"❌ Error reading email: {e}")
        return None


if __name__ == "__main__":
    # Test general email reading
    test_read_email()
    
    # Test with specific email ID if provided as command line argument
    if len(sys.argv) > 1:
        email_id = sys.argv[1]
        test_read_specific_email(email_id) 