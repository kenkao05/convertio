#!/bin/bash
echo "Setting up Convertio dependencies..."

if ! command -v brew &> /dev/null; then
  echo "Homebrew not found. Installing..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

brew install ffmpeg imagemagick poppler pandoc python3
brew install --cask libreoffice

pip3 install -r requirements.txt

echo ""
echo "Done. Run with: python3 app.py"
