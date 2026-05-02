#!/bin/bash
# Food Waste Collection and Recycling for Gaza Food Security
# Collects food waste from hotels, restaurants, markets
# Converts to animal feed OR compost

WORKSPACE="/root/.openclaw/workspace/gaza-food-security"
WASTE_SOURCES="$WORKSPACE/4_recycling/waste_sources"
PROCESSED_OUTPUT="$WORKSPACE/4_recycling/processed"
LOG_FILE="$WORKSPACE/4_recycling/collection.log"

# Create dirs if not exist
mkdir -p "$WASTE_SOURCES" "$PROCESSED_OUTPUT/compost" "$PROCESSED_OUTPUT/animal_feed"

echo "starting food waste collection at $(date)" >> "$LOG_FILE"

# Process each waste bin
for bin in $(ls "$WASTE_SOURCES"/); do
  BIN_PATH="$WASTE_SOURCES/$bin"
  BIN_INFO="$BIN_PATH/info.json"
  
  if [ ! -f "$BIN_INFO" ]; then
    echo "⚠️ No info for $bin, skipping"
    continue
  fi
  
  # Read bin metadata
  SOURCE_TYPE=$(jq -r '.type' "$BIN_INFO")
  CONTACT=$(jq -r '.contact' "$BIN_INFO)
  LOCATION=$(jq -r '.location' "$BIN_INFO")
  
  echo "Collecting from $bin ($SOURCE_TYPE at $LOCATION)" >> "$LOG_FILE"
  
  # Check if bin has enough waste (>5kg)
  WASTE_WEIGHT=$(du -sh "$BIN_PATH" 2>/dev/null | cut -f1 | sed 's/K/*1024/; s/M/*1048576/; s/G/*1073741824/; s/:.*//')
  if [ "$WASTE_WEIGHT" -lt 5 ]; then
    echo "  — Insufficient waste (<5kg), skip"
    continue
  fi
  
  # Process based on type
  if [ "$SOURCE_TYPE" = "organic_kitchen" ]; then
    # Convert to animal feed (for chickens/goats)
    echo "  → Converting to animal feed"
    ./process_organic_for_feed.sh "$BIN_PATH" "$PROCESSED_OUTPUT/animal_feed/$(date +%Y%m%d)_$bin"
  elif [ "$SOURCE_TYPE" = "garden_waste" ]; then
    # Convert to compost
    echo "  → Converting to compost"
    ./process_garden_compost.sh "$BIN_PATH" "$PROCESSED_OUTPUT/compost/$(date +%Y%m%d)_$bin"
  else
    echo "  → Unknown type, skip"
    continue
  fi
  
  # Log collection
  echo "$(date '+%Y-%m-%d %H:%M:%S') COLLECTED $bin $WASTE_WEIGHT kg $SOURCE_TYPE $LOCATION" >> "$LOG_FILE"
  
  # Empty bin (keep structure)
  rm -rf "$BIN_PATH"/*
  touch "$BIN_PATH"/.keep
done

echo "collection complete at $(date)" >> "$LOG_FILE"
