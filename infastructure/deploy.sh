#!/bin/bash

# Check if render-cli is installed
if ! command -v render &> /dev/null; then
    echo "Installing Render CLI..."
    curl -o render https://render.com/download/cli/linux/latest
    chmod +x render
    sudo mv render /usr/local/bin/
fi

# Login to Render
echo "Logging in to Render..."
render login

# Deploy to Render
echo "Deploying to Render..."
render deploy 