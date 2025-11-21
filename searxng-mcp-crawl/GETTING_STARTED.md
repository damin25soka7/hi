# Simple Guide for First-Time Users

## 🎯 Get Started in 3 Steps

### Step 1: Install Node.js (One-time only)

If you don't have Node.js:
- Windows/Mac: Download from https://nodejs.org
- After installation, restart your computer

### Step 2: Run Setup Wizard

Choose **ONE** method:

**Method A - Automatic Setup (Recommended):**
1. Double-click the `setup.js` file
2. Answer the questions (press Enter for defaults)
3. Done!

**Method B - Using Command:**
```bash
npm run setup
```

### Step 3: Start the Server

**Easiest Way - Double-Click:**
- Windows: Double-click `start.bat`
- Mac/Linux: Double-click `start.sh`

**Or Using Command:**
```bash
npm start
```

**Or Using npx:**
```bash
npx .
```

## ✅ Once the Server is Running

Server URL: `http://127.0.0.1:32769` (default)

Configure your chatbot with:
```json
{
  "searxng-enhanced": {
    "url": "http://127.0.0.1:32769",
    "type": "http",
    "method": "sse"
  }
}
```

## 🔧 Changing Settings

Run `setup.js` again, or edit the `.env` file directly:

```env
SEARXNG_BASE_URL=http://localhost:32768  # SearXNG address
PORT=32769                                # Server port
DESIRED_TIMEZONE=UTC                      # Timezone
```

## ❓ Troubleshooting

### "Node.js not found"
→ Install Node.js: https://nodejs.org

### "Python not found"
→ Install Python 3.9+: https://python.org

### "Cannot connect to SearXNG"
→ Make sure SearXNG is running:
```bash
curl http://localhost:32768/search?q=test&format=json
```

### Port already in use
→ Change PORT in `.env` file to a different number (e.g., 8080)

## 💡 More Help

- Detailed docs: See `README.md`
- Example configs: Check `examples/` folder
- NPX usage: See `NPX_USAGE.md`

## 🎉 That's It!

If you have questions, open a GitHub Issue.
