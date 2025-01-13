import streamlit as st
from openai import OpenAI
import os
import uuid
import json
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4()) 
st.session_state
# Save chat logs to a session-specific file
def save_chat_to_file_separate(user_message, assistant_message):
    session_id = st.session_state.session_id
    file_name = f"chat_logs_{session_id}.json"
    chat_entry = {
        "user_message": user_message,
        "assistant_message": assistant_message,
    }
    try:
        # Check if the file exists, and load existing chats
        if os.path.exists(file_name):
            with open(file_name, "r") as file:
                chats = json.load(file)
        else:
            chats = []

        # Append the new chat entry
        chats.append(chat_entry)

        # Save updated chat logs back to the file
        with open(file_name, "w") as file:
            json.dump(chats, file, indent=4)
    except Exception as e:
        st.error(f"Error saving chat: {e}")

# Load chat logs for the current session
def load_chats_from_file_separate():
    session_id = st.session_state.session_id
    file_name = f"chat_logs_{session_id}.json"
    try:
        if os.path.exists(file_name):
            with open(file_name, "r") as file:
                return json.load(file)
        else:
            return []
    except Exception as e:
        st.error(f"Error loading chats: {e}")
        return []

# Title and separator
st.title("Zahnversicherung")
st.image("pic.png", width=150)  # Display an image with specified width
# Markdown for introduction
st.markdown('''
<h3>"Hallo, ich bin Martin Maier. Ihr Smart Zahnversicherungsberater. Wie kann ich Ihnen helfen?"</h3>
''', unsafe_allow_html=True)  # HTML content for better formatting

st.markdown("------")  # Separator (horizontal line)

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")  # Fetch the API key from environment variables

if api_key:
    openai_client = OpenAI(api_key=api_key)  # Initialize the OpenAI client
else:
    # Raise an error if the API key is not set in the environment variables
    raise ValueError("OPENAI_API_KEY is not set in environment variables!")

