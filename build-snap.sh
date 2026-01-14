#!/bin/bash
# Build script for Context Timer snap package

set -e

usage() {
    cat << EOF
Usage: $(basename "$0") [COMMAND]

Build a snap package for Context Timer.

Commands:
    (none)          Build the snap package (default action)
    clean           Remove all snap build artifacts and reset repository
    -h, --help      Display this help message

Examples:
    $(basename "$0")            # Build the snap
    $(basename "$0") clean      # Clean all build artifacts

The build process will automatically detect and use:
  - Multipass (preferred) for isolated clean builds
  - LXD (alternative) if Multipass is not available
  - Direct build as fallback

See snap/local/README.md for more detailed information.
EOF
    exit 0
}

# Parse arguments
case "${1:-}" in
    -h|--help)
        usage
        ;;
    clean)
        # Clean command handled below
        ;;
    "")
        # No argument - build (default)
        ;;
    *)
        echo "ERROR: Unknown argument: $1"
        echo ""
        usage
        ;;
esac

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
