DEV=`pvs|awk '{print $1}'|grep dev|head -1`
if [[ `df -hT /|grep xfs` ]];
then 
 pvresize ${DEV} && lvresize -l +100%FREE `mount | grep \/\ |awk '{print $1}'` && xfs_growfs `mount | grep \/\ |awk '{print $1}'`;
else
 pvresize ${DEV} && lvresize -l +100%FREE `mount | grep \/\ |awk '{print $1}'` && resize2fs `mount | grep \/\ |awk '{print $1}'`
fi

echo -e "\n"
df -h /
echo -e "\n"
