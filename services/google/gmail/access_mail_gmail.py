import os
import base64
import json
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from typing import List, Dict
from config import GOOGLE_GMAIL_ACCESS_CREDENTIALS, GOOGLE_GMAIL_ACCESS_TOKEN

# Define the required scopes for Gmail API
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]

# Fenêtre de recherche en jours
DAYS_WINDOW = 7  # 7 derniers jours


def authenticate_gmail():
    """
    Authenticate with Gmail API and return a service object.
    Reuses existing token.json if available.
    """
    creds = None
    token_file = GOOGLE_GMAIL_ACCESS_TOKEN
    credentials_file = GOOGLE_GMAIL_ACCESS_CREDENTIALS

    # Load existing credentials if available
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        if __name__ == '__main__':
            print("Using existing credentials from token file")
        
        # Refresh token if expired
        if creds.expired and creds.refresh_token:
            if __name__ == '__main__':
                print("Refreshing expired token")
            creds.refresh(Request())
            with open(token_file, "w") as token:
                token.write(creds.to_json())
    else:
        if __name__ == '__main__':
            # If no token file, run the OAuth flow
            print("No existing token found. Starting authentication flow...")
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file, 
            SCOPES,
            redirect_uri='http://localhost:8080'
        )
        
        # Run the OAuth flow with access_type=offline to get refresh token
        creds = flow.run_local_server(
            port=8080,
            access_type='offline',
            prompt='consent'
        )
        
        # Save credentials for future use
        with open(token_file, "w") as token:
            token.write(creds.to_json())
        if __name__ == '__main__':
            print("New authentication completed and saved")
    
    # Create the Gmail service
    service = build("gmail", "v1", credentials=creds)
    return service


def list_messages(service, query: str = "") -> List[Dict]:
    """
    List all email messages matching the query by paginating through the Gmail API.
    
    Args:
        service: Authenticated Gmail service.
        query: Gmail search query (e.g., "from:example@gmail.com").
    
    Returns:
        List of message metadata (IDs).
    """
    messages = []
    try:
        if __name__ == '__main__':
            print("Fetching email list...")
        response = service.users().messages().list(userId="me", q=query).execute()
        
        while "messages" in response:
            batch_size = len(response["messages"])
            messages.extend(response["messages"])
            if __name__ == '__main__':
                print(f"Retrieved {len(messages)} message IDs so far...")
            
            # Check if there is another page of messages
            if "nextPageToken" in response:
                page_token = response["nextPageToken"]
                response = service.users().messages().list(userId="me", q=query, pageToken=page_token).execute()
            else:
                break  # No more messages
        if __name__ == '__main__':      
            print(f"Total emails found: {len(messages)}")
        return messages
    except Exception as e:
        if __name__ == '__main__':
            print(f"Error fetching messages: {e}")
        return []


def get_message_details(service, msg_id: str, index: int, total: int) -> Dict:
    """
    Retrieve details of a specific email.
    
    Args:
        service: Authenticated Gmail service.
        msg_id: ID of the email message.
        index: Current processing index for progress reporting.
        total: Total number of messages for progress reporting.
    
    Returns:
        Dictionary containing email details (sender, subject, date, body).
    """
    try:
        if index % 10 == 0:  # Show progress every 10 emails
            print(f"Processing email {index}/{total}...")
            
        msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
        headers = msg["payload"]["headers"]

        # Extract required fields
        email_data = {
            "id": msg_id,
            "sender": next((h["value"] for h in headers if h["name"].lower() == "from"), "Unknown"),
            "subject": next((h["value"] for h in headers if h["name"].lower() == "subject"), "No Subject"),
            "date": next((h["value"] for h in headers if h["name"].lower() == "date"), "Unknown"),
            "body": extract_email_body(msg),
        }
        return email_data
    except Exception as e:
        if __name__ == '__main__':
            print(f"Error fetching email details for message {index}/{total} (ID: {msg_id}): {e}")
        return {
            "id": msg_id,
            "error": str(e),
            "sender": "Error",
            "subject": "Error retrieving email",
            "date": "Unknown",
            "body": "Error retrieving email body"
        }


def clean_email_body(text: str) -> str:
    """
    Clean and normalize email body text.

    Args:
        text: Raw email body text.

    Returns:
        Cleaned email body text.
    """
    # Remove HTML tags if present
    text = re.sub(r'<[^>]+>', '', text)

    # Replace \r\n with \n
    text = text.replace('\r\n', '\n')

    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text


def extract_email_body(msg) -> str:
    """
    Extract email body from Gmail API response.

    Args:
        msg: Gmail message object.

    Returns:
        Decoded email body as a string.
    """
    try:
        payload = msg["payload"]

        # Handle case where message has no parts (plain text email)
        if "parts" not in payload:
            # Check if body contains data
            if "data" in payload.get("body", {}):
                body_data = payload["body"]["data"]
                raw_body = base64.urlsafe_b64decode(body_data.encode("ASCII")).decode("utf-8", errors="replace").strip()
                return clean_email_body(raw_body)
            return "No body content available."

        # Function to recursively search for text parts
        def find_text_part(parts):
            for part in parts:
                mime_type = part.get("mimeType", "")

                # If it's plain text, return the data
                if mime_type == "text/plain" and "data" in part.get("body", {}):
                    return part["body"]["data"]

                # If this part has its own parts, search them recursively
                if "parts" in part:
                    recursive_result = find_text_part(part["parts"])
                    if recursive_result:
                        return recursive_result

            return None

        # Find a text part in the message
        text_data = find_text_part(payload["parts"])

        # If we found text data, decode it
        if text_data:
            raw_body = base64.urlsafe_b64decode(text_data.encode("ASCII")).decode("utf-8", errors="replace").strip()
            return clean_email_body(raw_body)

        # If no plain text was found, try to use the first part's data as fallback
        if "data" in payload["parts"][0].get("body", {}):
            body_data = payload["parts"][0]["body"]["data"]
            raw_body = base64.urlsafe_b64decode(body_data.encode("ASCII")).decode("utf-8", errors="replace").strip()
            return clean_email_body(raw_body)

        return "No text content found in this email."

    except Exception as e:
        return f"Could not extract email body: {e}"
    


def access_gmail():
    """Main function to run the Gmail API operations with no user input."""
    try:
        # Authenticate and get service
        service = authenticate_gmail()
        print("Successfully connected to Gmail API!")

        # Requête: uniquement reçus dans l'inbox, pas envoyés par moi, et sur les 7 derniers jours
        query = f"in:inbox -from:me newer_than:{DAYS_WINDOW}d"

        # Fetch all messages
        messages = list_messages(service, query=query)

        if not messages:
            if __name__ == '__main__':
                print("No emails found in your account for the last 7 days.")
            return []

        # Process all emails
        email_details = []
        total_messages = len(messages)

        print(f"Starting to process {total_messages} emails...")
        for i, msg in enumerate(messages):
            details = get_message_details(service, msg["id"], i+1, total_messages)
            email_details.append(details)

        if __name__ == '__main__':
            print(json.dumps(email_details, indent=2, ensure_ascii=False))

        return email_details

    except Exception as e:
        print(f"An error occurred: {e}")
        return []


if __name__ == "__main__":
    access_gmail()
