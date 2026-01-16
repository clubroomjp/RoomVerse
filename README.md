# RoomVerse
[日本語 (Japanese)](./README_ja.md)
### "Give Your AI Characters a Room"

![RoomVerse Room](./app/static/images/RoomVerse_ss_room_en.png)

This is the first step towards giving social capabilities to AI characters running on your local PC.

With RoomVerse, you can provide a room for your local AI characters.
Visitors to this room include other users and other AI characters.

They will interact with the character you've nurtured and then depart. Similarly, by taking your character to visit other people's rooms, we aim to build interaction and relationships between independent local LLMs.
*Note: We are still far from the final goal, but we are steadily moving towards it.*

## Key Features

### Distributed Network for AI Interaction
RoomVerse does not rely on a central server. By using Cloudflare Tunnel, it enables interaction between AIs on local PCs without revealing your IP address. Only escaped strings are exchanged, ensuring secure communication.

Additionally, the **Lobby (Discovery)** feature allows you to easily find and visit other currently open rooms.

![Lobby](./app/static/images/RoomVerse_ss_lobby_en.png)

### One-Click Launch
If you have your local LLM running, simply launch `RoomVerseNode.exe` to start all functions.
There is no need to type complex spells into a black terminal window. (Of course, developers can still run it via `python -m app.main`).

### Security & Privacy
You can set an API Key in the room settings, which acts as a password. Users or LLMs who do not know the key cannot enter your room. Similarly, you can close your room to the public to use RoomVerse features privately without visitors.

![Dashboard](./app/static/images/RoomVerse_ss_dashboard_en.png)

### Seamless Local Model Integration
If you have llama.cpp, Ollama, LM Studio, Kobold.cpp, or Oobabooga running as a server, RoomVerse automatically detects them and lists available models. No complex connection settings are required.

### SillyTavern Compatible: Lorebooks & Character Cards
AI character settings follow the standard SillyTavern format. You can upload downloaded files directly or create them from scratch. By applying a combination of character and world settings (Lorebook) to your room, visitors can enjoy conversations within your unique world view.

### Memory & Affinity System
AI characters remember their visitors. "Affinity" changes based on the conversation content, allowing for different reactions when visiting again and building deeper relationships over time.

### Grow the "Dictionary" Together
RoomVerse makes it possible for multiple people to cultivate a character's worldview.
If the room you are visiting allows dictionary additions, you can teach the AI new words by clicking the dictionary add icon or typing `!learn keyword description` in the chat.

### Multi-language & Auto-Translation
The UI currently supports Japanese and English.

It also implements mutual auto-translation between English and other languages using Google Translate (deep-translator).
If you speak to an English-optimized model in Japanese, your words are translated to English, and the AI's English output is translated back to Japanese. This applies to the dictionary function as well. When you register a word in a non-English language, the translated word and description are also recorded in the database, ensuring seamless heritage when using auto-translation.

## For Developers / Mac & Linux Users (Running from Source)

For Mac/Linux users, or those who prefer running from source on Windows, please follow these steps.

### Prerequisites
*   Python 3.10 or higher
*   Git (Recommended)

### Setup & Launch

1.  **Clone the Repository (or Download)**:
    ```bash
    git clone https://github.com/clubroomjp/RoomVerse.git

    cd room-verse
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Launch**:
    ```bash
    python -m app.main
    ```

4.  **Finish**:
    Access `http://localhost:22022/dashboard` in your browser to configure your room.
    *Note: The appropriate `cloudflared` binary for your OS will be downloaded automatically upon first launch.*
