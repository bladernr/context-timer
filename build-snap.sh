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

# Clean previous builds (optional)
if [ "$1" = "clean" ]; then
    echo "Cleaning previous builds..."
    snapcraft clean
    rm -f *.snap
    echo "Clean complete!"
    echo ""
fi

# Build the snap
echo "Building snap..."
if command -v multipass &> /dev/null || command -v lxd &> /dev/null; then
    # Use clean build environment if available
    snapcraft --use-lxd 2>/dev/null || snapcraft
else
    # Build directly
    snapcraft
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
