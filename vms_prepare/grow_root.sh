#!/bin/bash
if [[ -z $1 ]];then read -p "Enter the IP address, please: " HOST;else HOST=$1;fi
#if [[ -z $2 ]];then read -p "Enter the USER name,  please: " USER;else USER=$2;fi
if [[ -z $2 ]];then USER=root;else USER=$2;fi

echo -e "\nAre You sure You want to repartition root filesystem in ${HOST}?\n\nWARNING!\n\nThis procedure may result in loss of all data in ${HOST}!\n"
read -p "Please type ${HOST} to run or anything should exit: " ANS
if [[ ${ANS} != ${HOST} ]];then echo Bay Bay;exit;fi



ssh-keygen -R ${HOST}

scp grow-root-part*.sh ${USER}@${HOST}:~/ || (ssh -o StrictHostKeyChecking=no ${USER}@${HOST} \
"which scp || (ls -l /etc/redhat-release && yum install -y openssh-clients);" && \
scp grow-root-partI.sh grow-root-partII.sh ${USER}@${HOST}:~/)

ssh -o StrictHostKeyChecking=no ${USER}@${HOST} "/bin/bash ~/grow-root-partI.sh && /bin/rm ~/grow-root-partI.sh && reboot" && echo -e "\n\n PART I .... OK!"

sleep 30

#ping ${HOST} -c 2  &>/dev/null || (echo "#1: no ping :("; sleep 10)
#ping ${HOST} -c 2  &>/dev/null || (echo "#2: no ping :("; sleep 10)
#ping ${HOST} -c 2  &>/dev/null || (echo "#3: no ping :("; sleep 10)
#ping ${HOST} -c 2  &>/dev/null || (echo "#4: no ping :("; sleep 20)
#ping ${HOST} -c 2  &>/dev/null || (echo "#5: no ping :("; sleep 20)
#ping ${HOST} -c 2  &>/dev/null || (echo "#6: no ping..... The Server has DIED!";)


for t in $(seq 10)
do
  ping ${HOST} -c 2 &>/dev/null
  if [ $? -eq 0 ];then echo -e "\n Server ["${HOST}"] is alive, exit";break; else echo $t" - Server is not available"; sleep 10; fi
done

for t in $(seq 7)
do
  echo "Try ssh connect to" ${USER}@${HOST}
  ssh -o StrictHostKeyChecking=no ${USER}@${HOST} "if [[ -f ~/grow-root-partII.sh ]];then /bin/bash ~/grow-root-partII.sh&&/bin/rm ~/grow-root-partII.sh&&reboot;else echo 'No file ~/grow-root-partII.sh';fi" && echo -e "\n\n PART II .... OK!"
  if [ $? -eq 0 ];then echo  -e "\n loop exit!"; break; else sleep 10; fi
done

for t in $(seq 10)
do
  ping ${HOST} -c 2 &>/dev/null
  if [ $? -eq 0 ];then echo -e "\n Server ["${HOST}"] is alive, exit";break; else echo $t" - Server is not available"; sleep 10; fi 
done

#ping ${HOST} -c 2 &>/dev/null || sleep 10
#ping ${HOST} -c 2 &>/dev/null || sleep 20
#ping ${HOST} -c 2 &>/dev/null || sleep 30
#ping ${HOST} -c 2 &>/dev/null || sleep 40
#ping ${HOST} -c 2 || echo -e '\n\n ERROR!!! The Server has DIED! =('
