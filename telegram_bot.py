import os
import re
import json
import urllib.parse
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7601635113:AAHjmE2yjru1sIIbAW6g56-sIc30cv4Tsm8')

def parse_txt_file(file_path):
    """Parse the txt file and classify subjects with videos and PDFs"""
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
        
        # Extract subject name from title
        subject_match = re.search(r'(?:Lect[.-]?\d+\s+)(.+?)(?:\s*\(|$)', title)
        if subject_match:
            subject_name = subject_match.group(1).strip()
        else:
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
        
        # Process Classplus URLs through API
        if is_video and 'classplus' in url.lower():
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
                'drm': 'classplus' in match.group(3).lower()
            })
        else:
            subjects_dict[subject_name]['pdfs'].append({
                'name': title,
                'src': url,
                'full_url': url  # Keep original URL for opening in new tab
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
    """Generate HTML file from parsed data"""
    # Convert data to JSON string for JavaScript
    data_json = json.dumps(data, ensure_ascii=False, indent=2)
    
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Engineers Babu | HTML Viewer</title>

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
  display:flex;
  flex-direction:column;
}}

.card h3{{
  margin-bottom:12px;
  font-size:18px;
  font-weight:600;
}}

/* ================= SUBJECTS ================= */
.folder-title{{
  padding:12px;
  border-radius:12px;
  background:var(--inner-bg);
  font-weight:600;
  cursor:pointer;
  margin-bottom:8px;
}}

.subject{{
  margin-top:6px;
  padding:10px;
  border-radius:10px;
  background:var(--inner-bg);
  cursor:pointer;
  transition:all 0.2s;
}}

.subject:hover,
.subject.active{{
  background:var(--primary);
  color:#fff;
  transform:translateX(4px);
}}

/* ================= VIDEO PLAYER SECTION ================= */
#videoPlayer{{
  flex:1;
  display:flex;
  flex-direction:column;
  min-height:400px;
}}

#videoPlayerContainer{{
  flex:1;
  background:var(--inner-bg);
  border-radius:14px;
  overflow:hidden;
  display:flex;
  align-items:center;
  justify-content:center;
  border:1px solid var(--border);
  margin-bottom:12px;
}}

/* Fixed API Player Container - NO SCROLLING */
.api-player-container{{
  width:100%;
  height:100%;
  min-height:360px;
  background:#000;
  position:relative;
  display:flex;
  align-items:center;
  justify-content:center;
  overflow:hidden !important;
}}

.api-player-iframe{{
  width:100%;
  height:100%;
  border:none;
  background:#000;
  overflow:hidden !important;
}}

/* PLAYLIST SECTION */
#playlistContainer{{
  flex:1;
  overflow-y:auto;
  max-height:300px;
  padding-right:4px;
}}

.playlist-item{{
  padding:10px;
  border-radius:10px;
  background:var(--inner-bg);
  cursor:pointer;
  margin-bottom:6px;
  transition:all 0.2s;
  display:flex;
  align-items:center;
  gap:8px;
}}

.playlist-item:before{{
  content:"▶";
  font-size:12px;
  opacity:0.7;
}}

.playlist-item:hover,
.playlist-item.active{{
  background:var(--primary);
  color:#fff;
  transform:translateX(4px);
}}

.playlist-item.active:before{{
  content:"⏸";
}}

/* ================= PDF SECTION ================= */
#pdfContainer{{
  flex:1;
  display:flex;
  flex-direction:column;
  min-height:400px;
}}

#pdfList{{
  flex:1;
  overflow-y:auto;
  max-height:350px;
  padding-right:4px;
}}

.pdf-item{{
  padding:10px;
  border-radius:10px;
  background:var(--inner-bg);
  cursor:pointer;
  margin-bottom:6px;
  transition:all 0.2s;
  display:flex;
  align-items:center;
  gap:8px;
}}

.pdf-item:before{{
  content:"📄";
  font-size:14px;
}}

.pdf-item:hover,
.pdf-item.active{{
  background:var(--primary);
  color:#fff;
  transform:translateX(4px);
}}

/* PDF VIEWER REMOVED - Now opens in new tab */

/* ================= RESPONSIVE ================= */
@media(max-width:900px){{
  .container{{
    grid-template-columns:1fr;
  }}
  #videoPlayerContainer{{
    min-height:300px;
  }}
  .api-player-container{{
    min-height:300px;
  }}
}}

