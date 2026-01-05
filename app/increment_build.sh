#!/bin/bash
# Script to automatically increment build number in pubspec.yaml

PUBSPEC_FILE="pubspec.yaml"

# Check if pubspec.yaml exists
if [ ! -f "$PUBSPEC_FILE" ]; then
    echo "Error: pubspec.yaml not found!"
    exit 1
fi

# Extract current version line
VERSION_LINE=$(grep "^version:" "$PUBSPEC_FILE")

if [ -z "$VERSION_LINE" ]; then
    echo "Error: Could not find version in pubspec.yaml"
    exit 1
fi

# Extract version number and build number (format: x.y.z+build)
CURRENT_VERSION=$(echo "$VERSION_LINE" | sed 's/version: //' | sed 's/ //g')

# Split into version and build number
if [[ $CURRENT_VERSION == *"+"* ]]; then
    VERSION_NUMBER=$(echo "$CURRENT_VERSION" | cut -d'+' -f1)
    BUILD_NUMBER=$(echo "$CURRENT_VERSION" | cut -d'+' -f2)
else
    VERSION_NUMBER=$CURRENT_VERSION
    BUILD_NUMBER=0
fi

# Increment build number
NEW_BUILD_NUMBER=$((BUILD_NUMBER + 1))
NEW_VERSION="${VERSION_NUMBER}+${NEW_BUILD_NUMBER}"

# Update pubspec.yaml
sed -i "s/^version: .*/version: $NEW_VERSION/" "$PUBSPEC_FILE"

echo "Build number incremented: $CURRENT_VERSION -> $NEW_VERSION"
echo "New build number: $NEW_BUILD_NUMBER"
