#! /bin/bash


ls /home | while read result
do
	cp .bashrc /home/$result/.bashrc
	echo " Done for user $result "
done
cp .bashrc /root/.bashrc
echo "Done root"
