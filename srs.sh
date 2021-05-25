!/bin/bash
input="vm_list.txt"
while IFS= read -r line
do
   vmname=`echo $line | awk '{print $1}'` 
   vm_cpu=`echo $line | awk '{print $2}'`
   vm_mem=`echo $line | awk '{print $3}'`
   vm_hdd=`echo $line | awk '{print $4}'`
   storage=`echo $line | awk '{print $6}'`
   echo yes | ./run.py --datastor $storage  -D --net 172.24.5.0/24 --name $vmname --ram $vm_mem --cpu $vm_cpu --hdd $vm_hdd --template template_centos7.5 --exp 23.04.2022 --desc VKryukov@phoenixit.ru --folder BI/BI_INO_N_OTKR_CVM
done < "$input"



