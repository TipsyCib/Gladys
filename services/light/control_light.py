from tapo import ApiClient
from tapo.requests import Color
import os
import asyncio
from config import TAPO_USERNAME, TAPO_PASSWORD, TAPO_IP_ADDRESS
    
# Contrôle de la lampe
async def control_lampe(action, value=None):
    tapo_username = TAPO_USERNAME
    tapo_password = TAPO_PASSWORD
    ip_address = TAPO_IP_ADDRESS

    client = ApiClient(tapo_username, tapo_password)
    device = await client.l530(ip_address)

    try:

        if action == "on":
            await device.on()
            return "💡 Lampe allumée !"

        elif action == "off":
            await device.off()
            return "💡 Lampe éteinte !"

        elif action == "brightness_porcentage":
            await device.set_brightness(value)
            return f"🔆 Luminosité réglée à {value}%"
        elif action == "brightness_min":
            value = 30
            await device.set_brightness(value)
            return f"🔆 Luminosité réglée à {value}%"
        elif action == "brightness_moyenne":
            value = 50
            await device.set_brightness(value)
            return f"🔆 Luminosité réglée à {value}%"
        elif action == "brightness_max":
            value = 100
            await device.set_brightness(value)
            return f"🔆 Luminosité réglée à {value}%"

        elif action == "color_indigo":
            await device.set_color(Color.Indigo)  
            return f"🌈 Couleur changée ({value})"
        elif action == "color_blue":
            await device.set_color(Color.Azure)  
            return f"🌈 Couleur changée ({value})"
        elif action == "color_rouge":
            await device.set_color(Color.DarkRed)  
            return f"🌈 Couleur changée ({value})"
        elif action == "color_violet":
            await device.set_color(Color.BlueViolet)  
            return f"🌈 Couleur changée ({value})"
        elif action == "color_vert":
            await device.set_color(Color.ForestGreen)  
            return f"🌈 Couleur changée ({value})"
        elif action == "color_rose":
            await device.set_color(Color.Pink)  
            return f"🌈 Couleur changée ({value})"
        elif action == "color_white":
            await device.set_color(Color.CoolWhite)  
            return f"🌈 Couleur changée ({value})"
        elif action == "color_warm":
            await device.set_color(Color.WarmWhite)  
            return f"🌈 Couleur changée ({value})"
        
        else:
            return "Commande invalide."
        
    except Exception as e:
        return f"⚠️ Erreur avec Tapo : {e}"