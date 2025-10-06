"""Unit tests for core components."""
import pytest
from pathlib import Path
from datetime import datetime
import yaml

# Test config.py
def test_config_paths():
    """Test that config paths are correctly defined."""
    from config import PROJECT_DIR, MEMORY_FILE, PROMPTS_FILE

    assert PROJECT_DIR.exists()
    assert PROMPTS_FILE.exists()
    assert PROMPTS_FILE.name == "prompts.yaml"
    assert MEMORY_FILE.name == "memory.json"


def test_load_prompts():
    """Test loading prompts from YAML file."""
    from config import load_prompts

    prompts = load_prompts()
    assert "system_prompt" in prompts
    assert "summarization_prompt" in prompts
    assert len(prompts["system_prompt"]) > 0
    assert "tools" in prompts["system_prompt"].lower()


def test_config_constants():
    """Test configuration constants."""
    from config import MISTRAL_MODEL, MEMORY_THRESHOLD_KB, MEMORY_KEEP_LAST_N

    assert MISTRAL_MODEL == "mistral-small-latest"
    assert MEMORY_THRESHOLD_KB == 50
    assert MEMORY_KEEP_LAST_N == 10


# Test tools.py
def test_get_date():
    """Test get_date tool returns a valid date string."""
    from tools import get_date

    date_str = get_date()
    assert isinstance(date_str, str)
    assert len(date_str) > 0
    # Should contain current year
    current_year = str(datetime.now().year)
    assert current_year in date_str



def test_tool_schemas():
    """Test that tool schemas are properly defined."""
    from tools import TOOL_SCHEMAS

    assert len(TOOL_SCHEMAS) == 6

    # Check get_date schema
    date_schema = next(t for t in TOOL_SCHEMAS if t["function"]["name"] == "get_date")
    assert date_schema["type"] == "function"
    assert len(date_schema["function"]["parameters"]["properties"]) == 0

    # Check access_gmail schema
    gmail_schema = next(t for t in TOOL_SCHEMAS if t["function"]["name"] == "access_gmail")
    assert gmail_schema["type"] == "function"
    assert len(gmail_schema["function"]["parameters"]["properties"]) == 0

    # Check send_mail_gmail schema
    send_schema = next(t for t in TOOL_SCHEMAS if t["function"]["name"] == "send_mail_gmail")
    assert send_schema["type"] == "function"
    assert "draft" in send_schema["function"]["parameters"]["properties"]
    assert "draft" in send_schema["function"]["parameters"]["required"]

    # Check get_google_contacts schema
    contacts_schema = next(t for t in TOOL_SCHEMAS if t["function"]["name"] == "get_google_contacts")
    assert contacts_schema["type"] == "function"
    assert len(contacts_schema["function"]["parameters"]["properties"]) == 0

    # Check add_google_contacts schema
    add_contacts_schema = next(t for t in TOOL_SCHEMAS if t["function"]["name"] == "add_google_contacts")
    assert add_contacts_schema["type"] == "function"
    assert "name" in add_contacts_schema["function"]["parameters"]["properties"]
    assert "email" in add_contacts_schema["function"]["parameters"]["properties"]
    assert "phone" in add_contacts_schema["function"]["parameters"]["properties"]
    assert set(add_contacts_schema["function"]["parameters"]["required"]) == {"name", "email"}

    # Check execute_browser_task schema
    browser_schema = next(t for t in TOOL_SCHEMAS if t["function"]["name"] == "execute_browser_task")
    assert browser_schema["type"] == "function"
    assert "task_description" in browser_schema["function"]["parameters"]["properties"]
    assert "expected_result" in browser_schema["function"]["parameters"]["properties"]
    assert set(browser_schema["function"]["parameters"]["required"]) == {"task_description", "expected_result"}


def test_execute_tool_get_date():
    """Test execute_tool with get_date."""
    from tools import execute_tool

    result = execute_tool("get_date", {})
    assert isinstance(result, str)
    assert len(result) > 0



def test_execute_tool_unknown():
    """Test execute_tool with unknown tool name."""
    from tools import execute_tool

    result = execute_tool("unknown_tool", {})
    assert "Error" in result
    assert "Unknown tool" in result


