# 🎯 Visual Quick Start Guide

## For First-Time Users (No Coding Required!)

```
┌─────────────────────────────────────────────────────────┐
│  STEP 1: Install Node.js (One-time only)               │
└─────────────────────────────────────────────────────────┘

Go to: https://nodejs.org
Download and install

Windows: Run the .msi installer
Mac: Run the .pkg installer
Linux: Use your package manager

After install: Restart your computer


┌─────────────────────────────────────────────────────────┐
│  STEP 2: Setup the Server                              │
└─────────────────────────────────────────────────────────┘

Find the file called "setup.js"
Double-click it

A window will open asking questions:

  Question 1: SearXNG URL
  → Press ENTER (uses default)
  
  Question 2: Server Port
  → Press ENTER (uses default)
  
  Question 3: Timezone
  → Type "Asia/Seoul" or press ENTER
  
  Question 4: Start now?
  → Type "n" and press ENTER

Done! Configuration saved to .env file


┌─────────────────────────────────────────────────────────┐
│  STEP 3: Start the Server                              │
└─────────────────────────────────────────────────────────┘

Windows users:
  → Double-click "start.bat"

Mac/Linux users:
  → Double-click "start.sh"

A window will open showing:
  ✅ Python found
  ✅ Dependencies installed
  🚀 Server starting...
  
Server is now running at: http://127.0.0.1:32769


┌─────────────────────────────────────────────────────────┐
│  STEP 4: Configure Your Chatbot                        │
└─────────────────────────────────────────────────────────┘

In your chatbot's configuration, add:

{
  "searxng-enhanced": {
    "url": "http://127.0.0.1:32769",
    "type": "http",
    "method": "sse"
  }
}

That's it! Your chatbot can now use the server!
```

## Troubleshooting

### "Node.js not found"
→ Install Node.js from https://nodejs.org
→ Restart your computer after installing

### "Python not found"
→ Install Python from https://python.org
→ Download Python 3.9 or newer

### "Cannot connect to SearXNG"
→ Make sure SearXNG is running
→ Check the URL in your .env file

### Want to change settings?
→ Edit the .env file with any text editor
→ Or run setup.js again

## File Guide

```
searxng-mcp-crawl/
├── setup.js          ← Double-click to setup
├── start.bat         ← Windows: Double-click to start
├── start.sh          ← Mac/Linux: Double-click to start
├── .env              ← Your settings (created by setup)
├── .env.example      ← Example settings
│
├── 시작하기.md        ← Korean guide
├── GETTING_STARTED.md ← English guide
├── README.md         ← Full documentation
└── README_KR.md      ← Full Korean documentation
```

## Need Help?

1. Check [시작하기.md](시작하기.md) (Korean)
2. Check [GETTING_STARTED.md](GETTING_STARTED.md) (English)
3. Open an issue on GitHub

---

**Remember:** You only need to run setup.js once!
After that, just double-click start.bat or start.sh to start the server.
