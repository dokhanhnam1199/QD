#!/bin/bash

# Set Gemini API key
export GEMINI_API_KEY="AIzaSyDWz_8AG8ir2JnMbK_fzFl4H66epIQkqFs"

# Run Python scripts
python3 main.py problem=bpp_online algorithm=hsevo-qd 
python3 main.py problem=bpp_online algorithm=reevo-qd 
python3 main.py problem=bpp_online algorithm=eoh-qd

# Set Gemini API key
export GEMINI_API_KEY="AIzaSyDfvAYFsYjunymV2TaCVzblh_BFz0B1G7M"

# Run Python scripts
python3 main.py problem=bpp_online algorithm=hsevo-qd 
python3 main.py problem=bpp_online algorithm=reevo-qd 
python3 main.py problem=bpp_online algorithm=eoh-qd  