def test_tool_registry():
    """Test that tool registry contains all tools."""
    from tools import TOOL_FUNCTIONS

    assert "access_gmail" in TOOL_FUNCTIONS
    assert "send_mail_gmail" in TOOL_FUNCTIONS
    assert "get_google_contacts" in TOOL_FUNCTIONS
    assert "add_google_contacts" in TOOL_FUNCTIONS
    assert "execute_browser_task" in TOOL_FUNCTIONS
    assert "get_date" in TOOL_FUNCTIONS
    assert callable(TOOL_FUNCTIONS["access_gmail"])
    assert callable(TOOL_FUNCTIONS["send_mail_gmail"])
    assert callable(TOOL_FUNCTIONS["get_google_contacts"])
    assert callable(TOOL_FUNCTIONS["add_google_contacts"])
    assert callable(TOOL_FUNCTIONS["execute_browser_task"])
    assert callable(TOOL_FUNCTIONS["get_date"])


# Test access_mail_gmail.py
def test_clean_email_body():
    """Test email body cleaning function."""
    from services.google.gmail.access_mail_gmail import clean_email_body

    # Test HTML tag removal
    html_text = "<p>Hello <b>world</b></p>"
    assert clean_email_body(html_text) == "Hello world"

    # Test \r\n replacement
    windows_text = "Line1\r\nLine2\r\nLine3"
    assert clean_email_body(windows_text) == "Line1\nLine2\nLine3"

    # Test excessive newlines removal
    excessive_newlines = "Text1\n\n\n\n\nText2"
    assert clean_email_body(excessive_newlines) == "Text1\n\nText2"

    # Test whitespace trimming
    whitespace_text = "   Test content   "
    assert clean_email_body(whitespace_text) == "Test content"


def test_extract_email_body_no_parts():
    """Test email body extraction for messages without parts."""
    from services.google.gmail.access_mail_gmail import extract_email_body
    import base64

    # Create a simple message without parts
    test_content = "Simple email body"
    encoded_content = base64.urlsafe_b64encode(test_content.encode("utf-8")).decode("ASCII")

    msg = {
        "payload": {
            "body": {
                "data": encoded_content
            }
        }
    }

    result = extract_email_body(msg)
    assert result == test_content


def test_extract_email_body_with_parts():
    """Test email body extraction for messages with parts."""
    from services.google.gmail.access_mail_gmail import extract_email_body
    import base64

    # Create a message with parts
    test_content = "Email with parts"
    encoded_content = base64.urlsafe_b64encode(test_content.encode("utf-8")).decode("ASCII")

    msg = {
        "payload": {
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {
                        "data": encoded_content
                    }
                }
            ]
        }
    }

    result = extract_email_body(msg)
    assert result == test_content


def test_extract_email_body_no_content():
    """Test email body extraction when no content is available."""
    from services.google.gmail.access_mail_gmail import extract_email_body

    msg = {
        "payload": {
            "body": {}
        }
    }

    result = extract_email_body(msg)
    assert "No body content available" in result


def test_get_message_details_error_handling():
    """Test that get_message_details handles errors gracefully."""
    from services.google.gmail.access_mail_gmail import get_message_details
    from unittest.mock import Mock

    # Create a mock service that raises an exception
    mock_service = Mock()
    mock_service.users().messages().get().execute.side_effect = Exception("API Error")

    result = get_message_details(mock_service, "test_id", 1, 10)

    assert result["id"] == "test_id"
    assert "error" in result
    assert result["sender"] == "Error"
    assert "Error retrieving email" in result["subject"]


def test_authenticate_gmail_scopes():
    """Test that Gmail API scopes are correctly defined."""
    from services.google.gmail.access_mail_gmail import SCOPES

    assert len(SCOPES) == 2
    assert "https://www.googleapis.com/auth/gmail.readonly" in SCOPES
    assert "https://www.googleapis.com/auth/gmail.send" in SCOPES


def test_days_window_constant():
    """Test that DAYS_WINDOW constant is set correctly."""
    from services.google.gmail.access_mail_gmail import DAYS_WINDOW

    assert DAYS_WINDOW == 7
    assert isinstance(DAYS_WINDOW, int)


