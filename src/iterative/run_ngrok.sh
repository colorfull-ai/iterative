#!/bin/bash


#
###################
#-----------------#
# Made by NullDev #
#-----------------#
###################

###################
#-----------------#
#   NGROK  PATH   #
#-----------------#
###################
NG=ngrok
#-----------------#
###################

###################
#-----------------#
#  PORT TO OPEN   #
#-----------------#
###################
PT=5279
#-----------------#
###################

RAW=null
API=null
FST=null
LNK_HTTP=.
LNK_HTTPS=.
sq='"'
lnpref=public_url
prefix="${lnpref}:"
tnl='localhost:4040/api/tunnels'
#COL
C_RED=$(tput setaf 1)
C_GRN=$(tput setaf 2)
C_YLW=$(tput setaf 3)
C_BLE=$(tput setaf 4)
C_RST=$(tput sgr0)

# Determine the current working directory
CURRENT_DIR=$(pwd)

echo "Current directory: $CURRENT_DIR"

# Construct the path to config.yaml (assuming it's in a subdirectory of the current working directory)
CONFIG_FILE="${CURRENT_DIR}/.iterative/config.yaml"

# Read ngrok_domain and fastapi_port from config.yaml
NGROK_DOMAIN=$(awk -F": " '/ngrok_domain/{print $2}' $CONFIG_FILE)
PORT=$(awk -F": " '/fastapi_port/{print $2}' $CONFIG_FILE)

# Use default PT value if PORT is null or empty
if [[ -z $PORT ]]; then
    PORT=$PT
fi

# Check if NGROK_DOMAIN is set and not empty
if [[ -n $NGROK_DOMAIN ]]; then
    NGROK_CMD="$NG http --domain=$NGROK_DOMAIN $PORT"
else
    NGROK_CMD="$NG http $PORT"
fi


printf " ${C_GRN}Executing ngrok...${C_RST}\n\n"
# EXEC=$($NGROK_CMD >> /dev/null &)
$NGROK_CMD >> /dev/null &
NGROK_PID=$!

sleep 5s

# Fetch ngrok tunnel URL
if ! [ -x "$(command -v curl)" ]; then
    unset API
    API=$(wget -qO - $tnl | awk -F"," -v k=$lnpref '{
        gsub(/{|}/,"")
        for(i=1;i<=NF;i++){
            if ( $i ~ k ){ printf "${i}" }
        }
    }')
else
    unset API
    API=$(curl -s $tnl | awk -F"," -v k=$lnpref '{
        gsub(/{|}/,"")
        for(i=1;i<=NF;i++){
            if ( $i ~ k ){ print $i }
        }
    }')
fi
API=${API//$sq}
API=${API//$prefix}
IFS=$'\n' read -rd '' -a FST <<<"$API"
FST=${FST//http\:\/\/}

# Set LINK_HTTPS to ngrok tunnel URL or custom domain
if [[ -n $NGROK_DOMAIN ]]; then
    LINK_HTTPS="https://${NGROK_DOMAIN}"
else
    LINK_HTTPS="${FST}"
fi

printf " ${C_BLE}NGROK Status: ${C_GRN}ONLINE${C_RST}\n\n"
printf " ${C_BLE}WEBHOOK_DEV_LINK Link (HTTPS): ${C_YLW}${LINK_HTTPS}${C_RST}\n"
printf " ${C_BLE}HOST: ${C_YLW}${LINK_HTTPS}${C_RST}\n"
printf " ${C_BLE}PORT: ${C_YLW}${PORT}${C_RST}\n\n"

# ######## Override the Environment Variables needed at run time ######
export NGROK_EXECUTABLE=$NG
export WEBHOOK_DEV_LINK=$LINK_HTTPS
export CLOUD_RUN_SERVICE_URL=$LINK_HTTPS
export HOST=$LINK_HTTPS

# Write environment variables to a temp file
echo "NGROK_EXECUTABLE=$NG" > /tmp/env_vars.txt
echo "WEBHOOK_DEV_LINK=$LINK_HTTPS" >> /tmp/env_vars.txt
echo "CLOUD_RUN_SERVICE_URL=$LINK_HTTPS" >> /tmp/env_vars.txt
echo "HOST=$LINK_HTTPS" >> /tmp/env_vars.txt