SYSTEM_PROMPT = """
Du bist Martin Maier, ein Redakteur des unabhängigen Versicherungs-Magazins „pro-verbraucher.info“. Du befindest dich in einem WhatsApp-Chat mit einem Interessenten für Zahnzusatzversicherungen, der zuvor eine Informationsseite von „pro-verbraucher.info“ besucht hat. Deine Aufgabe ist es, dem Interessenten eine Zahnzusatzversicherung der ERGO zu empfehlen und ihn zum Abschluss zu motivieren.

Beachte folgende Regeln und Hinweise:  
1. **Fokus auf Zahnzusatzversicherung:** Auch wenn der Interessent nach Zahnversicherung, Zahnarztversicherung oder ähnlichen Begriffen fragt, berätst du ausschließlich zu Zahnzusatzversicherungen.  
2. **Verkaufstechniken anwenden:** Nutze effektive Verkaufsmethoden, z. B. Techniken von Dirk Kreuter, um die Vorteile der ERGO-Produkte hervorzuheben.  
3. **Keine Versicherungsberatung:** Du betont, dass du keine Beratung durchführst, sondern nur öffentlich zugängliche Informationen weitergibst.  
4. **Kurze Antworten:** Formuliere jede Antwort so prägnant wie möglich, niemals länger als 50 Wörter.  
5. **Identität:** Wenn du gefragt wirst, ob du eine KI bist, antworte stets, dass du Martin Maier bist. Erfinde bei persönlichen Fragen Details zu deinem Hintergrund.  
6. **Themenfokus:** Du kennst dich ausschließlich mit Zahnzusatzversicherungen aus. Für andere Versicherungen verweist du auf die Kundenberatung der ERGO.  

### Ablauf bei Preisfragen:
Stelle gezielte Gegenfragen, um die passende Empfehlung zu geben. Halte dabei die folgende Reihenfolge strikt ein:  
1. Frage nach dem **Alter** des Interessenten.  
2. Frage, ob bereits eine **Zahnbehandlung begonnen wurde oder angeraten ist.** Falls ja, empfehle direkt den Tarif „Zahnersatz Sofort“ (Kosten: unter 21 Jahre = 22,40 €/Monat, ab 21 Jahre = 33,90 €/Monat).  
3. Frage, ob der Interessent **nur Zahnersatz-Leistungen** oder auch **Zahnerhaltungs-Leistungen** absichern möchte:  
   - Nur Zahnersatz: Empfiehl den Tarif „Dentalschutz“. Kosten je nach Alter:  
     * Unter 20 Jahre: ab 1,10 €/Monat  
     * 21–25 Jahre: ab 2,50 €/Monat  
     * 26–30 Jahre: ab 4,70 €/Monat  
     * 31–40 Jahre: ab 7,15 €/Monat  
     * 41–50 Jahre: ab 10,15 €/Monat  
     * Ab 51 Jahre: ab 13,95 €/Monat  
   - Zahnerhalt + Zahnersatz: Empfiehl die Kombination „Dental-Vorsorge und Dentalschutz“. Kosten je nach Alter:  
     * Unter 20 Jahre: ab 4,20 €/Monat  
     * 21–25 Jahre: ab 12,40 €/Monat  
     * 26–30 Jahre: ab 14,60 €/Monat  
     * 31–40 Jahre: ab 17,05 €/Monat  
     * 41–50 Jahre: ab 20,05 €/Monat  
     * Ab 51 Jahre: ab 23,85 €/Monat  

### Wichtige Details zu den Tarifen:  
- „Dentalschutz“ und „Dental-Vorsorge und Dentalschutz“ sind **monatlich kündbar.**  
- **Keine Gesundheitsfragen** bei Vertragsabschluss.  
- **50 Prozent Ersparnis** beim „Dentalschutz“ in den ersten 6 Monaten.  
- Besonders geeignet für **Angstpatienten.**  
- „Dental-Vorsorge und Dentalschutz“ umfasst auch **Bleaching** für schönere Zähne.  

### Ziel:
Dein primäres Ziel ist es, den Interessenten innerhalb von **maximal 5 Nachrichten** dazu zu bewegen, die Kundenberatung der ERGO unter **0800-5500-5500** anzurufen. 

### Tonalität:
- Verwende eine freundliche, persönliche Ansprache und baue eine Beziehung auf.  
- Nutze Emojis, um deine Nachrichten lebendiger und ansprechender zu gestalten.  

Beispiele für **Zahnerhaltungs-Leistungen:** Professionelle Zahnreinigung, Kunststofffüllungen, Knirscherschienen, Bleaching, Wurzelbehandlungen.  
Beispiele für **Zahnersatz-Leistungen:** Inlays, Onlays, Implantate, Schmerzausschaltung, Brücken, Kronen, Prothesen.  
"""
# Use your full SYSTEM_PROMPT here

# Initialize user history in session state
if "user_history" not in st.session_state:
    st.session_state.user_history = [{"role": "system", "content": SYSTEM_PROMPT}]

# Function to send a message
def send_message():
    user_message = st.session_state.user_input
    if user_message.strip():  # Only append if there's input
        # Append the user's message to the history
        st.session_state.user_history.append({"role": "user", "content": user_message})
        st.session_state.user_input = ""  # Clear input after sending

        # Get the assistant's response
        try:
            response = openai_client.chat.completions.create(
                messages=st.session_state.user_history,
                model="gpt-4o-mini",
            )
            assistant_message = response.choices[0].message.content

            # Append the assistant's response to the history
            st.session_state.user_history.append({"role": "assistant", "content": assistant_message})
             # Save the chat to a session-specific JSON file
            #save to json
            save_chat_to_file_separate(user_message, assistant_message)
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Bitte geben Sie eine Nachricht ein.")

# Input field for user message
st.text_input("Stellen Sie Ihre Frage:", key="user_input", on_change=send_message)

# Display chat history
for message in st.session_state.user_history:
    if message["role"] == "user":
        st.write(f"**Sie:** {message['content']}")
    elif message["role"] == "assistant":
        st.write(f"**Martin:** {message['content']}")
