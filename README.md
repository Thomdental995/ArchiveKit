# Web Archive Downloader

Made by MikePinku

Web Archive Downloader is a Python CLI tool that downloads archived website snapshots from the Internet Archive Wayback Machine and saves them for local offline viewing.

## Platform Support

This tool is intentionally limited to:
- Windows
- Linux

If you run it on another OS, it exits with a clear message.

## Features

- Download archived pages from normal URLs or direct Wayback URLs
- Keep exact Wayback timestamp when a full Wayback link is used
- Download HTML and common assets (CSS, JS, images, media)
- Rewrite links so saved pages work offline
- Optional same-host crawl depth
- Friendly CLI messages (welcome, progress, success, error)
- Version flag support via --version

## Setup and Installation

### Option A: Setup with .venv (recommended)

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux (bash):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the tool:

Windows:

```powershell
.\.venv\Scripts\python.exe web_archive_downloader.py --help
```

Linux:

```bash
python3 web_archive_downloader.py --help
```

### Option B: Setup without .venv (system-wide or user install)

Windows:

```powershell
py -m pip install -r requirements.txt
py web_archive_downloader.py --help
```

Linux:

```bash
python3 -m pip install --user -r requirements.txt
python3 web_archive_downloader.py --help
```

Note: On Linux distributions with externally managed Python environments, prefer Option A (.venv).

## Install the Tool for Daily Use

If you want to run it from anywhere on your computer:

Windows:
- Keep the project in a permanent folder.
- Use the full command path or create a small .bat launcher in a folder that is in PATH.

Linux:
- Keep the project in a permanent folder.
- Create a shell alias in your shell profile (for example .bashrc):

```bash
alias wad='python3 /absolute/path/to/web_archive_downloader.py'
```

Then run:

```bash
wad --help
```

## Usage

Basic download:

```bash
python web_archive_downloader.py https://example.com
```

Download with preferred timestamp:

```bash
python web_archive_downloader.py https://example.com --timestamp 20200101120000
```

Download from direct Wayback URL (exact snapshot):

```bash
python web_archive_downloader.py https://web.archive.org/web/20260122131334/https://example.com
```

Show version:

```bash
python web_archive_downloader.py --version
```

## Output Structure

```text
downloads/
  example.com_20200101120000/
    pages/
    assets/
```

## FAQ

### Who made this program and who are you?

yes, my name is Mickael H-G (known as pinkythegawd and MikePinku), i am born in Montreal, Quebec and i am aged 20 years old. i love video games and making program tools and designing websites, those things are my personal favorite things to do and i absolutely love computers, phones and technology. i live with an spectrum autism disorder with an ADHD, but it doesn't let me go my dreams or wishes even thought i am autistic. everyone can make their dream come true, you just have to be patient and live will go on.

### How was this program made?

This tool was made in Python using:
- requests for HTTP access
- BeautifulSoup for HTML parsing and rewriting
- argparse for command-line options

### Why are some pages or assets missing?

Some assets are not available in the archive snapshot or return errors from Wayback. The tool skips unavailable assets so the full download process can continue.

## Contributing My Project

Contributions are welcome.

1. Fork the project.
2. Create a new branch for your changes.
3. Make your changes with clear commit messages.
4. Test on Windows or Linux.
5. Open a pull request with a short explanation of what changed.

Suggested contribution areas:
- Better asset type handling
- Retry strategy and performance improvements
- Better packaging and installer flow
- Additional tests and docs

## Bugs (Known Issues)

- Wayback endpoints can be slow or return temporary 5xx errors.
- Some dynamic JavaScript-heavy pages may not work perfectly offline.
- Not every archived asset exists for every timestamp.
- Crawl depth above 0 can increase runtime significantly.

## What's Changed (Version)

### 1.0-rc1

- Added welcome screen in CLI
- Added progress/success/error user messages
- Added direct Wayback URL input support with exact timestamp handling
- Improved text decoding to reduce garbled characters
- Added --version support
