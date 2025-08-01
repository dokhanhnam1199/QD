#!/bin/bash

# export NVIDIA_NIM_API_KEY="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"
export GEMINI_API_KEY="AIzaSyDWz_8AG8ir2JnMbK_fzFl4H66epIQkqFs"
python3 main.py problem=bpp_online algorithm=hsevo

export GEMINI_API_KEY="AIzaSyClMkkPMcAWwnl5TNm1ascII6kACFBJR8w"
python3 main.py problem=bpp_online algorithm=hsevo

export GEMINI_API_KEY="AIzaSyAh0deHriOSJywOPy12D6mW0NFIXQiUFOA"
python3 main.py problem=bpp_online algorithm=hsevo

export GEMINI_API_KEY="AIzaSyBT0seRZasGy5Bez9OTGrF1C8AJzAbOkKI"
python3 main.py problem=bpp_online algorithm=hsevo-qd

export GEMINI_API_KEY="AIzaSyCGyujN5lrt_Xzx1mh822TFU_m7v9lhUk0"
python3 main.py problem=bpp_online algorithm=hsevo-qd

export GEMINI_API_KEY="AIzaSyA8oz7wwkIhL8mTlMbBRivM2If5_5Xg0cI"
python3 main.py problem=bpp_online algorithm=hsevo-qd

export GEMINI_API_KEY="AIzaSyAO4_Ef7POQDbKuFEs48jMsW2DNzOz-yr0"
python3 main.py problem=bpp_online algorithm=reevo

export GEMINI_API_KEY="AIzaSyDUa7OM0Bzs39ko8k5q4FsS-WvLCMK-R_g"
python3 main.py problem=bpp_online algorithm=reevo

export GEMINI_API_KEY="AIzaSyACSFh8rYeMI0g1SIpTtaA8zrv3RMFgvag"
python3 main.py problem=bpp_online algorithm=reevo

export GEMINI_API_KEY="AIzaSyDNaiNFZH9wfeOuKRKwvxZpBYEnMaz0XIs"
python3 main.py problem=bpp_online algorithm=reevo-qd

export GEMINI_API_KEY="AIzaSyAcZkFgnw7Wng7OyaNTdPEkvxmU5xmCoe8"
python3 main.py problem=bpp_online algorithm=reevo-qd

export GEMINI_API_KEY="AIzaSyDfvAYFsYjunymV2TaCVzblh_BFz0B1G7M"
python3 main.py problem=bpp_online algorithm=reevo-qd

