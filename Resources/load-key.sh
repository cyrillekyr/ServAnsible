#! /bin/bash


ls /home | while read result
do
	mkdir /home/$result/.ssh
	chown $result:$result /home/$result/.ssh
	cat ssham-key >>/home/$result/.ssh/authorized_keys
	chown $result:$result /home/$result/.ssh/authorized_keys
	echo " Done for user $result "
done
cat ssham-key >>/root/.ssh/authorized_keys
echo "Done root"
