#!/bin/bash

# Build and run the Tauri dashboard application

echo "Building and running Coda Dashboard..."

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  npm install
fi

# Run the development server
echo "Starting development server..."
npm run tauri dev
