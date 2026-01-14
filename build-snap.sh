#!/bin/bash
# Build script for Context Timer snap package

set -e

echo "Building Context Timer snap package..."
echo "========================================"
echo ""

# Check if snapcraft is installed
if ! command -v snapcraft &> /dev/null; then
    echo "ERROR: snapcraft is not installed"
    echo "Install it with: sudo snap install snapcraft --classic"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "snap/snapcraft.yaml" ]; then
    echo "ERROR: snap/snapcraft.yaml not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Clean all build artifacts
if [ "$1" = "clean" ]; then
    echo "Cleaning all snap build artifacts..."
    
    # Clean snapcraft build directories
    if [ -d "parts" ]; then
        echo "  Removing parts/..."
        rm -rf parts/
    fi
    if [ -d "prime" ]; then
        echo "  Removing prime/..."
        rm -rf prime/
    fi
    if [ -d "stage" ]; then
        echo "  Removing stage/..."
        rm -rf stage/
    fi
    
    # Remove snap packages
    if ls *.snap 1> /dev/null 2>&1; then
        echo "  Removing *.snap files..."
        rm -f *.snap
    fi
    
    # Clean snapcraft cache
    snapcraft clean
    
    echo "Clean complete! Repository reset to pre-build state."
    echo ""
    exit 0
fi

# Build the snap
echo "Building snap..."
if command -v multipass &> /dev/null; then
    # Multipass is installed - snapcraft will use it automatically
    echo "Using Multipass for clean build environment..."
    snapcraft pack
elif command -v lxd &> /dev/null; then
    # LXD is available but not Multipass
    echo "Using LXD for clean build environment..."
    snapcraft pack --use-lxd
else
    # Build directly on host system
    echo "Building directly (no Multipass/LXD found)..."
    snapcraft pack
fi

echo ""
echo "========================================"
echo "Build complete!"
echo ""

# List the generated snap file
SNAP_FILE=$(ls -t *.snap 2>/dev/null | head -1)
if [ -n "$SNAP_FILE" ]; then
    echo "Snap package: $SNAP_FILE"
    echo ""
    echo "To install locally:"
    echo "  sudo snap install $SNAP_FILE --dangerous"
    echo ""
    echo "To upload to the store:"
    echo "  snapcraft login"
    echo "  snapcraft upload $SNAP_FILE --release=stable"
else
    echo "Warning: No .snap file found"
fi
