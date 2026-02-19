# Convertio

A hobby project I built because I was tired of uploading files to random websites just to convert a PDF or flip an image format. Everything runs locally — nothing leaves your machine.

Mainly useful if you're a CS student or engineer who constantly needs to convert lecture slides, reports, or documentation between formats without thinking about it too much.

---

## What it does

Upload a file, pick a target format, download the result. That's it.

**Supported conversions:**

| Input                   | Output options              |
| ----------------------- | --------------------------- |
| PDF                     | PPTX, DOCX, PNG, JPG, JPEG  |
| PPTX                    | PDF                         |
| DOCX                    | PDF, MD                     |
| MD                      | PDF, DOCX                   |
| PNG / JPG / JPEG / WEBP | any other image format, PDF |
| MP4 / WEBM              | each other, MP3             |
| MP3                     | MP4, WEBM                   |

PDF → image exports every page as a ZIP of images. Audio → video wraps it in a black-background video.

---

## Setup

### Prerequisites

The app is a thin Flask wrapper around four system tools. You need all of them installed.

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install libreoffice ffmpeg imagemagick poppler-utils pandoc python3 python3-pip
```

Or just run the setup script:

```bash
chmod +x installation/setup_linux.sh && ./installation/setup_linux.sh
```

#### macOS

You need [Homebrew](https://brew.sh) first, then:

```bash
brew install libreoffice ffmpeg imagemagick poppler pandoc python3
```

Or run:

```bash
chmod +x installation/setup_mac.sh && ./installation/setup_mac.sh
```

#### Windows

Install manually:

- [Python 3](https://www.python.org/downloads/) — check "Add to PATH"
- [LibreOffice](https://www.libreoffice.org/download/libreoffice/)
- [FFmpeg](https://ffmpeg.org/download.html) — add `bin/` folder to PATH
- [ImageMagick](https://imagemagick.org/script/download.php#windows)
- [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases) — add `bin/` to PATH
- [Pandoc](https://pandoc.org/installing.html)

Or run the setup script (requires admin PowerShell + [winget](https://aka.ms/winget)):

```powershell
.\installation\setup_windows.ps1
```

---

### Running the app

```bash
pip3 install -r requirements.txt
python3 app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

---

## Project structure

```
convertio/
├── app.py                        # Flask backend, conversion logic
├── requirements.txt
├── PRD.md                        # Original spec
├── README.md
├── templates/
│   └── index.html                # UI
├── static/
│   ├── style.css
│   └── script.js
├── installation/
│   ├── setup_linux.sh
│   ├── setup_mac.sh
│   └── setup_windows.ps1
├── uploads/                      # Temp storage, auto-cleared after download
└── output/                       # Temp storage, auto-cleared after download
```

---

## Notes

- Max file size: 50MB
- Converted files are deleted automatically after you download them
- Formatting quality for document conversions depends on LibreOffice
- This is a local tool — don't expose it to the internet

---

Built for personal use. Works on my machine.
