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
PT=8000
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

pkill -f ngrok
printf " ${C_GRN}Executing ngrok...${C_RST}\n\n"
EXEC=$($NG http $PT >> /dev/null &)
sleep 5s
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
sleep 1s
LNK_HTTP="${FST}"
LNK_HTTPS="${FST}"
printf " ${C_BLE}NGROK Status: ${C_GRN}ONLINE${C_RST}\n\n"
printf " ${C_BLE}Link (HTTPS): ${C_YLW}${LNK_HTTPS}${C_RST}\n"
printf "\n"

# ######## Override the Environment Variables needed at run time ######
export NGROK_EXECUTABLE=$NG
# LNK_HTTPS is the HTTPS URL that ngrok provides
export WEBHOOK_DEV_LINK=$LNK_HTTPS
export CLOUD_RUN_SERVICE_URL=$LNK_HTTPS
export HOST=$LNK_HTTPS