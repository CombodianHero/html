# Engineers Babu HTML Generator Bot 🤖

A Telegram bot that automatically converts text files with video and PDF links into beautiful, interactive HTML viewers.

## 📋 Features

- ✅ **Automatic Classification**: Intelligently groups videos and PDFs by subject
- 🎬 **Video Player**: Supports regular videos and DRM-protected content via Shaka Player
- 📄 **PDF Viewer**: Integrated PDF viewer with clickable navigation
- 🎨 **Modern UI**: Beautiful dark/light theme with responsive design
- 🔍 **Search Functionality**: Quickly find subjects
- 🔄 **Classplus URL Conversion**: Automatically converts Classplus URLs to engineers-babu.onrender.com proxy

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Setup

1. **Clone or download the files**
   ```bash
   git clone <your-repo>
   cd <your-repo>
   ```

2. **Install dependencies**
   ```bash
   pip install python-telegram-bot --upgrade
   ```

3. **Configure the bot**
   - Open `telegram_bot.py`
   - Replace `YOUR_BOT_TOKEN_HERE` with your actual bot token from BotFather

4. **Run the bot**
   ```bash
   python telegram_bot.py
   ```

## 📖 Usage

### For Bot Users

1. **Start the bot**: Send `/start` to your bot
2. **Upload a txt file**: Send a `.txt` file with the following format:
   ```
   (Category)Title:URL
   ```
3. **Receive HTML**: The bot will analyze the file and send back a generated HTML viewer

### Example Input Format

```txt
(Theory)Lect.-1 EVS (Population Forecasting):https://example.com/video1.m3u8
(Environment)Lect.-1 EVS Notes:https://example.com/notes1.pdf
(Theory)Lect.-2 EVS Water Demand:https://media-cdn.classplusapp.com/.../master.m3u8
(Environment)Lect.-2 EVS Water Demand:https://cdn-wl-assets.classplus.co/.../notes.pdf
```

### How It Works

1. **Parsing**: The bot reads the txt file and extracts:
   - Category (e.g., "Theory", "Environment")
   - Title (e.g., "Lect.-1 EVS")
   - URL (video or PDF link)

2. **Classification**: 
   - Groups content by subject name (extracted from titles)
   - Separates videos from PDFs
   - Detects Classplus URLs and converts them

3. **HTML Generation**:
   - Creates a beautiful, responsive HTML file
   - Embeds all data in JavaScript
   - Adds video player with Shaka Player support
   - Adds PDF viewer with iframe

## 🎯 Key Features Explained

### Subject Classification

The bot intelligently extracts subject names from lecture titles:
- Input: `(Theory)Lect.-1 EVS (Population Forecasting)`
- Extracted Subject: `EVS`

### Classplus URL Handling

URLs containing "classplus" are automatically converted:
```
Original: https://media-cdn.classplusapp.com/.../master.m3u8
Converted: https://engineers-babu.onrender.com/?url=<encoded_url>
```

### DRM Support

The bot detects Classplus URLs and marks them for DRM playback using Shaka Player.

## 🛠️ Project Structure

```
├── telegram_bot.py          # Main bot code
├── test_parser.py          # Standalone test script
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

## 📦 Dependencies

```txt
python-telegram-bot>=20.0
```

## 🎨 HTML Template Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Theme Toggle**: Switch between light and dark themes
- **Search Bar**: Filter subjects by name
- **Collapsible Folders**: Organize subjects by category
- **Video Playlist**: Click any video to play
- **PDF Navigation**: Click any PDF to view

## 🔧 Customization

### Change the HTML Title
Edit `generate_html()` function in `telegram_bot.py`:
```python
<title>Your Custom Title</title>
```

### Modify Theme Colors
Edit the CSS variables in the `generate_html()` function:
```css
:root {
  --page-bg:#0f1117;
  --card-bg:#161b22;
  --primary:#2563eb;
  /* ... */
}
```

### Add More File Types
Extend the parsing logic in `parse_txt_file()`:
```python
# Add support for .mp3, .doc, etc.
if url.endswith('.mp3'):
    # Handle audio files
```

## 🐛 Troubleshooting

### Bot not responding
- Check if the bot token is correct
- Ensure the bot is running (`python telegram_bot.py`)
- Check for error messages in the console

### Videos not playing
- Ensure Shaka Player CDN is accessible
- Check if the video URL is valid
- For DRM content, verify the Classplus proxy is working

### PDFs not loading
- Verify PDF URLs are accessible
- Some PDFs may have CORS restrictions
- Try opening the URL directly in a browser

## 📝 Example Test

Run the standalone test:
```bash
python test_parser.py
```

This will:
1. Parse the uploaded txt file
2. Generate an HTML file in `/mnt/user-data/outputs/`
3. Show statistics about subjects found

## 🤝 Contributing

Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📄 License

MIT License - Feel free to use and modify!

## 👨‍💻 Author

Engineers Babu Team

---

**Enjoy using the Engineers Babu HTML Generator Bot! 🎉**
