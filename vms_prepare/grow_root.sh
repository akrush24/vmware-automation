#!/bin/bash
if [[ -z $1 ]];then read -p "Enter the IP address, please: " HOST;else HOST=$1;fi
#if [[ -z $2 ]];then read -p "Enter the USER name,  please: " USER;else USER=$2;fi
if [[ -z $2 ]];then USER=root;else USER=$2;fi

if [[ $3 -ne "-s" ]];
then
  echo -e "\nAre You sure You want to repartition root filesystem in ${HOST}?\n\nWARNING!\n\nThis procedure may result in loss of all data in ${HOST}!\n"
  read -p "Please type ${HOST} to run or anything should exit: " ANS
  if [[ ${ANS} != ${HOST} ]];then echo Bay Bay;exit;fi
fi

DIRECTORY=`dirname $0`

ssh-keygen -R ${HOST}

scp ${DIRECTORY}/grow-root-part*.sh ${USER}@${HOST}:~/ || (ssh -o StrictHostKeyChecking=no ${USER}@${HOST} \
"which scp || (ls -l /etc/redhat-release && yum install -y openssh-clients);" && \
scp ${DIRECTORY}/grow-root-partI.sh grow-root-partII.sh ${USER}@${HOST}:~/)

ssh -o StrictHostKeyChecking=no ${USER}@${HOST} "/bin/bash ~/grow-root-partI.sh && /bin/rm ~/grow-root-partI.sh && reboot" && echo -e "\n\n PART I .... OK!"

sleep 20

for t in $(seq 10)
do
  ping ${HOST} -c 2 &>/dev/null
  if [ $? -eq 0 ];then echo -e "\n Server ["${HOST}"] is alive, exit";break; else echo $t" - Server is not available"; sleep 10; fi
done

for t in $(seq 10)
do
  echo "Try ssh connect to" ${USER}@${HOST}
  ssh -o StrictHostKeyChecking=no ${USER}@${HOST} "if [[ -f ~/grow-root-partII.sh ]];then /bin/bash ~/grow-root-partII.sh&&/bin/rm ~/grow-root-partII.sh;else echo 'No file ~/grow-root-partII.sh';fi" && echo -e "\n\n PART II .... OK!"
  if [ $? -eq 0 ];then echo  -e "\n loop exit!"; break; else sleep 10; fi
done

for t in $(seq 10)
do
  ping ${HOST} -c 2 &>/dev/null
  if [ $? -eq 0 ];then echo -e "\n Server ["${HOST}"] is alive, exit";break; else echo $t" - Server is not available"; sleep 10; fi 
done