# Test write_mail_gmail.py
def test_extract_email_details_valid():
    """Test email details extraction from valid draft."""
    from services.google.gmail.write_mail_gmail import extract_email_details

    draft = """A : test@example.com
Objet : Test Subject
Corps : This is the email body"""

    to, subject, body = extract_email_details(draft)
    assert to == "test@example.com"
    assert subject == "Test Subject"
    assert body == "This is the email body"


def test_extract_email_details_with_bot_question():
    """Test email details extraction removes bot question."""
    from services.google.gmail.write_mail_gmail import extract_email_details

    draft = """A : test@example.com
Objet : Test
Corps : Email body
Souhaitez-vous que je l'envoie tel quel ?"""

    to, subject, body = extract_email_details(draft)
    assert body == "Email body"
    assert "Souhaitez" not in body


def test_extract_email_details_with_special_spaces():
    """Test email details extraction with non-breaking spaces."""
    from services.google.gmail.write_mail_gmail import extract_email_details

    # Using non-breaking space character
    draft = "A\u00A0:\u00A0test@example.com\nObjet\u00A0:\u00A0Test\nCorps\u00A0:\u00A0Body"

    to, subject, body = extract_email_details(draft)
    assert to == "test@example.com"
    assert subject == "Test"
    assert body == "Body"


def test_extract_email_details_invalid():
    """Test email details extraction with invalid format."""
    from services.google.gmail.write_mail_gmail import extract_email_details

    draft = "Invalid draft format"

    with pytest.raises(ValueError, match="Format de brouillon invalide"):
        extract_email_details(draft)


# Test add_google_contacts.py
def test_extract_contact_details():
    """Test contact details extraction."""
    from services.google.contacts.add_google_contacts import extract_contact_details

    contact_info = """Nom : John Doe
Email : john@example.com
Phone : +33123456789"""

    name, email, phone = extract_contact_details(contact_info)
    assert name == "John Doe"
    assert email == "john@example.com"
    assert phone == "+33123456789"


def test_extract_contact_details_missing_phone():
    """Test contact extraction with missing phone."""
    from services.google.contacts.add_google_contacts import extract_contact_details

    contact_info = """Nom : Jane Doe
Email : jane@example.com"""

    name, email, phone = extract_contact_details(contact_info)
    assert name == "Jane Doe"
    assert email == "jane@example.com"
    assert phone is None


def test_add_google_contacts_scopes():
    """Test that Google Contacts add scopes are correctly defined."""
    from services.google.contacts.add_google_contacts import SCOPES

    assert len(SCOPES) == 1
    assert "https://www.googleapis.com/auth/contacts" in SCOPES


# Test get_google_contacts.py
def test_get_google_contacts_scopes():
    """Test that Google Contacts get scopes are correctly defined."""
    from services.google.contacts.get_google_contacts import SCOPES

    assert len(SCOPES) == 1
    assert "https://www.googleapis.com/auth/contacts.readonly" in SCOPES


# Test browser_agent.py
def test_execute_browser_task_returns_dict():
    """Test that execute_browser_task returns expected structure."""
    from services.browser.browser_agent import execute_browser_task
    from unittest.mock import patch, MagicMock

    # Mock the run_task function to avoid actual browser execution
    with patch('services.browser.browser_agent.run_task') as mock_run:
        mock_result = MagicMock()
        mock_result.final_result.return_value = "Test result"
        mock_run.return_value = mock_result

        result = execute_browser_task("test task", "expected result")

        assert isinstance(result, dict)
        assert "status" in result
        assert "output" in result
        assert "expected_result" in result
        assert result["status"] == "completed"
        assert result["expected_result"] == "expected result"


def test_execute_browser_task_handles_errors():
    """Test that execute_browser_task handles errors gracefully."""
    from services.browser.browser_agent import execute_browser_task
    from unittest.mock import patch

    # Mock the run_task function to raise an exception
    with patch('services.browser.browser_agent.run_task') as mock_run:
        mock_run.side_effect = Exception("Browser error")

        result = execute_browser_task("test task", "expected result")

        assert result["status"] == "error"
        assert "Browser error" in result["output"]
