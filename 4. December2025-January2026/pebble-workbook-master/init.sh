#!/bin/bash

# Exit on any error
set -e

echo "🚀 Initializing workspace..."

# Make all shell scripts executable
find . -type f -name "*.sh" -exec chmod +x {} \;
echo "✅ Shell scripts are now executable"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Build all Docker containers in docker/ directory
echo "🐳 Building Docker containers..."
for dockerfile in docker/*/Dockerfile; do
    if [ -f "$dockerfile" ]; then
        container_name=$(basename $(dirname "$dockerfile"))
        echo "Building $container_name..."
        docker build -t "coding-workspace-$container_name" -f "$dockerfile" docker/$container_name
        
        # Verify the build was successful
        if [ $? -ne 0 ]; then
            echo "❌ Failed to build $container_name container"
            exit 1
        fi
    fi
done

echo "✅ Setup complete! Your workspace is ready." 