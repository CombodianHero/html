# Quick Setup Guide 🚀

## Step 1: Get Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 2: Install Requirements

```bash
pip install python-telegram-bot --upgrade
```

## Step 3: Configure the Bot

Open `telegram_bot.py` and replace this line:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
```

With your actual token:
```python
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

## Step 4: Run the Bot

```bash
python telegram_bot.py
```

You should see:
```
🤖 Bot started! Send /start to begin.
```

## Step 5: Test the Bot

1. Open Telegram and find your bot
2. Send `/start`
3. Upload the `BTSC_JE_NEW_SPL_Subjects.txt` file (or any txt file with the correct format)
4. Wait a few seconds
5. Download the generated HTML file!

## File Format

Your txt file should have lines in this format:
```
(Category)Title:URL
```

Example:
```
(Theory)Lect.-1 EVS:https://example.com/video.m3u8
(Environment)Lect.-1 Notes:https://example.com/notes.pdf
```

## Testing Without Telegram

You can test the parser without running the bot:

```bash
python test_parser.py
```

This will generate an HTML file from the example txt file.

## Troubleshooting

**Problem**: `ModuleNotFoundError: No module named 'telegram'`
**Solution**: Run `pip install python-telegram-bot --upgrade`

**Problem**: Bot doesn't respond
**Solution**: 
1. Check your bot token is correct
2. Make sure the bot is running
3. Check for errors in the console

**Problem**: Videos don't play
**Solution**: 
1. Check if the video URL is accessible
2. For Classplus videos, ensure the proxy server is running
3. Try opening the URL in a browser

## Need Help?

- Check the full README.md for detailed information
- Make sure your txt file format is correct
- Verify all URLs are accessible

---

Happy coding! 🎉
