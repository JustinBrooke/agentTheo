# Catholic Theological Review Agent

An AI-powered assistant that reviews Catholic blog posts and articles for theological accuracy, proper citations, and alignment with authentic Church teaching.

## What is this?

This is a tool that helps Catholic bloggers, writers, and content creators ensure their articles are theologically accurate. It automatically checks your writing against:

- The Catechism of the Catholic Church
- Official Vatican documents and papal encyclicals
- The writings of the Church Fathers
- Catholic Encyclopedia and scholarly sources

Think of it as a friendly theological fact-checker that helps you avoid errors before publishing.

## What it checks

- **Doctrinal accuracy**: Are your theological claims correct according to Church teaching?
- **Quote verification**: Are your citations accurate and properly sourced?
- **Historical facts**: Are historical claims about the Church accurate?
- **Scripture interpretation**: Does your biblical interpretation align with Catholic teaching?
- **Church Fathers**: Are references to patristic writings accurate?

## What you'll get

After reviewing your article, the tool provides:

1. A summary of your main theological points
2. A detailed analysis of each claim with verification status
3. Citation accuracy checks
4. A list of any issues that need correction
5. Suggestions for improvement
6. An overall assessment (Approved / Needs Revision / Major Concerns / Not Recommended)

---

## Getting Started (Step-by-Step Guide)

### What you'll need

1. A computer (Windows, Mac, or Linux)
2. Internet connection
3. About 15 minutes for setup (one-time only)

Don't worry if you've never used a command line or terminal before - we'll walk through everything!

### Step 1: Install Python

Python is a programming language that this tool is built with. You need it installed on your computer.

**For Windows:**
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click the big yellow "Download Python" button
3. Run the installer
4. **IMPORTANT**: Check the box that says "Add Python to PATH" before clicking Install
5. Click "Install Now"

**For Mac:**
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download the macOS installer
3. Run the installer and follow the prompts

**For Linux:**
Python is usually already installed. To check, open Terminal and type: `python3 --version`

### Step 2: Open your Terminal (Command Line)

This is where you'll type commands to run the tool.

**For Windows:**
- Press the Windows key and type "Command Prompt" or "PowerShell"
- Click to open it

**For Mac:**
- Press Command + Space to open Spotlight
- Type "Terminal" and press Enter

**For Linux:**
- Press Ctrl + Alt + T
- Or find "Terminal" in your applications menu

### Step 3: Download this tool

In your terminal, copy and paste these commands one at a time, pressing Enter after each:

```bash
cd Desktop
git clone https://github.com/JustinBrooke/agentTheo.git
cd agentTheo
```

**What this does:**
- `cd Desktop` - Moves to your Desktop folder (easier to find)
- `git clone...` - Downloads the tool to your computer
- `cd agentTheo` - Opens the tool's folder

