from telebot import types
from src.mi_bot.core.personalities import PERSONALITIES

def main_menu():
    """Returns a main keyboard with personality options."""
    markup = types.InlineKeyboardMarkup()
    
    # Organize personalities in pairs
    personality_list = list(PERSONALITIES.keys())
    for i in range(0, len(personality_list), 2):
        row = []
        for j in range(i, min(i + 2, len(personality_list))):
            key = personality_list[j]
            # Simple mapping for labels
            labels = {
                "amigo": "🤝 Amigo",
                "motivador": "🚀 Motivador",
                "sabio": "📚 Sabio",
                "humorista": "🤡 Humorista",
                "mentor": "💼 Mentor",
                "apoyo": "❤️ Apoyo"
            }
            row.append(types.InlineKeyboardButton(
                text=labels.get(key, key.capitalize()), 
                callback_data=f"set_personality_{key}"
            ))
        markup.add(*row)
        
    return markup

def help_keyboard():
    """Returns a keyboard with helpful commands."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("/start", "/help")
    markup.add("/exportar", "/analisis", "/insights", "/reset")
    return markup
