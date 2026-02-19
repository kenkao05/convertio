#!/bin/bash
echo "Setting up Convertio dependencies..."

sudo apt update
sudo apt install -y libreoffice ffmpeg imagemagick poppler-utils pandoc python3 python3-pip

pip3 install -r requirements.txt

echo ""
echo "Done. Run with: python3 app.py"
