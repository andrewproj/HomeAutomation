for f in *.mid; do 
    fluidsynth -T wav -F "$(basename -- "$f" .mid).wav" /usr/share/sounds/sf2/FluidR3_GM.sf2 "$f"
done
