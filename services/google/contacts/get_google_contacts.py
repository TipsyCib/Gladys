import json
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import GOOGLE_CONTACTS_CREDENTIALS, GOOGLE_CONTACTS_TOKEN

# Scopes requis pour accéder aux contacts
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']

def authenticate_google():
    """
    Authentifie avec l'API Google et retourne un objet service pour Google People.
    Réutilise le token existant si disponible.
    """
    creds = None
    token_file = GOOGLE_CONTACTS_TOKEN
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

def get_google_contacts():
    service = authenticate_google()

    # Récupération des contacts
    results = service.people().connections().list(
        resourceName='people/me',
        pageSize=2000,  # Nombre maximum de contacts à récupérer
        personFields='names,emailAddresses,phoneNumbers'
    ).execute()

    contacts = results.get('connections', [])

    # Extraction des informations pertinentes
    contact_list = []
    for contact in contacts:
        contact_info = {
            'name': contact.get('names', [{}])[0].get('displayName', 'Inconnu'),
            'email': contact.get('emailAddresses', [{}])[0].get('value', 'Non fourni'),
            'phone': contact.get('phoneNumbers', [{}])[0].get('value', 'Non fourni')
        }
        contact_list.append(contact_info)

    return contact_list

if __name__ == '__main__':
    contacts = get_google_contacts()
    print(contacts)
