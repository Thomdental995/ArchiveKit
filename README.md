# Web Archive Downloader

[![Release](https://img.shields.io/github/v/tag/pinkythegawd/ArchiveKit?label=release)](https://github.com/pinkythegawd/ArchiveKit/releases/tag/v1.0-rc1)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-0A7E3B)](https://github.com/pinkythegawd/ArchiveKit)
[![Open Source](https://img.shields.io/badge/open%20source-yes-1f883d)](https://github.com/pinkythegawd/ArchiveKit)
[![Stars](https://img.shields.io/github/stars/pinkythegawd/ArchiveKit?style=social)](https://github.com/pinkythegawd/ArchiveKit/stargazers)
[![Issues](https://img.shields.io/github/issues/pinkythegawd/ArchiveKit)](https://github.com/pinkythegawd/ArchiveKit/issues)
[![Downloads](https://img.shields.io/github/downloads/pinkythegawd/ArchiveKit/v1.0-rc1/total)](https://github.com/pinkythegawd/ArchiveKit/releases/tag/v1.0-rc1)
[![License](https://img.shields.io/github/license/pinkythegawd/ArchiveKit)](https://github.com/pinkythegawd/ArchiveKit/blob/main/LICENSE)
[![CI](https://github.com/pinkythegawd/ArchiveKit/actions/workflows/ci.yml/badge.svg)](https://github.com/pinkythegawd/ArchiveKit/actions/workflows/ci.yml)

Made by MikePinku

Download archived websites from the Internet Archive Wayback Machine with a simple Python CLI.
This project is focused on practical offline archiving for Windows and Linux users.

## ✨ Why This Project

Web Archive Downloader helps you quickly capture archived snapshots and view them locally.
It is designed to be simple, stable, and friendly for both beginners and power users.

## 🧭 Table of Contents

- [📌 Platform Support](#-platform-support)
- [🚀 Features](#-features)
- [⚙️ Setup and Installation](#-setup-and-installation)
- [💻 Daily Use Installation](#-daily-use-installation)
- [🧪 Usage Examples](#-usage-examples)
- [📂 Output Structure](#-output-structure)
- [❓ FAQ](#-faq)
- [🤝 Contributing](#-contributing)
- [🐞 Known Issues](#-known-issues)
- [📝 What's Changed](#-whats-changed)

## 📌 Platform Support

This tool is intentionally limited to:
- Windows
- Linux

If the program is run on another OS, it exits with a clear platform message.

## 🚀 Features

- Download archived pages from normal URLs or direct Wayback URLs
- Keep exact Wayback timestamp when a full Wayback link is provided
- Download HTML and common assets (CSS, JS, images, media)
- Rewrite links so saved pages work offline
- Optional same-host crawl depth for broader page capture
- Friendly CLI messages (welcome, progress, success, error)
- Built-in version output with --version

## ⚙️ Setup and Installation

### Option A: Using .venv (recommended)

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

Quick verification:

Windows:

```powershell
.\.venv\Scripts\python.exe web_archive_downloader.py --help
```

Linux:

```bash
python3 web_archive_downloader.py --help
```

### Option B: Without .venv (system-wide or user install)

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

Note: Some Linux distributions use externally managed Python environments. If that happens, use Option A.

## 💻 Daily Use Installation

If you want to run the tool from anywhere:

Windows:
- Keep the project in a permanent folder.
- Use a full path command or create a small .bat launcher in a directory that is already in PATH.

Linux:
- Keep the project in a permanent folder.
- Add an alias in your shell config (for example .bashrc):

```bash
alias wad='python3 /absolute/path/to/web_archive_downloader.py'
```

Then run:

```bash
wad --help
```

## 🧪 Usage Examples

Basic download:

```bash
python web_archive_downloader.py https://example.com
```

Download with preferred timestamp:

```bash
python web_archive_downloader.py https://example.com --timestamp 20200101120000
```

Download from a direct Wayback URL (exact snapshot):

```bash
python web_archive_downloader.py https://web.archive.org/web/20260122131334/https://example.com
```

Download with crawl depth:

```bash
python web_archive_downloader.py https://example.com --depth 1
```

Show version:

```bash
python web_archive_downloader.py --version
```

## 📂 Output Structure

```text
downloads/
  example.com_20200101120000/
    pages/
    assets/
```

## ❓ FAQ

### Who made this program and who are you?

yes, my name is Mickael H-G (known as pinkythegawd and MikePinku), i am born in Montreal, Quebec and i am aged 20 years old. i love video games and making program tools and designing websites, those things are my personal favorite things to do and i absolutely love computers, phones and technology. i live with an spectrum autism disorder with an ADHD, but it doesn't let me go my dreams or wishes even thought i am autistic. everyone can make their dream come true, you just have to be patient and live will go on.

### How was this program made?

This tool was built in Python with:
- requests for HTTP access
- BeautifulSoup for HTML parsing and rewriting
- argparse for command-line argument handling

### Why are some pages or assets missing?

Some files do not exist in specific archive snapshots, and Wayback may return temporary errors. The downloader continues by skipping unavailable assets when possible.

## 🤝 Contributing

Contributions are welcome.

1. Fork the project.
2. Create a new branch for your work.
3. Make your changes with clear commit messages.
4. Test your changes on Windows or Linux.
5. Open a pull request with a short explanation.

Areas where contributions are especially helpful:
- Better asset type coverage
- Retry and network resilience improvements
- Packaging and installer improvements
- Tests and documentation

## 🐞 Known Issues

- Wayback endpoints can be slow or return temporary 5xx errors.
- Some JavaScript-heavy sites may not fully work offline.
- Not every archived asset exists for every timestamp.
- Higher crawl depth values can increase runtime significantly.

## 📝 What's Changed

### v1.0-rc1

- Added a welcome screen to the CLI
- Added clear progress, success, and error messages
- Added direct Wayback URL input with exact timestamp handling
- Improved text decoding to reduce garbled characters
- Added --version support
