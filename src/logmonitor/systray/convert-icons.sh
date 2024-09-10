#!/bin/bash

set -eu

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


for in_file in "$SCRIPT_DIR"/*.png; do
	if [[ $in_file == *"-w.png"* ]]; then
		continue
	fi

	out_file="${in_file%.png}-w.png"
	echo "converting $in_file to $out_file"

	# change black to white
	convert "$in_file" -negate "$out_file"

	in_file="$out_file"

	# extend and centerize image 
	convert \
	   "$in_file" \
	   -append \
	   -background transparent \
	   -gravity Center \
	   -extent 512x \
	   "$out_file"

	## stretch image
	#convert -resize 512x512! "$in_file" "$out_file"

	# remove metadata
	convert -strip "$in_file" "$out_file"
done


## paint circles with colors
IMG_PATH="$SCRIPT_DIR/task-checkmark-icon-w.png"
convert "$IMG_PATH" -fuzz 5% -fill green2 -draw 'color 350,350 floodfill' "$IMG_PATH"

IMG_PATH="$SCRIPT_DIR/task-remove-icon-w.png"
convert "$IMG_PATH" -fuzz 5% -fill tomato -draw 'color 350,350 floodfill' "$IMG_PATH"

IMG_PATH="$SCRIPT_DIR/task-error-icon-w.png"
convert "$IMG_PATH" -fuzz 5% -fill yellow -draw 'color 350,350 floodfill' "$IMG_PATH"

IMG_PATH="$SCRIPT_DIR/task-sync-icon-w.png"
convert "$IMG_PATH" -fuzz 5% -fill DodgerBlue -draw 'color 350,350 floodfill' "$IMG_PATH"


echo "done"
