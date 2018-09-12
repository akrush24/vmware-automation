#!/bin/bash
if [[ -z $1 ]];then read -p "Enter the IP address, please: " HOST;else HOST=$1;fi
if [[ -z $2 ]];then read -p "Enter the USER name,  please: " USER;else USER=$2;fi
if [[ -z $3 ]];then read -p "Enter new mashin name, please: " HOST_NAME;else HOST_NAME=$3;fi


/usr/bin/ssh-keygen -R ${HOST}
ssh ${USER}@${HOST} <<EOF!
HOST_NAME=${HOST_NAME} 
IT=${HOST}

if [[ -z \${HOST_NAME}  ]];then HOST_NAME=\`/bin/hostname\`;fi
if [[ -f /etc/redhat-release ]]
then 
  if [[ \`egrep "release\ [56]" /etc/redhat-release\` ]]
  then
    echo -e "NETWORKING=yes\nHOSTNAME=\${HOST_NAME}\nDHCP_HOSTNAME=\${HOST_NAME}" > /etc/sysconfig/network 
  else
    echo -e "NETWORKING=yes\nHOSTNAME=\${HOST_NAME}\nDHCP_HOSTNAME=\${HOST_NAME}" > /etc/sysconfig/network
    echo \${HOST_NAME} > /etc/hostname
  fi
  hostname \${HOST_NAME}
elif [[ -f /etc/issue ]]
then
  if [[ \`egrep "Ubuntu" /etc/issue\` ]]
  then
    echo \${HOST_NAME} > /etc/hostname
  fi
fi
reboot
EOF!

