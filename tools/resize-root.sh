#!/bin/sh
set -e
echo 1 > /sys/block/sda/device/rescan

MOUNT_LINE=$(cat /etc/mtab | grep ' / ' | grep -v '^rootfs')
DEVICE=$(echo "$MOUNT_LINE" | cut -d' ' -f1)
FSTYPE=$(echo "$MOUNT_LINE" | cut -d' ' -f3)
GROWPART=$(which growpart)

if [ $? -ne 0 ]; then
  echo "growpart command is missing"
  exit 1
fi

if [ $(df | grep ' /$' | wc -l) -eq 0 ]; then
  DEVICE=$(readlink -f "$DEVICE")
  DISK=$(echo "$DEVICE" | sed 's/.$//')
  PARTITION=$(echo "$DEVICE" | sed "s|^$DISK||")
  LVM="no"
fi

echo $LVM

if [ "${LVM}" != "no" ]; then
  if [ -f /etc/debian_version ]; then
    DEVICE=$(mount | grep ' / ' | grep -v '^rootfs'|cut -d' ' -f1)
  fi
  PVRESIZE=$(which pvresize)
  LVEXTEND=$(which lvextend)
  DISK=$(pvdisplay |grep "PV Name"|awk '{print $3}'|sed 's/.$//')
  PARTITION=$(pvdisplay |grep "PV Name"|awk '{print $3}'| sed "s|^${DISK}||")
  PV=$(pvdisplay |grep "PV Name"|awk '{print $3}')
  LV=$(lvdisplay ${DEVICE} |grep "LV Path"|awk '{print $3}')


  TABLE=$(parted ${DISK} print 2>/dev/null | grep 'Partition Table:' | awk '{print $3}')
  if [ "${TABLE}" = 'msdos' ] && [ ${PARTITION} -gt 4 ]; then
    PARTITION="$(parted ${DISK} print | grep 'extended' | awk '{print $1}') $PARTITION"
  fi
fi

echo DEVICE: ${DEVICE}
echo FSTYPE: ${FSTYPE}
echo DISK: ${DISK}
echo PARTITION: ${PARTITION}


(
  for PART in ${PARTITION}; do
    ${GROWPART} ${DISK} ${PART}
  done

  if [ "${LVM}" != "no" ]; then
    ${PVRESIZE} ${PV}
    ${LVEXTEND} -l +100%FREE ${LV}
  fi
) || : 

case "${FSTYPE}" in
  ext2|ext3|ext4)
    resize2fs ${DEVICE}
    ;;
  xfs)
    xfs_growfs /
    ;;
  btrfs)
    btrfs filesystem resize max /
    ;;
esac

df -h /
