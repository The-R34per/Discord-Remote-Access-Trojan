# Discord Remote Access Trojan (Discord RAT)

---

## Overview
This project is a **Discord‑controlled remote command execution bot**.  

The bot connects to a Discord server, creates a channel named after the host machine’s public IP, and executes PowerShell commands sent through that channel. Output is returned directly to Discord.

NOTE: This program **will work** if you have a network that restricts imbound/internal SSH, due to the use of an external API (Discord Token).

This project is intended **strictly for educational use in controlled environments**.

---

## Ethical & Safety Disclaimer

This code is meant for **educational purposes only.**  
It must **only** be used:

- On systems you own or have explicit permission to test  
- In isolated, controlled environments  
- For learning, demonstration, and research purposes  

Misuse of remote‑execution tools can violate laws.  
The author is **not responsible** for any misuse or damage caused by this project.

---

## Features
- Connects to Discord using a bot token  
- Creates a host‑specific command channel  
- Executes arbitrary PowerShell commands  
- Streams command output back to Discord  
- Graceful shutdown command (`shutdown`)  
- Hidden PowerShell window using `CREATE_NO_WINDOW`

---

## How It Works
1. The bot logs into Discord using a bot token.  
2. On startup, it retrieves the machine’s public IP and creates a dedicated text channel.  
3. It launches a persistent PowerShell subprocess.  
4. Any message sent in the channel is treated as a PowerShell command.  
5. Output is captured and returned to Discord in chunks (max 2000 characters).  
6. Sending `shutdown` terminates the bot.

---

## Requirements
- Python 3.8+  
- `discord.py`  
- `requests`

*Optional:*
If you want to turn the .py file into an executable (.exe) you will also need:
`PyInstaller`

**Install dependencies:**

```bash
pip install discord.py requests
```

```bash
pip install pyinstaller
```

---

## How to Make it Into a Executable
Open a terminal in the same place as the .py file and enter the following command:
```bash
python -m PyInstaller --onefile --noconsole DiscordRAT.py
```

This will create 2 folders, the .exe file will be in the **"dist"** folder.

---

## How to Run

Open a terminal window at the path of the bot.py file, then enter the following command:
```bash
python3 DiscordRAT.py
```

---

## License

Discord Remote Access Trojan © 2026 by The-R34per is licensed under CC BY-NC-SA 4.0. To view a copy of this license, visit https://creativecommons.org/licenses/by-nc-sa/4.0/
