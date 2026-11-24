#!/bin/sh
# usage: sh encode.sh OUTPUT.mp4 N_SCENES  -> concat scene_XX.mp4 + mix.wav, 2-pass ~5.4 Mbps (<50 MB for ~70 s)
OUT=$1; N=$2; rm -f list.txt ffmpeg2pass*
i=0; while [ $i -lt $N ]; do printf "file 'scene_%02d.mp4'\n" $i >> list.txt; i=$((i+1)); done
ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt -c copy video.mp4
ffmpeg -y -loglevel error -i video.mp4 -c:v libx264 -preset medium -b:v 5400k -pass 1 -an -f null /dev/null
ffmpeg -y -loglevel error -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset medium -b:v 5400k -maxrate 8000k -bufsize 12000k -pass 2 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height -of compact "$OUT"
