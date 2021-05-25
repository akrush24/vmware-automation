!/bin/bash
input="ip.txt"
while IFS= read -r line
do
   ip=`echo $line | awk '{print $1}'` 
   ssh root@$ip 'bash -s' < tools/resize-root.sh   
done < "$input"



