#!/bin/bash

# --------------------------------------------------------------------------- #
# Devloper: Andrew Kirfman                                                    #
# Project: CSCE-483 Smart Greenhouse                                          #
#                                                                             #
# File: ./run_server.sh                                                       #
# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #
# Normal Color Definitions                                                    #
# --------------------------------------------------------------------------- #

BLACK=$(tput setaf 0)
RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 4)
LIME_YELLOW=$(tput setaf 190)
BLUE=$(tput setaf 4)
MAGENTA=$(tput setaf 5)
CYAN=$(tput setaf 6)
WHITE=$(tput setaf 7)
BOLD=$(tput bold)
NORMAL=$(tput sgr0)
BLINK=$(tput blink)
REVERSE=$(tput smso)
UNDERLINE=$(tput smul)

# --------------------------------------------------------------------------- #
# Bold Color Definitions                                                      #
# --------------------------------------------------------------------------- #

BOLDBLACK=${BOLD}${BLACK}
BOLDRED=${BOLD}${RED}
BOLDGREEN=${BOLD}${GREEN}
BOLDYELLOW=${BOLD}${YELLOW}
BOLDLIME_YELLOW=${BOLD}${LIME_YELLOW}
BOLDBLUE=${BOLD}${BLUE}
BOLDMAGENTA=${BOLD}${MAGENTA}
BOLDCYAN=${BOLD}${CYAN}
BOLDWHITE=${BOLD}${WHITE}

# --------------------------------------------------------------------------- #
# Server Initialization Code                                                  #
# --------------------------------------------------------------------------- #

PORT=$1
[ -z $1 ] && PORT=10001

rm *.pyc &> /dev/null
echo "${BOLDWHITE}Running on port $PORT at $(hostname)${NORMAL}" 
echo "${BOLDWHITE}  - Navigate to http://$(hostname):$PORT/${NORMAL}" 
python2.7 server_test.py --port=$PORT --logger="vv"