**Don't have git installed?** You might see an error. If so:
- **Windows**: Download from [git-scm.com](https://git-scm.com/)
- **Mac**: It will prompt you to install it automatically
- **Linux**: Run `sudo apt install git` (Ubuntu/Debian) or `sudo yum install git` (Fedora/RedHat)

### Step 4: Set up the tool

Still in your terminal, run this command:

```bash
python -m venv venv
```

**For Mac/Linux, use:**
```bash
python3 -m venv venv
```

**What this does:** Creates a special isolated space for this tool (called a "virtual environment"). This keeps everything organized and won't affect other programs on your computer.

### Step 5: Activate the virtual environment

**For Windows:**
```bash
venv\Scripts\activate
```

**For Mac/Linux:**
```bash
source venv/bin/activate
```

**What this does:** Turns on that isolated space we just created. You'll see `(venv)` appear at the beginning of your command line - that means it's working!

### Step 6: Install the tool

```bash
pip install -e .
```

**What this does:** Installs all the pieces the tool needs to run. This might take a minute or two. You'll see some text scrolling by - that's normal!

### Step 7: Get your access keys (API keys)

The tool needs special access keys to look up information from different Catholic databases. Think of these like library cards that let the tool access different resources.

**You need two keys:**

1. **Anthropic API Key** (for the AI that does the reviewing)
   - Go to [console.anthropic.com](https://console.anthropic.com/)
   - Sign up for an account (it's free to start)
   - Once logged in, find "API Keys" in the menu
   - Click "Create Key" and copy the key (it looks like: `sk-ant-...`)
   - **Cost**: You get free credits to try it out, then pay-as-you-go (typically a few cents per review)

2. **Magisterium API Key** (for Church teaching database)
   - Go to [magisterium.com](https://magisterium.com/) and create an account
   - Find the API section to get your key
   - Note: Check their current API access policy

### Step 8: Set up your keys

In the `agentTheo` folder on your Desktop, you'll see a file called `.env.example`.

1. Make a copy of this file and rename it to just `.env` (remove the .example part)
2. Open the `.env` file in any text editor (Notepad, TextEdit, etc.)
3. You'll see:
   ```
   MAGISTERIUM_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   ```
4. Replace `your_key_here` with your actual keys (the ones you got in Step 7)
5. Save the file

**Security note:** Never share your `.env` file or post your keys online!

---

## How to Use the Tool

Now you're ready to review articles! Make sure your terminal is still open with `(venv)` showing.

### Review a blog post from your computer

If you have your blog post saved as a file (like `my-article.md` or `my-article.txt`):

```bash
agentTheo review ./my-article.md
```

The tool will read your article and show you the review right in the terminal!

### Review a blog post from a website

If the article is already published online:

```bash
agentTheo review https://example.com/blog/my-post
```

### Save the review to a file

To save the review so you can read it later:

```bash
agentTheo review ./my-article.md -o review.md
```

This creates a file called `review.md` with the full review that you can open in any text editor.

### Quick checks

**Check a single theological claim:**
```bash
agentTheo check "The Eucharist is the real presence of Christ"
```

**Look up a Catechism paragraph:**
```bash
agentTheo catechism 1374
```

**Search for a topic:**
```bash
agentTheo search "transubstantiation"
```

---

## Understanding the Review

The tool categorizes Church teaching by authority level:

| Level | What it means |
|-------|---------------|
| **De fide definita** | Defined dogma - Catholics must believe this |
| **Sententia certa** | Theologically certain - very strong teaching |
| **Sententia communis** | Common teaching - widely accepted |
| **Sententia probabilis** | Probable opinion - respected theological view |
| **Opinio tolerata** | Tolerated opinion - acceptable to hold |

---

## Troubleshooting

**"Command not found" errors:**
- Make sure you activated the virtual environment (Step 5)
- Make sure you installed the tool (Step 6)

**"Permission denied" errors:**
- On Mac/Linux, you might need to add `sudo` before a command
- Or check that you have write permissions in the folder

**"Invalid API key" errors:**
- Double-check that you copied your keys correctly into the `.env` file
- Make sure there are no extra spaces
- Make sure the file is named exactly `.env` (not `.env.txt`)

**The tool seems stuck:**
- It might be processing - wait a minute or two
- Press Ctrl+C to cancel and try again

**Need to stop?**
- Press Ctrl+C to stop the tool
- Type `deactivate` to turn off the virtual environment
- Type `exit` to close the terminal

---

## Next time you want to use the tool

You don't have to do all the setup steps again! Just:

1. Open Terminal
2. Navigate to the folder: `cd Desktop/agentTheo`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Run your command: `agentTheo review ./my-article.md`

---

## Getting Help

- **Issues with the tool?** Open an issue at: [github.com/JustinBrooke/agentTheo/issues](https://github.com/JustinBrooke/agentTheo/issues)
- **Don't understand a theological term?** Check the [Catholic Answers website](https://www.catholic.com/)
- **General questions?** Include them when you open a GitHub issue

---

## Important Disclaimer

This tool is designed to assist human reviewers, not replace them. Always have your theological content reviewed by qualified theologians or your spiritual director before publication. The tool helps catch errors and verify sources, but human wisdom and pastoral sensitivity are irreplaceable.

---

## For Developers

If you're comfortable with code and want to integrate this into your own projects, see the [Developer Guide](docs/developer-guide.md) (coming soon) for programmatic usage, testing, and contribution guidelines.

---

## License

MIT License - See LICENSE file for details. This means you're free to use and modify this tool, even for commercial purposes.
