#!/bin/bash

# script to generate all numbers for a font

CHARACTERS=( 0 1 2 3 4 5 6 7 8 9 : )
FONT=$1
SIZE=$2
OUTDIR="`pwd`/fonts/$FONT"

mkdir -p $OUTDIR

for char in "${CHARACTERS[@]}"; do
  if [ "$char" == ":" ]; then
    name="colon"
  else
    name="$char"
  fi

  set -x

  convert \
  -background white \
  -fill black \
  -size $SIZE \
  -font $FONT \
  +antialias \
  label:"$char" \
  "$OUTDIR/$name.bmp"

  set +x
done

echo "wrote images to $OUTDIR"