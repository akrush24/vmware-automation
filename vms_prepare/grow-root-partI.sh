echo -e "\n++++ STAR ++++"
fdisk -l /dev/sda

START_SEC=`fdisk -lc /dev/sda|awk '{if($1 == "/dev/sda2"){print $2}}'`

if [[ -z `fdisk -l /dev/sda|grep sda2|grep Extended` ]]
then

fdisk /dev/sda <<EOF!
d
2
n
p
2
${START_SEC}

w
q
EOF!

else

fdisk /dev/sda <<EOF!
d
5
d
2
n
e
2


n
l


w
q
EOF!

fi

echo -e "\n---- FINISH -----\n"
fdisk -l /dev/sda
echo -e "\n"