@media(max-width:600px){{
  #videoPlayerContainer{{
    min-height:250px;
  }}
  .api-player-container{{
    min-height:250px;
  }}
}}

/* Scrollbar Styling */
::-webkit-scrollbar{{
  width:6px;
}}

::-webkit-scrollbar-track{{
  background:transparent;
  border-radius:3px;
}}

::-webkit-scrollbar-thumb{{
  background:var(--primary);
  border-radius:3px;
}}

::-webkit-scrollbar-thumb:hover{{
  background:var(--primary);
  opacity:0.8;
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

  <!-- LEFT - SUBJECTS -->
  <div class="card" id="subjectsCard">
    <h3>📚 Subjects</h3>
    <div id="subjects"></div>
  </div>

  <!-- CENTER - VIDEO PLAYER -->
  <div class="card" id="videoCard">
    <h3>🎬 Video Player</h3>
    <div id="videoPlayer">
      <div id="videoPlayerContainer">
        <div class="api-player-container">
          <iframe class="api-player-iframe" 
                  id="apiPlayer" 
                  allowfullscreen
                  allow="autoplay; encrypted-media; picture-in-picture">
          </iframe>
        </div>
      </div>
      <div id="playlistContainer">
        <div id="playlist"></div>
      </div>
    </div>
  </div>

  <!-- RIGHT - PDF LIST -->
  <div class="card" id="pdfCard">
    <h3>📄 PDF Files</h3>
    <div id="pdfContainer">
      <div id="pdfList"></div>
      <div style="margin-top:15px; padding:12px; background:var(--inner-bg); border-radius:10px; font-size:14px; color:var(--muted);">
        <p>📌 <strong>Note:</strong> Click on any PDF to open it in a new tab</p>
      </div>
    </div>
  </div>

</div>

<script>
/* ================= THEME TOGGLE ================= */
function toggleTheme(){{
  document.body.classList.toggle("light");
  const toggleBtn = document.querySelector('.toggle');
  toggleBtn.textContent = document.body.classList.contains('light') ? '🌙' : '☀️';
}}

/* ================= DATA ================= */
const data = {data_json};

/* ================= VARIABLES ================= */
let currentVideo = null;

/* ================= SUBJECTS RENDERING ================= */
function renderSubjects(){{
  let html="";
  data.forEach(f=>{{
    html+=`
      <div class="folder-title"
        onclick="toggleFolder(this)">
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

function toggleFolder(element){{
  const content = element.nextElementSibling;
  content.style.display = content.style.display === 'block' ? 'none' : 'block';
}}

/* ================= LOAD SUBJECT ================= */
function loadSubject(sub,el){{
  // Highlight selected subject
  document.querySelectorAll(".subject").forEach(x=>x.classList.remove("active"));
  el.classList.add("active");
  
  // Load videos if available
  if(sub.videos && sub.videos.length > 0){{
    playVideo(sub.videos[0]);
    renderPlaylist(sub.videos);
  }} else {{
    document.getElementById('apiPlayer').src = '';
    document.getElementById('playlist').innerHTML = '<div style="padding:20px;text-align:center;color:var(--muted)">No videos available</div>';
  }}
  
  // Load PDFs if available
  if(sub.pdfs && sub.pdfs.length > 0){{
    renderPdfs(sub.pdfs);
  }} else {{
    document.getElementById('pdfList').innerHTML = '<div style="padding:20px;text-align:center;color:var(--muted)">No PDFs available</div>';
  }}
}}

/* ================= VIDEO PLAYER FUNCTIONS ================= */
function playVideo(video){{
  currentVideo = video;
  
  // Set iframe source
  const apiPlayer = document.getElementById('apiPlayer');
  apiPlayer.src = video.src;
  
  // Highlight the clicked video in playlist
  highlightPlaylistItem(video);
  
  // Scroll video section into view
  document.getElementById('videoCard').scrollIntoView({{
    behavior: 'smooth',
    block: 'start'
  }});
}}

function renderPlaylist(videos){{
  let html = '';
  videos.forEach((v, index) => {{
    html += `
      <div class="playlist-item" 
           onclick="playVideo(${{JSON.stringify(v)}})"
           data-index="${{index}}">
        <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
          ${{v.title}}
        </span>
      </div>
    `;
  }});
  
  document.getElementById('playlist').innerHTML = html;
  
  // Highlight first video
  if(videos.length > 0){{
    highlightPlaylistItem(videos[0]);
  }}
}}

function highlightPlaylistItem(video){{
  document.querySelectorAll(".playlist-item").forEach(item => {{
    item.classList.remove("active");
    const itemVideo = JSON.parse(item.getAttribute('onclick').match(/playVideo\((.*)\)/)[1]);
    if(itemVideo.title === video.title){{
      item.classList.add("active");
    }}
  }});
}}

/* ================= PDF FUNCTIONS ================= */
function renderPdfs(pdfs){{
  let html = '';
  pdfs.forEach((pdf, index) => {{
    html += `
      <div class="pdf-item" 
           onclick="openPdf('${{pdf.full_url || pdf.src}}')"
           data-index="${{index}}">
        <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
          ${{pdf.name}}
        </span>
      </div>
    `;
  }});
  
  document.getElementById('pdfList').innerHTML = html;
}}

function openPdf(url){{
  // Open PDF in new tab
  window.open(url, '_blank');
}}

/* ================= SEARCH FUNCTION ================= */
function filterSubjects(val){{
  document.querySelectorAll(".subject").forEach(s=>{{
    s.style.display = s.innerText.toLowerCase().includes(val.toLowerCase())
      ? "block" : "none";
  }});
}}

/* ================= KEYBOARD SHORTCUTS ================= */
document.addEventListener('keydown', function(e){{
  // Space to play/pause
  if(e.code === 'Space' && document.activeElement.tagName !== 'INPUT'){{
    e.preventDefault();
    const apiPlayer = document.getElementById('apiPlayer');
    if(apiPlayer.src){{
      apiPlayer.focus();
    }}
  }}
  
  // F for fullscreen
  if(e.code === 'KeyF' && document.activeElement.tagName !== 'INPUT'){{
    e.preventDefault();
    const apiPlayer = document.getElementById('apiPlayer');
    if(apiPlayer.src){{
      if(apiPlayer.requestFullscreen){{
        apiPlayer.requestFullscreen();
      }}
    }}
  }}
}});

/* ================= INITIALIZATION ================= */
renderSubjects();

// Auto-load first subject if available
if(data.length > 0 && data[0].subjects.length > 0){{
  setTimeout(() => {{
    const firstSubject = data[0].subjects[0];
    const firstSubjectElement = document.querySelector('.subject');
    if(firstSubjectElement){{
      loadSubject(firstSubject, firstSubjectElement);
    }}
  }}, 500);
}}
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
        "Example:\n"
        "(Physics)Lect.-1 Introduction:https://example.com/video1.mp4\n"
        "(Physics)Notes-1 Formulas:https://example.com/notes.pdf\n\n"
        "I'll generate an HTML viewer with API video player! 🚀"
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
        
        # Count totals
        total_videos = sum(len(subject['subjects'][0]['videos']) for subject in parsed_data)
        total_pdfs = sum(len(subject['subjects'][0]['pdfs']) for subject in parsed_data)
        
        # Send the generated HTML file
        with open(output_path, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=output_filename,
                caption=(
                    f"✅ **HTML Viewer Generated!**\n\n"
                    f"📊 **Statistics:**\n"
                    f"• 📁 Subjects: {len(parsed_data)}\n"
                    f"• 🎬 Videos: {total_videos}\n"
                    f"• 📄 PDFs: {total_pdfs}\n\n"
                    f"**Features:**\n"
                    f"• 🎯 API Video Player\n"
                    f"• 📄 PDFs open in new tab\n"
                    f"• 🔍 Search functionality\n"
                    f"• 🌙/☀️ Dark/Light theme\n"
                    f"• 📱 Mobile responsive"
                )
            )
        
        # Clean up
        os.remove(input_path)
        os.remove(output_path)
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        await update.message.reply_text(f"❌ Error processing file: {str(e)}")

def main():
    """Start the bot"""
    if BOT_TOKEN == "7601635113:AAHjmE2yjru1sIIbAW6g56-sIc30cv4Tsm8":
        logger.error("Please set BOT_TOKEN environment variable")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Start the bot
    logger.info("🤖 Bot started! Send /start to begin.")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == '__main__':
    main()
