#!/bin/bash
# Build Flutter app with automatic build number increment

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "Flutter App Build with Auto-Increment"
echo "========================================"
echo ""

# Increment build number
echo "Step 1: Incrementing build number..."
bash "$SCRIPT_DIR/increment_build.sh"

if [ $? -ne 0 ]; then
    echo "Error: Failed to increment build number"
    exit 1
fi

echo ""
echo "Step 2: Getting Flutter dependencies..."
flutter pub get

if [ $? -ne 0 ]; then
    echo "Error: Failed to get Flutter dependencies"
    exit 1
fi

echo ""
echo "Step 3: Building Flutter app..."

# Check for build target argument
TARGET="${1:-apk}"

case $TARGET in
    apk)
        echo "Building APK..."
        flutter build apk
        ;;
    appbundle)
        echo "Building App Bundle..."
        flutter build appbundle
        ;;
    debug)
        echo "Building debug APK..."
        flutter build apk --debug
        ;;
    *)
        echo "Building $TARGET..."
        flutter build $TARGET
        ;;
esac

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "Build completed successfully!"
    echo "========================================"
else
    echo ""
    echo "Build failed!"
    exit 1
fi
