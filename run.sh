#!/bin/bash

# export NVIDIA_NIM_API_KEY="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"
export GEMINI_API_KEY="AIzaSyAOsThfG73iYOo3u3cx1v42lCg1Uq9I4g4"
python3 main.py problem=bpp_online algorithm=hsevo
# python3 main.py problem=bpp_online algorithm=hsevo
# python3 main.py problem=bpp_online algorithm=hsevo

python3 main.py problem=bpp_online algorithm=hsevo-qd
# python3 main.py problem=bpp_online algorithm=hsevo-qd
# python3 main.py problem=bpp_online algorithm=hsevo-qd

python3 main.py problem=bpp_online algorithm=reevo
# python3 main.py problem=bpp_online algorithm=reevo
# python3 main.py problem=bpp_online algorithm=reevo

python3 main.py problem=bpp_online algorithm=reevo-qd
# python3 main.py problem=bpp_online algorithm=reevo-qd
# python3 main.py problem=bpp_online algorithm=reevo-qd

