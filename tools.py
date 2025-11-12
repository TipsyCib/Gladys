"""Tool definitions and execution for the agentic chatbot."""
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict
from services.google.gmail.access_mail_gmail import access_gmail
from services.google.gmail.write_mail_gmail import extract_email_details, send_email_from_draft
from services.google.contacts.get_google_contacts import get_google_contacts
from services.google.contacts.add_google_contacts import add_google_contacts
from services.browser.browser_agent import execute_browser_task
from services.light.control_light import control_lampe


# Tool implementations


def get_date() -> str:
    """Get today's date in a readable format.

    Returns:
        Today's date as a formatted string
    """
    return datetime.now().strftime("%A, %B %d, %Y")


# Tool registry mapping tool names to functions
TOOL_FUNCTIONS: Dict[str, Callable] = {
    "get_date": get_date,
    "access_gmail": access_gmail,
    "send_mail_gmail": send_email_from_draft,
    "get_google_contacts": get_google_contacts,
    "add_google_contacts": add_google_contacts,
    "execute_browser_task": execute_browser_task,
    "control_light": control_lampe,


}


# Tool schemas for Mistral API (following OpenAI function calling format)
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_date",
            "description": "Get today's date in a readable format",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "access_gmail",
            "description": "Access Gmail to read emails",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_mail_gmail",
            "description": "Send an email using a draft text",
            "parameters": {
                "type": "object",
                "properties": {
                    "draft": {
                        "type": "string",
                        "description": (
                            "Draft email text containing recipient, subject, and body. "
                            "Format should include 'A : <recipient>', 'Objet : <subject>', and 'Corps : <body>'."
                        )
                    }
                },
                "required": ["draft"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_google_contacts",
            "description": "Retrieve all Google Contacts to find email addresses. MUST be called when the user mentions a contact by NAME (not email address) to get their email before sending a message. Always call this first when user says 'dis à X', 'envoie à X', 'contacte X' where X is a person's name.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_google_contacts",
            "description": "Add a new contact to Google Contacts",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the contact"
                    },
                    "email": {
                        "type": "string",
                        "description": "Email address of the contact"
                    },
                    "phone": {
                        "type": "string",
                        "description": "Phone number of the contact (optional)"
                    }
                },
                "required": ["name", "email"]
            }
        }
    },

    {
                "type": "function",
                "function": {
                    "name": "execute_browser_task",
                    "description": "Exécute une tâche automatisée dans un navigateur web en utilisant Browser Use avec Gemini. Utilise cette fonction quand l'utilisateur demande d'aller sur un site, chercher des informations, remplir des formulaires, ou toute action nécessitant un navigateur.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_description": {
                                "type": "string",
                                "description": "Description détaillée et précise de la tâche à accomplir dans le navigateur. Doit inclure les URLs, les étapes exactes, et ce qu'il faut chercher ou faire."
                            },
                            "expected_result": {
                                "type": "string",
                                "description": "Ce que l'utilisateur attend comme résultat (ex: 'trouver le prix', 'télécharger le fichier', 'récupérer les informations')"
                            }
                        },
                        "required": ["task_description", "expected_result"]
                    }
                }
            },

    {
        "type": "function",
        "function": {
            "name": "control_light",
            "description": "Contrôle une lampe intelligente Tapo (allumer, éteindre, changer la luminosité ou la couleur)",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": [
                            "on", "off",
                            "brightness_min", "brightness_moyenne", "brightness_max", "brightness_porcentage",
                            "color_indigo", "color_blue", "color_rouge", "color_violet",
                            "color_vert", "color_rose", "color_white", "color_warm"
                        ],
                        "description": "L'action à effectuer sur la lampe"
                    },
                    "value": {
                        "type": "integer",
                        "description": "Valeur de luminosité en pourcentage (1-100), uniquement pour brightness_porcentage"
                    }
                },
                "required": ["action"]
            }
        }
    }
]


def execute_tool(tool_name: str, tool_args: Dict[str, Any]) -> str:
    """Execute a tool by name with given arguments.

    Args:
        tool_name: Name of the tool to execute
        tool_args: Dictionary of arguments to pass to the tool

    Returns:
        Result of the tool execution as a string
    """
    if tool_name not in TOOL_FUNCTIONS:
        return f"Error: Unknown tool '{tool_name}'"

    try:
        tool_func = TOOL_FUNCTIONS[tool_name]

        # Check if the function is a coroutine (async function)
        if asyncio.iscoroutinefunction(tool_func):
            # Run async function in event loop
            result = asyncio.run(tool_func(**tool_args))
        else:
            # Run sync function normally
            result = tool_func(**tool_args)

        return str(result)
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"
