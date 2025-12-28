#!/bin/bash
# Android SDK setup script for Flutter

echo "Setting up Android SDK for Flutter..."

# Create Android directory
mkdir -p ~/Android/cmdline-tools
cd ~/Android/cmdline-tools

# Download command line tools
echo "Downloading Android command line tools..."
wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip

# Extract
echo "Extracting..."
unzip -q commandlinetools-linux-11076708_latest.zip
mv cmdline-tools latest
rm commandlinetools-linux-11076708_latest.zip

# Set up SDK directory
export ANDROID_HOME=$HOME/Android/Sdk
mkdir -p $ANDROID_HOME

# Install required components
echo "Installing SDK components (this may take a while)..."
cd ~/Android/cmdline-tools/latest/bin
./sdkmanager --sdk_root=$ANDROID_HOME "platform-tools" "platforms;android-34" "build-tools;34.0.0"

# Accept licenses
echo "Accepting licenses..."
yes | ./sdkmanager --sdk_root=$ANDROID_HOME --licenses

# Add to bashrc
echo ""
echo "Adding environment variables to ~/.bashrc..."
if ! grep -q "ANDROID_HOME" ~/.bashrc; then
    echo 'export ANDROID_HOME=$HOME/Android/Sdk' >> ~/.bashrc
    echo 'export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin' >> ~/.bashrc
    echo 'export PATH=$PATH:$ANDROID_HOME/platform-tools' >> ~/.bashrc
fi

echo ""
echo "✅ Android SDK setup complete!"
echo ""
echo "Run: source ~/.bashrc"
echo "Then: flutter doctor"
echo "Then: flutter build apk --debug"
