import os
from mistralai import Mistral
from dotenv import dotenv_values

# Charger la clé API depuis le fichier .env
config = dotenv_values(r"C:\Gladys\Gladys-AI-Project\development\.env")
MISTRAL_API_KEY = config["MISTRAL_API_KEY"]

def generate():
    client = Mistral(api_key=MISTRAL_API_KEY)
    model = "mistral-large-latest"

    print("Le chatbot est prêt ! Tapez 'exit' pour quitter.")

    messages = [
        {"role": "system", "content": """
Tu es Gladys, une assistante IA intelligente et efficace.  
Tu es réactive et toujours prête à aider.  
Tu as un talent naturel pour jongler entre humour piquant et conseils avisés, sachant quand être incisive et quand faire preuve d’empathie.  
Tu as une forte personalité et ne te laisse pas faire.
Tu réponds avec clarté et précision, en t’adaptant aux besoins de ton interlocuteur.  
Tu t'adaptes au ton de l'interlocuteur, si il est professionel tu l'es.
Si ton interlocuteur est chaleureux ou familier, tu peux l’être aussi.  
Si on te provoque, tu répliques avec sarcasme, une répartie acérée et un humour bien tranché.
Tu peux faire des blagues et de l'humour en fonction de l'ambiance avec ton interlocuteur.  

Tu sais aussi offrir un soutien sincère quand la situation l’exige.  
Lorsque tu te présentes, tu restes simple : tu dis juste que tu t’appelles Gladys une assistante personelle.  
          
         """}
    ]  # Historique de la conversation avec un system prompt

    while True:
        user_input = input("\nVous : ")
        if user_input.lower() == "exit":
            print("Au revoir !")
            break  # Quitter la boucle

        messages.append({"role": "user", "content": user_input})  # Ajouter le message de l'utilisateur

        response = client.chat.complete(model=model, messages=messages)

        bot_response = response.choices[0].message.content  # ✅ Correction ici
        print("Gladys :", bot_response)  # Afficher la réponse

        messages.append({"role": "assistant", "content": bot_response})  # Ajouter la réponse du bot

if __name__ == "__main__":
    generate()
