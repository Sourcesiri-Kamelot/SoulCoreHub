#!/bin/bash

# SoulCoreHub Image Optimization Script
# This script optimizes images for web performance

echo "SoulCoreHub Image Optimization"
echo "============================="

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null; then
    echo "ImageMagick is not installed. Installing..."
    brew install imagemagick
fi

# Directory containing images
IMAGE_DIR="/Users/helo.im.ai/SoulCoreHub/public/images"

# Create a backup directory
BACKUP_DIR="${IMAGE_DIR}/originals"
mkdir -p "$BACKUP_DIR"

# Process PNG files
echo "Optimizing PNG files..."
for file in "$IMAGE_DIR"/*.png; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "Processing: $filename"
        
        # Create backup
        cp "$file" "$BACKUP_DIR/$filename.bak"
        
        # Optimize PNG
        convert "$file" -strip -quality 85 "$file"
    fi
done

# Process JPG files
echo "Optimizing JPG files..."
for file in "$IMAGE_DIR"/*.{jpg,jpeg}; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "Processing: $filename"
        
        # Create backup
        cp "$file" "$BACKUP_DIR/$filename.bak"
        
        # Optimize JPG
        convert "$file" -strip -quality 85 "$file"
    fi
done

# Generate favicon from logo
echo "Generating favicon.ico..."
if [ -f "$IMAGE_DIR/soulcorehub-logo.png" ]; then
    convert "$IMAGE_DIR/soulcorehub-logo.png" -background transparent -resize 32x32 "$IMAGE_DIR/../favicon.ico"
    echo "Favicon created at /public/favicon.ico"
fi

echo "Image optimization complete!"
echo "Original files backed up to: $BACKUP_DIR"
