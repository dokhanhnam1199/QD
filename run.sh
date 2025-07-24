#!/bin/bash

export NVIDIA_NIM_API_KEY="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"

python3 main.py problem=bpp_online algorithm=hsevo

#python3 main.py problem=bpp_online algorithm=hsevo-qd

python3 main.py problem=bpp_online algorithm=reevo

python3 main.py problem=bpp_online algorithm=reevo-qd

python3 main.py problem=bpp_online algorithm=hsevo

python3 main.py problem=bpp_online algorithm=hsevo-qd

python3 main.py problem=bpp_online algorithm=reevo

python3 main.py problem=bpp_online algorithm=reevo-qd

python3 main.py problem=bpp_online algorithm=hsevo

python3 main.py problem=bpp_online algorithm=hsevo-qd

python3 main.py problem=bpp_online algorithm=reevo

python3 main.py problem=bpp_online algorithm=reevo-qd
