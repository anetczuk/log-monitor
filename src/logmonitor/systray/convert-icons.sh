#!/bin/bash

set -eu

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")


for in_file in "$SCRIPT_DIR"/*.png; do
	if [[ $in_file == *"-w.png"* ]]; then
		continue
	fi
	out_file="${in_file%.png}-w.png"
	echo "converting $in_file to $out_file"
	convert "$in_file" -negate "$out_file"
	convert -resize 512x512! "$out_file" "$out_file"

	convert -strip "$out_file" "$out_file"
done


echo "done"
