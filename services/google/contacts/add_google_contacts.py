import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import GOOGLE_CONTACTS_CREDENTIALS, GOOGLE_ADD_CONTACTS_TOKEN

# Scopes requis pour accéder aux contacts
SCOPES = ['https://www.googleapis.com/auth/contacts']

def authenticate_google_contacts():
    """
    Authentifie avec l'API Google et retourne un objet service pour Google People.
    Réutilise le token existant si disponible.
    """
    creds = None
    token_file = GOOGLE_ADD_CONTACTS_TOKEN
    credentials_file = GOOGLE_CONTACTS_CREDENTIALS

    # Charger les identifiants existants si disponibles
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        print("Utilisation des identifiants existants")

        # Rafraîchir le token s'il est expiré
        if creds.expired and creds.refresh_token:
            print("Rafraîchissement du token expiré")
            creds.refresh(Request())
            with open(token_file, "w") as token:
                token.write(creds.to_json())
    else:
        print("Aucun token existant trouvé. Démarrage du processus d'authentification...")
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file, SCOPES, redirect_uri='http://localhost:8080'
        )

        creds = flow.run_local_server(
            port=8080, access_type='offline', prompt='consent'
        )

        # Enregistrer les identifiants pour un usage futur
        with open(token_file, "w") as token:
            token.write(creds.to_json())
        print("Authentification terminée et enregistrée")

    # Créer le service Google People
    return build('people', 'v1', credentials=creds)

def create_google_contact(name, email, phone):
    service = authenticate_google_contacts()

    contact_body = {
        "names": [{"givenName": name}],
        "emailAddresses": [{"value": email}],
        "phoneNumbers": [{"value": phone}]
    }

    try:
        contact = service.people().createContact(body=contact_body).execute()
        print(f"Contact créé : {contact.get('resourceName')}")
        return True
    except Exception as e:
        print(f"Erreur lors de la création du contact : {e}")
        raise

import re

def extract_contact_details(contact_info):
    """
    Extrait le nom, l'email et le numéro de téléphone d'un contact.
    """

    # Modèles pour extraire les informations
    name_pattern = r"Nom\s*:\s*(.+)"
    email_pattern = r"Email\s*:\s*(\S+)"
    phone_pattern = r"Phone\s*:\s*(\+?\d+)"

    # Recherche des informations
    name_match = re.search(name_pattern, contact_info, re.IGNORECASE)
    email_match = re.search(email_pattern, contact_info, re.IGNORECASE)
    phone_match = re.search(phone_pattern, contact_info, re.IGNORECASE)

    # Extraction avec gestion des cas où un champ est manquant
    name = name_match.group(1).strip() if name_match else None
    email = email_match.group(1).strip() if email_match else None

    phone = phone_match.group(1).strip() if phone_match else None

    return name, email, phone

def add_google_contacts(name=None, email=None, phone=None, contact_info=None):
    """
    Crée un contact dans Google Contacts.
    Peut accepter soit des paramètres individuels (name, email, phone)
    soit un texte à parser (contact_info).
    """
    #print(f"[DEBUG] Paramètres reçus - name: {name}, email: {email}, phone: {phone}, contact_info: {contact_info}")

    # Si contact_info est fourni, extraire les détails
    if contact_info:
        name, email, phone = extract_contact_details(contact_info)
        #print(f"[DEBUG] Extraction - Nom: {name}, Email: {email}, Phone: {phone}")

    if not name:
        raise ValueError("Le nom du contact est requis")

    try:
        create_google_contact(name, email, phone)
        return f'{name} a bien été enregistré(e).'
    except Exception as e:
        print(f"[ERROR] Échec de l'ajout du contact: {str(e)}")
        import traceback
        traceback.print_exc()
        raise



if __name__ == '__main__':
    create_google_contact("Jean Duponteau", "jean.duponteau@example.com", "+33123456789")









