#!/bin/bash

# Set Gemini API key
export GEMINI_API_KEY="AIzaSyDNaiNFZH9wfeOuKRKwvxZpBYEnMaz0XIs"

# Run Python scripts
python3 main.py problem=bpp_online algorithm=hsevo
python3 main.py problem=bpp_online algorithm=hsevo-qd
python3 main.py problem=bpp_online algorithm=reevo
python3 main.py problem=bpp_online algorithm=reevo-qd

# Set Gemini API key
export GEMINI_API_KEY="AIzaSyACSFh8rYeMI0g1SIpTtaA8zrv3RMFgvag"

# Run Python scripts
python3 main.py problem=bpp_online algorithm=hsevo
python3 main.py problem=bpp_online algorithm=hsevo-qd
python3 main.py problem=bpp_online algorithm=reevo
python3 main.py problem=bpp_online algorithm=reevo-qd

# Set Gemini API key
export GEMINI_API_KEY="AIzaSyAcZkFgnw7Wng7OyaNTdPEkvxmU5xmCoe8"

# Run Python scripts
python3 main.py problem=bpp_online algorithm=hsevo
python3 main.py problem=bpp_online algorithm=hsevo-qd
python3 main.py problem=bpp_online algorithm=reevo
python3 main.py problem=bpp_online algorithm=reevo-qd