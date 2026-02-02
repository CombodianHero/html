import os
import re
import json
import urllib.parse
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN', '7601635113:AAHjmE2yjru1sIIbAW6g56-sIc30cv4Tsm8')

# ---------------- PARSER ---------------- #
def parse_txt_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    subjects = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        m = re.match(r"\(([^)]+)\)(.+?):(https?://.+)", line)
        if not m:
            continue

        title = m.group(2).strip()
        url = m.group(3).strip()

        subject = re.sub(r"Lect[.-]?\d+", "", title).strip() or "General"

        is_pdf = url.lower().endswith(".pdf")

        if not is_pdf and "classplus" in url.lower():
            url = f"https://engineers-babu.onrender.com/?url={urllib.parse.quote(url)}"

        subjects.setdefault(subject, {"videos": [], "pdfs": []})

        if is_pdf:
            subjects[subject]["pdfs"].append({"name": title, "src": url})
        else:
            subjects[subject]["videos"].append({"title": title, "src": url})

    return [{
        "folder": k,
        "subjects": [{"name": k, **v}]
    } for k, v in subjects.items()]


# ---------------- HTML GENERATOR ---------------- #
def generate_html(data, user_id, user_name, output_path):
    data_json = json.dumps(data, ensure_ascii=False)

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Engineers Babu Player</title>

<style>
body {{
  margin:0;
  background:#0f1117;
  color:white;
  font-family:Arial;
}}

.api-player-container {{
  position:relative;
  width:100%;
  height:420px;
  background:black;
  overflow:hidden;
}}

.api-player-iframe {{
  width:100%;
  height:100%;
  border:none;
}}

.watermark {{
  position:absolute;
  top:20px;
  left:20px;
  z-index:99;
  opacity:0.25;
  font-size:14px;
  color:white;
  pointer-events:none;
  white-space:nowrap;
  text-shadow:0 0 6px black;
}}

.playlist-item {{
  padding:10px;
  background:#1f2633;
  margin:4px;
  cursor:pointer;
}}
.playlist-item:hover {{ background:#2563eb; }}
</style>
</head>

<body>

<h3>🎬 Video Player</h3>

<div id="videoPlayer"></div>
<div id="playlist"></div>

<script>
const data = {data_json};

const USER_WATERMARK = "User: {user_name} | ID: {user_id}";

function playVideo(v){{
  videoPlayer.innerHTML = `
  <div class="api-player-container">
    <iframe class="api-player-iframe"
      src="${{v.src}}"
      allowfullscreen
      allow="autoplay; encrypted-media; fullscreen">
    </iframe>

    <div id="wm" class="watermark">${{USER_WATERMARK}}</div>
  </div>
  `;

  videoPlayer.scrollIntoView({{behavior:"smooth"}});
  startWatermarkMotion();
}}

function renderPlaylist(vs){{
  playlist.innerHTML = vs.map(v =>
    `<div class="playlist-item" onclick='playVideo(${{JSON.stringify(v)}})'>${{v.title}}</div>`
  ).join("");
}}

function startWatermarkMotion(){{
  const wm = document.getElementById("wm");
  if(!wm) return;

  setInterval(() => {{
    wm.style.top = Math.random()*70 + "%";
    wm.style.left = Math.random()*70 + "%";
  }}, 3000);
}}

// Load first video
if(data[0]?.subjects[0]?.videos.length){{
  renderPlaylist(data[0].subjects[0].videos);
  playVideo(data[0].subjects[0].videos[0]);
}}

// Disable right click & inspect
document.addEventListener("contextmenu", e => e.preventDefault());
document.addEventListener("keydown", e => {{
  if(e.key==="F12" || (e.ctrlKey && e.shiftKey && ["I","J","C"].includes(e.key)) || (e.ctrlKey && e.key==="U")) {{
    e.preventDefault();
  }}
}});

// Fullscreen orientation lock
document.addEventListener("fullscreenchange",()=>{
  if(document.fullscreenElement && screen.orientation?.lock)
    screen.orientation.lock("landscape").catch(()=>{{}});
  else screen.orientation?.unlock?.();
});
</script>

</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


# ---------------- BOT HANDLERS ---------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📤 Send .txt file to generate protected player")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc.file_name.endswith(".txt"):
        return await update.message.reply_text("❌ Only .txt allowed")

    file = await context.bot.get_file(doc.file_id)
    input_path = f"/tmp/{doc.file_name}"
    await file.download_to_drive(input_path)

    data = parse_txt_file(input_path)

    user = update.effective_user
    output = f"/tmp/{doc.file_name.replace('.txt','.html')}"

    generate_html(data, user.id, user.full_name, output)

    await update.message.reply_document(
        document=open(output,"rb"),
        filename=os.path.basename(output),
        caption="✅ Protected HTML generated"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.run_polling()


if __name__ == "__main__":
    main()
