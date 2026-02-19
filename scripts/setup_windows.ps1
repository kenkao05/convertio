Write-Host "Setting up Convertio dependencies..."

# Requires winget (comes with Windows 11 / updated Windows 10)
winget install --id Python.Python.3 -e --source winget
winget install --id TheDocumentFoundation.LibreOffice -e --source winget
winget install --id Gyan.FFmpeg -e --source winget
winget install --id ImageMagick.ImageMagick -e --source winget
winget install --id JohnMacFarlane.Pandoc -e --source winget

# Poppler has no winget package — download manually
Write-Host ""
Write-Host "NOTE: Poppler must be installed manually for PDF->image conversions."
Write-Host "Download from: https://github.com/oschwartz10612/poppler-windows/releases"
Write-Host "Extract and add the bin/ folder to your PATH."
Write-Host ""

pip install -r requirements.txt

Write-Host "Done. Run with: python app.py"
