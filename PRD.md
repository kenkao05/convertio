# Personal File Conversion Tool – Product Requirements Document (PRD)

## 1. Overview

### Product Name

Local Universal Converter (Working Title)

### Purpose

A lightweight, locally running file conversion tool designed for personal use.  
The application allows users to upload a file, automatically detect its format, view valid conversion options, convert it, track progress, and download the result.

The tool runs entirely on the user's local machine and relies on system-installed conversion engines.

---

## 2. Goals

- Provide reliable conversion between practical, real-world formats.
- Keep the UI extremely simple and intuitive.
- Ensure minimal setup complexity.
- Use trusted system tools for conversion.
- Avoid unnecessary or illogical conversions.
- Maintain clean architecture for GitHub showcase.

---

## 3. Non-Goals

- No cloud hosting.
- No user accounts.
- No multi-user support.
- No online processing.
- No support for obscure file formats.
- No batch processing (MVP scope).

---

## 4. Supported Formats

### 4.1 Document Formats

- PDF (.pdf)
- PowerPoint (.pptx)
- Word (.docx)

### 4.2 Image Formats

- PNG (.png)
- JPG (.jpg)
- JPEG (.jpeg)
- WEBP (.webp)

### 4.3 Audio Formats

- MP3 (.mp3)

### 4.4 Video Formats

- MP4 (.mp4)
- WEBM (.webm)

---

## 5. Conversion Rules

### 5.1 Document Conversions

| Input | Allowed Outputs            |
| ----- | -------------------------- |
| pptx  | pdf                        |
| docx  | pdf                        |
| pdf   | pptx, docx, png, jpg, jpeg |

Notes:

- Direct pptx ↔ docx conversion is not supported.
- Formatting preservation depends on LibreOffice capabilities.

---

### 5.2 Image Conversions

| Input | Allowed Outputs      |
| ----- | -------------------- |
| png   | jpg, jpeg, webp, pdf |
| jpg   | png, jpeg, webp, pdf |
| jpeg  | png, jpg, webp, pdf  |
| webp  | png, jpg, jpeg, pdf  |

---

### 5.3 Media Conversions

| Input | Allowed Outputs |
| ----- | --------------- |
| mp3   | mp4, webm       |
| mp4   | webm, mp3       |
| webm  | mp4, mp3        |

Notes:

- Audio → Video creates a static-background video.
- Video → Audio extracts audio stream.

---

## 6. User Flow

1. User opens the application in browser.
2. User uploads a file.
3. Backend:
   - Detects file type.
   - Returns valid conversion options.
4. UI dynamically shows available formats.
5. User selects target format.
6. User clicks "Convert".
7. Progress bar appears.
8. Conversion completes.
9. Download button becomes available.
10. User downloads converted file.

---

## 7. Functional Requirements

### 7.1 File Upload

- Accept single file.
- Validate file extension and MIME type.
- Store temporarily in `/uploads`.

### 7.2 Format Detection

- Detect using MIME type and extension.
- Reject unsupported formats.

### 7.3 Conversion Engine Routing

Backend selects engine based on file type:

| Conversion Type | Engine                 |
| --------------- | ---------------------- |
| Document        | LibreOffice (headless) |
| Image → Image   | ImageMagick            |
| Image → PDF     | ImageMagick            |
| PDF → Image     | Poppler                |
| Media           | FFmpeg                 |

### 7.4 Progress Tracking

- Backend streams progress (if supported by engine).
- Frontend updates progress bar.
- If live tracking unavailable, use staged progress indicator.

### 7.5 File Download

- Converted file stored in `/output`.
- Download served via backend route.
- Optional auto-delete after download.

---

## 8. Technical Stack

### Frontend

- HTML
- CSS
- Vanilla JavaScript (Fetch API)

### Backend

- Python 3
- Flask (or built-in HTTP server)
- subprocess module

### System Dependencies

- LibreOffice
- ImageMagick
- FFmpeg
- Poppler

---

## 9. Directory Structure

project-root/
│
├── app.py
├── PRD.md
├── static/
│ ├── style.css
│ └── script.js
├── templates/
│ └── index.html
├── uploads/
├── output/
└── README.md

---

## 10. Error Handling

- Unsupported format → show error message.
- Conversion failure → display failure notification.
- File size limits enforced.
- Invalid file content rejected.

---

## 11. Performance Requirements

- Conversion should begin within 2 seconds.
- Files under 50MB should convert without timeout.
- No memory leaks from subprocess handling.
- Temporary files cleaned periodically.

---

## 12. Security Considerations

- Restrict allowed file types.
- Sanitize filenames.
- Do not allow arbitrary command execution.
- Use controlled subprocess arguments.
- Prevent directory traversal attacks.

---

## 13. Future Enhancements (Optional)

- Batch file conversion.
- Drag-and-drop UI.
- Dark mode.
- Progress estimation accuracy improvements.
- Portable AppImage build.
- Windows support.

---

## 14. Success Criteria

- All defined conversions work reliably.
- No crashes during typical usage.
- Setup instructions clear and reproducible.
- Clean GitHub repository structure.
- Easy for another developer to clone and run.

---

End of Document.
