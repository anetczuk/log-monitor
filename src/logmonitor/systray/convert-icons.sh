#!/bin/bash

set -eu

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")



convert_image() {
	local input_file="$1"
	local output_file="$1"

	# extend and centerize image 
	convert \
	   "$input_file" \
	   -append \
	   -background transparent \
	   -gravity Center \
	   -extent 512x \
	   "$output_file"

	## stretch image
	#convert -resize 512x512! "$input_file" "$output_file"

	# remove metadata
	convert -strip "$input_file" "$output_file"
}


## paint circles with colors
paint_images() {
	local suffix="$1"

	IMG_PATH="$SCRIPT_DIR/task-checkmark-icon-$suffix.png"
	convert "$IMG_PATH" -fuzz 95% -fill green2 -draw 'color 350,350 floodfill' "$IMG_PATH"
	
	IMG_PATH="$SCRIPT_DIR/task-remove-icon-$suffix.png"
	convert "$IMG_PATH" -fuzz 95% -fill tomato -draw 'color 350,350 floodfill' "$IMG_PATH"
	
	IMG_PATH="$SCRIPT_DIR/task-error-icon-$suffix.png"
	convert "$IMG_PATH" -fuzz 95% -fill yellow -draw 'color 350,350 floodfill' "$IMG_PATH"
	
	IMG_PATH="$SCRIPT_DIR/task-sync-icon-$suffix.png"
	convert "$IMG_PATH" -fuzz 95% -fill DodgerBlue -draw 'color 350,350 floodfill' "$IMG_PATH"
}


# =========================================


# prepare white theme
for in_file in "$SCRIPT_DIR"/*.png; do
	if [[ $in_file == *"-w.png"* ]]; then
		continue
	fi
	if [[ $in_file == *"-b.png"* ]]; then
		continue
	fi

	out_file="${in_file%.png}-w.png"
	echo "converting $in_file to $out_file"
	
	cp -a "$in_file" "$out_file"

	# change black to white
	convert "$out_file" -negate "$out_file"

	convert_image "$out_file" "$out_file"

	# touch -r "$in_file" "$out_file"
done

paint_images "w"


# prepare black theme
for in_file in "$SCRIPT_DIR"/*.png; do
	if [[ $in_file == *"-w.png"* ]]; then
		continue
	fi
	if [[ $in_file == *"-b.png"* ]]; then
		continue
	fi

	out_file="${in_file%.png}-b.png"
	echo "converting $in_file to $out_file"
	
	cp -a "$in_file" "$out_file"

	convert_image "$out_file" "$out_file"

	# touch -r "$in_file" "$out_file"
done

paint_images "b"


echo "done"
