#!/bin/bash

# Variable setting
USAGE="./install.sh [-h] [-v] [-b boot_script] [-s service_description] [-p service_path]"

PYTHON_MODULE=$(basename $PWD)
SERVICE_DESCRIPTION="pvpc_bot.service"
SERVICE_PATH="/etc/systemd/system/"

ROOT_ACCESS="false"

# Parameter parsing
while getopts "hvb:s:p:" arg; do
	case $arg in
		h)
			echo $USAGE
			;;
		b)
			BOOT_SCRIPT=${OPTARG}
			;;
		s)
			SERVICE_DESCRIPTION=${OPTARG}
			;;
		p)	
			SERVICE_PATH=${OPTARG}
			;;
		v)
			set -x
			;;
		*) 
			echo $USAGE
			exit -1
			;;
	esac
done


# Functions
create_service_file(){
	service_file="$SERVICE_PATH/$SERVICE_DESCRIPTION"
	if [ "$ROOT_ACCESS" != "true" ]; then
		echo "Root acces not granted: the service file $service_file could not be created"
    else
		echo "Root acces granted, creating service file in $service_file"
		sudo su -c "echo '[Unit]' > $service_file"
	    sudo su -c "echo 'After=network.service' >> $service_file"
		sudo su -c "echo '' >> $service_file"
		sudo su -c "echo '[Service]' >> $service_file"
		sudo su -c "echo 'User='$USER >> $service_file"
		sudo su -c "echo 'WorkingDirectory='$(realpath $PWD/..) >> $service_file"
		sudo su -c "echo 'ExecStart=/bin/python3 -m '$PYTHON_MODULE '>>' $PWD'/data/logs/supra_logs.log' >> $service_file"
		sudo su -c "echo '' >> $service_file"
		sudo su -c "echo '[Install]' >> $service_file"
		sudo su -c "echo 'WantedBy=multi-user.target' >> $service_file"
		sudo su -c "echo '' >> $service_file"
		sudo su -c "chmod 644 $service_file"
		sudo systemctl daemon-reload
		sudo systemctl enable $SERVICE_DESCRIPTION
		sudo systemctl start $SERVICE_DESCRIPTION
	fi
}

request_root(){
	echo -n "Install the bot as a service? (You will be asked to grant root access) [Yn] "
	read selected_option
	if [ "$selected_option" != "n" ]; then
		sudo su -c "echo granted" >/dev/null
		ROOT_ACCESS="true"
	fi
}


setup_bot(){
	sed -i -e "s@^HOME = \".*\"@HOME = \"$PWD\"@g" config.py
	echo -n "Do you want to configure the bot now? [Yn] "
	read selected_option
	if [ "$selected_option" != "n" ]; then
		echo "You must set up an API_TOKEN and a BOT_TOKEN for the bot to work, edit the rest as you whish ;)"
		${EDITOR:-vi} config.py
	else
		echo "You must set up an API_TOKEN and a BOT_TOKEN for the bot to work!"
		echo "Do it in the config.py file ;)"
	fi
}


# Main script
echo "Installing python dependencies..."
python3 -m pip install -r ./requirements.txt --user

# Root instalation
request_root
create_service_file

# Bot setup
setup_bot
