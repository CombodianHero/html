import os
import re
import json
import urllib.parse
from telegram import Update, Document
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Replace with your bot token
BOT_TOKEN = "7601635113:AAHjmE2yjru1sIIbAW6g56-sIc30cv4Tsm8"

def parse_txt_file(file_path):
    """
    Parse the txt file and classify subjects with videos and PDFs
    Returns a structured JSON-like dictionary
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    subjects_dict = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Parse line: (Category)Title:URL
        match = re.match(r'\(([^)]+)\)(.+?):(https?://.+)', line)
        if not match:
            continue
        
        category = match.group(1).strip()
        title = match.group(2).strip()
        url = match.group(3).strip()
        
        # Extract subject name from title (e.g., "Lect.-1 EVS" -> "EVS")
        subject_match = re.search(r'(?:Lect[.-]?\d+\s+)(.+?)(?:\s*\(|$)', title)
        if subject_match:
            subject_name = subject_match.group(1).strip()
        else:
            # Fallback: use everything after lecture number
            subject_match = re.search(r'Lect[.-]?\d+\s+(.+)', title)
            if subject_match:
                subject_name = subject_match.group(1).strip()
            else:
                subject_name = "General"
        
        # Clean up subject name
        subject_name = re.sub(r'\s+', ' ', subject_name)
        
        # Determine if it's video or PDF
        is_pdf = url.endswith('.pdf')
        is_video = not is_pdf
        
        # Process Classplus URLs
        if 'classplus' in url.lower():
            url = f"https://engineers-babu.onrender.com/?url={urllib.parse.quote(url)}"
        
        # Initialize subject if not exists
        if subject_name not in subjects_dict:
            subjects_dict[subject_name] = {
                'videos': [],
                'pdfs': []
            }
        
        # Add to appropriate list
        if is_video:
            subjects_dict[subject_name]['videos'].append({
                'title': title,
                'src': url,
                'drm': 'classplus' in match.group(3).lower()  # Original URL check
            })
        else:
            subjects_dict[subject_name]['pdfs'].append({
                'name': title,
                'src': url
            })
    
    # Convert to the required format
    result = []
    for subject_name, content in subjects_dict.items():
        if content['videos'] or content['pdfs']:
            result.append({
                'folder': subject_name,
                'subjects': [{
                    'name': subject_name,
                    'videos': content['videos'],
                    'pdfs': content['pdfs']
                }]
            })
    
    return result

def generate_html(data, output_path):
    """
    Generate HTML file from parsed data using the provided template
    """
    # Convert data to JSON string for JavaScript
    data_json = json.dumps(data, ensure_ascii=False, indent=2)
    
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Engineers Babu | HTML Viewer</title>

<!-- Shaka Player (DRM / DASH) -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/shaka-player/4.7.11/shaka-player.compiled.js"></script>

<style>
/* ================= THEME VARIABLES ================= */
:root{{
  /* 🌙 DARK THEME */
  --page-bg:#0f1117;
  --card-bg:#161b22;
  --inner-bg:#1f2633;
  --text:#e5e7eb;
  --muted:#9ca3af;
  --border:rgba(255,255,255,0.08);
  --shadow:none;
  --primary:#2563eb;
}}

.light{{
  /* ☀️ LIGHT THEME */
  --page-bg:#f4f6fb;
  --card-bg:#ffffff;
  --inner-bg:#f1f4fb;
  --text:#1f2937;
  --muted:#6b7280;
  --border:rgba(0,0,0,0.06);
  --shadow:0 8px 24px rgba(0,0,0,0.05);
  --primary:#2563eb;
}}

/* ================= BASE ================= */
*{{
  margin:0;
  padding:0;
  box-sizing:border-box;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto;
}}

body{{
  background:var(--page-bg);
  color:var(--text);
  transition:background .3s,color .3s;
}}

/* ================= HEADER ================= */
.main-header{{
  position:relative;
  display:flex;
  justify-content:flex-end;
  align-items:center;
  padding:18px 20px;
  background:var(--card-bg);
  border-bottom:1px solid var(--border);
}}

.title-box{{
  position:absolute;
  left:50%;
  transform:translateX(-50%);
  text-align:center;
}}

.title-box h1{{
  font-size:42px;
  font-weight:800;
  background:linear-gradient(90deg,#00f5ff,#E50914,#ffcc00);
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  letter-spacing:2px;
}}

.title-box span{{
  font-size:13px;
  color:var(--muted);
  letter-spacing:3px;
}}

.toggle{{
  cursor:pointer;
  padding:8px 14px;
  border-radius:20px;
  background:var(--inner-bg);
  border:1px solid var(--border);
}}

/* ===== GRADIENT LINE ===== */
.gradient-bar{{
  height:6px;
  background:linear-gradient(
    90deg,
    #00f5ff,
    #7a00ff,
    #E50914,
    #ffcc00
  );
}}

/* ================= SEARCH ================= */
.search{{
  padding:14px;
}}

.search input{{
  width:100%;
  padding:12px;
  border-radius:12px;
  border:none;
  outline:none;
  background:var(--card-bg);
  color:var(--text);
  box-shadow:var(--shadow);
}}

/* ================= LAYOUT ================= */
.container{{
  display:grid;
  grid-template-columns:280px 1fr 360px;
  gap:18px;
  padding:18px;
}}

/* ================= CARD ================= */
.card{{
  background:var(--card-bg);
  border-radius:18px;
  padding:14px;
  border:1px solid var(--border);
  box-shadow:var(--shadow);
}}

/* ================= SUBJECTS ================= */
.folder-title{{
  padding:12px;
  border-radius:12px;
  background:var(--inner-bg);
  font-weight:600;
  cursor:pointer;
}}

.subject{{
  margin-top:6px;
  padding:10px;
  border-radius:10px;
  background:var(--inner-bg);
  cursor:pointer;
}}

.subject:hover,
.subject.active{{
  background:var(--primary);
  color:#fff;
}}

/* ================= VIDEO ================= */
#videoPlayer{{
  margin-top:10px;
  padding:8px;
  background:var(--inner-bg);
  border-radius:14px;
}}

video{{
  width:100%;
  border-radius:12px;
  background:black;
}}

.playlist-item{{
  margin-top:6px;
  padding:10px;
  border-radius:10px;
  background:var(--inner-bg);
  cursor:pointer;
}}

.playlist-item:hover,
.playlist-item.active{{
  background:var(--primary);
  color:#fff;
}}

/* ================= PDF ================= */
.pdf-item{{
  margin-bottom:6px;
  padding:10px;
  border-radius:10px;
  background:var(--inner-bg);
  cursor:pointer;
}}

.pdf-item:hover,
.pdf-item.active{{
  background:var(--primary);
  color:#fff;
}}

iframe{{
  width:100%;
  height:100%;
  background:var(--inner-bg);
  border-radius:14px;
  border:none;
}}

/* ================= RESPONSIVE ================= */
@media(max-width:900px){{
  .container{{
    grid-template-columns:1fr;
  }}
  iframe{{
    height:400px;
  }}
}}
</style>
</head>

<body class="light">

<header class="main-header">
  <div class="title-box">
    <h1>Engineers Babu</h1>
    <span>HTML VIEWER</span>
  </div>
  <div class="toggle" onclick="toggleTheme()">🌙 / ☀️</div>
</header>

<div class="gradient-bar"></div>

<div class="search">
  <input type="text" placeholder="Search subject..." onkeyup="filterSubjects(this.value)">
</div>

<div class="container">

  <!-- LEFT -->
  <div class="card" id="subjects"></div>

  <!-- CENTER -->
  <div class="card">
    <h3>🎬 Video Player</h3>
    <div id="videoPlayer"></div>
    <div id="playlist"></div>
  </div>

  <!-- RIGHT -->
  <div class="card">
    <h3>📄 PDF Viewer</h3>
    <div id="pdfList"></div>
    <iframe id="pdfViewer"></iframe>
  </div>

</div>

<script>
/* ================= THEME TOGGLE ================= */
function toggleTheme(){{
  document.body.classList.toggle("light");
}}

/* ================= DATA ================= */
const data = {data_json};

/* ================= LOGIC ================= */
function renderSubjects(){{
  let html="";
  data.forEach(f=>{{
    html+=`
      <div class="folder-title"
        onclick="this.nextElementSibling.style.display =
        this.nextElementSibling.style.display==='block'?'none':'block'">
        📁 ${{f.folder}}
      </div>
      <div style="display:none;padding-left:6px;">
    `;
    f.subjects.forEach(s=>{{
      html+=`<div class="subject" onclick='loadSubject(${{JSON.stringify(s)}},this)'>${{s.name}}</div>`;
    }});
    html+=`</div>`;
  }});
  subjects.innerHTML=html;
}}

function loadSubject(sub,el){{
  document.querySelectorAll(".subject").forEach(x=>x.classList.remove("active"));
  el.classList.add("active");
  
  if(sub.videos && sub.videos.length > 0){{
    playVideo(sub.videos[0]);
    renderPlaylist(sub.videos);
  }} else {{
    videoPlayer.innerHTML="<p style='padding:20px;text-align:center;color:var(--muted)'>No videos available</p>";
    playlist.innerHTML="";
  }}
  
  if(sub.pdfs && sub.pdfs.length > 0){{
    renderPdf(sub.pdfs);
  }} else {{
    pdfList.innerHTML="<p style='padding:10px;text-align:center;color:var(--muted)'>No PDFs available</p>";
    pdfViewer.src="";
  }}
}}

function playVideo(v){{
  videoPlayer.innerHTML="";
  
  // Highlight active video in playlist
  document.querySelectorAll(".playlist-item").forEach(x=>x.classList.remove("active"));
  
  if(v.drm){{
    const video=document.createElement("video");
    video.controls=true;
    video.autoplay=true;
    videoPlayer.appendChild(video);
    
    if(typeof shaka !== 'undefined'){{
      const player=new shaka.Player(video);
      player.load(v.src).catch(err=>{{
        console.error("Error loading video:", err);
        videoPlayer.innerHTML=`<p style='padding:20px;text-align:center;color:#ef4444'>Error loading video: ${{err.message}}</p>`;
      }});
    }} else {{
      videoPlayer.innerHTML="<p style='padding:20px;text-align:center;color:#ef4444'>Shaka Player not loaded</p>";
    }}
  }}else{{
    videoPlayer.innerHTML=`<video controls autoplay src="${{v.src}}"></video>`;
  }}
}}

function renderPlaylist(vs){{
  playlist.innerHTML=vs.map((v, idx)=>
    `<div class="playlist-item" onclick='playVideo(${{JSON.stringify(v)}});highlightPlaylistItem(this)' data-idx="${{idx}}">${{v.title}}</div>`
  ).join("");
}}

function highlightPlaylistItem(el){{
  document.querySelectorAll(".playlist-item").forEach(x=>x.classList.remove("active"));
  el.classList.add("active");
}}

function renderPdf(p){{
  pdfList.innerHTML=p.map((x, idx)=>
    `<div class="pdf-item" onclick="pdfViewer.src='${{x.src}}';highlightPdfItem(this)" data-idx="${{idx}}">${{x.name}}</div>`
  ).join("");
  if(p.length > 0){{
    pdfViewer.src=p[0].src;
  }}
}}

function highlightPdfItem(el){{
  document.querySelectorAll(".pdf-item").forEach(x=>x.classList.remove("active"));
  el.classList.add("active");
}}

function filterSubjects(val){{
  document.querySelectorAll(".subject").forEach(s=>{{
    s.style.display = s.innerText.toLowerCase().includes(val.toLowerCase())
      ? "block" : "none";
  }});
}}

renderSubjects();
</script>

</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    return output_path

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    await update.message.reply_text(
        "👋 Welcome to Engineers Babu HTML Generator Bot!\n\n"
        "📤 Send me a .txt file with the format:\n"
        "(Category)Title:URL\n\n"
        "I'll generate an HTML viewer for you! 🚀"
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle uploaded document"""
    document = update.message.document
    
    # Check if it's a txt file
    if not document.file_name.endswith('.txt'):
        await update.message.reply_text("❌ Please send a .txt file!")
        return
    
    await update.message.reply_text("⏳ Processing your file...")
    
    try:
        # Download file
        file = await context.bot.get_file(document.file_id)
        input_path = f"/tmp/{document.file_name}"
        await file.download_to_drive(input_path)
        
        # Parse the file
        parsed_data = parse_txt_file(input_path)
        
        # Generate HTML
        output_filename = document.file_name.replace('.txt', '.html')
        output_path = f"/tmp/{output_filename}"
        generate_html(parsed_data, output_path)
        
        # Send the generated HTML file
        with open(output_path, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=output_filename,
                caption=f"✅ HTML file generated successfully!\n\n"
                        f"📊 Found {len(parsed_data)} subjects\n"
                        f"🎬 Ready to view your videos and PDFs!"
            )
        
        # Clean up
        os.remove(input_path)
        os.remove(output_path)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error processing file: {str(e)}")

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Start the bot
    print("🤖 Bot started! Send /start to begin.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
