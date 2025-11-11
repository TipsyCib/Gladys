import base64
import os
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from config import GOOGLE_GMAIL_ACCESS_CREDENTIALS, GOOGLE_GMAIL_ACCESS_TOKEN, GMAIL_MAIL_USER, GMAIL_MAIL_TEST_RECIPIENT

def authenticate_gmail():
    """Authentifie l'utilisateur auprès de l'API Gmail."""
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = None
    token_file = GOOGLE_GMAIL_ACCESS_TOKEN
    credentials_file = GOOGLE_GMAIL_ACCESS_CREDENTIALS

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=8080)

        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

def send_email(service, sender, to, subject, body):
    """Envoie un e-mail avec l'API Gmail."""
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(body)
    message.attach(msg)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        send_message = service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
        print(f"Message Id: {send_message['id']}")
    except Exception as e:
        print("Erreur lors de l'envoi de l'email :", e)

def extract_email_details(draft: str):
    """
    Extrait (destinataire, sujet, corps) d'un brouillon tolérant :
    - 'A :' / 'Objet :' / 'Corps :' avec espaces insécables et variantes de ':'.
    - Corps pouvant démarrer sur la même ligne que 'Corps :' OU à la ligne suivante.
    - Retire toute phrase finale du type "Souhaitez-vous que je l'envoie tel quel..." ajoutée par l'assistant.
    """
    t = draft or ""
    # Tolérer espaces classiques + insécables + fine-insécables, et le deux-points pleine chasse
    space = r"[ \t\u00A0\u202F]*"

    # A / Objet
    m_to = re.search(rf"(?mi)^\s*A{space}:{space}(.+)$", t)
    m_subj = re.search(rf"(?mi)^\s*Objet{space}:{space}(.+)$", t)

    # Corps : capturer TOUT ce qui suit, y compris si ça commence sur la même ligne
    # (?m) = multiline (^/$ par ligne), (?s) = dotall ('.' inclut les retours ligne)
    m_body = re.search(rf"(?ms)^\s*Corps{space}:{space}(.*)$", t)

    if not (m_to and m_subj and m_body):
        raise ValueError("Format de brouillon invalide ou incomplet (A/Objet/Corps non trouvés).")

    to = m_to.group(1).strip()
    subject = m_subj.group(1).strip()
    body = m_body.group(1).strip()

    # Supprimer la question finale ajoutée par le bot, si présente
    # On enlève à partir de "Souhaitez-vous..." (toutes variantes possibles)
    body = re.split(r"(?i)Souhaitez[\s–—-]*vous.*", body)[0].rstrip()

    return to, subject, body

def send_email_from_draft(draft: str, sender: str = GMAIL_MAIL_USER):
    """
    Combine extract_email_details et send_email.
    Extrait les détails depuis un brouillon et envoie l'email directement.
    Authentifie automatiquement avec Gmail.
    """
    service = authenticate_gmail()
    to, subject, body = extract_email_details(draft)
    send_email(service, sender, to, subject, body)
    return f"Email envoyé avec succès à {to}"



if __name__ == '__main__':
    service = authenticate_gmail()
    send_email(service, GMAIL_MAIL_USER, GMAIL_MAIL_TEST_RECIPIENT, "Test", "Ceci est un test.")
