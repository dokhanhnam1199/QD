#!/bin/bash

# Set Gemini API key
export GEMINI_API_KEY="AIzaSyDNaiNFZH9wfeOuKRKwvxZpBYEnMaz0XIs"

# Run Python scripts
python3 main.py problem=bpp_online algorithm=hsevo

# Set Gemini API key
export GEMINI_API_KEY="AIzaSyACSFh8rYeMI0g1SIpTtaA8zrv3RMFgvag"

# Run Python scripts
python3 main.py problem=bpp_online algorithm=hsevo-qd

# Set Gemini API key
export GEMINI_API_KEY="AIzaSyAcZkFgnw7Wng7OyaNTdPEkvxmU5xmCoe8"

# Run Python scripts
python3 main.py problem=bpp_online algorithm=reevo

# Set Gemini API key
export GEMINI_API_KEY="AIzaSyDfvAYFsYjunymV2TaCVzblh_BFz0B1G7M"

# Run Python scripts
python3 main.py problem=bpp_online algorithm=reevo-qd
