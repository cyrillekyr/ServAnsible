#! /bin/sh


ls /home | while read result
do
	usermod -s /bin/bash $result
	echo " Done for user $result "
done
