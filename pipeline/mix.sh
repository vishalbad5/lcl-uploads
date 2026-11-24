#!/bin/sh
# usage: sh mix.sh  (needs voice_raw.wav + music.wav in cwd) -> mix.wav at -14 LUFS
ffmpeg -y -loglevel error -i voice_raw.wav -i music.wav -filter_complex "\
[0:a]aresample=48000,highpass=f=65,equalizer=f=180:t=q:w=1:g=1.0,equalizer=f=3100:t=q:w=1.2:g=1.8,acompressor=threshold=-21dB:ratio=2.8:attack=8:release=130:makeup=2.5,aecho=0.88:0.55:36|60:0.15|0.08,pan=stereo|c0=c0|c1=c0,asplit=2[v][sc];\
[1:a]volume=0.55[m];[m][sc]sidechaincompress=threshold=0.04:ratio=5:attack=20:release=350[md];\
[v][md]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.2:LRA=9" -ar 48000 -c:a pcm_s16le mix.wav
