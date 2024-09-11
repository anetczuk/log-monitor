#!/bin/bash

set -eu

## works both under bash and sh
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


EXEC_PATH="$SCRIPT_DIR/logmonitor/main.py start"
CONFIG_PATH=""

ARGS=()

while :; do
    if [ -z "${1+x}" ]; then
        ## end of arguments (prevents unbound argument error)
        break
    fi

    case "$1" in
      --exeprefix)      ## add prefix program
                        EXEC_PATH="$2 $EXEC_PATH"
                        shift; shift ;;
      --config)         ## config file
                        CONFIG_PATH=$(realpath "$2")
                        shift; shift ;;
      *)  ARGS+=($1)
          shift ;;
    esac
done


## add udev rule
AUTOSTART_DIR=~/.config/autostart
AUTOSTART_FILE=$AUTOSTART_DIR/log-monitor.desktop

mkdir -p $AUTOSTART_DIR

if [ "$CONFIG_PATH" != "" ]; then
    EXEC_PATH="$EXEC_PATH -c $CONFIG_PATH"
else
    echo "missing --config param"
    echo "please provide yaml config path"
    exit 1
fi


cat > $AUTOSTART_FILE << EOL
[Desktop Entry]
Name=Log Monitor
GenericName=Log Monitor
Comment=Parse log files and expose data in form of RSS feed.
Type=Application
Categories=Office;
Exec=$EXEC_PATH
Icon=$SCRIPT_DIR/logmonitor/systray/task-checkmark-icon.png
Terminal=false
StartupNotify=true
X-GNOME-Autostart-enabled=true
EOL


echo "File created in: $AUTOSTART_FILE"
