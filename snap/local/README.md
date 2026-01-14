# Building the Context Timer Snap

This directory contains the files necessary to build a snap package for Context Timer.

> **Note**: This README is located in `snap/local/` because snapcraft requires that only snapcraft-specific files exist in the `snap/` directory. The `snap/local/` directory is ignored by snapcraft and can contain additional documentation and files.

## Prerequisites

### Required

Install snapcraft:
```bash
sudo snap install snapcraft --classic
```

### Optional (but recommended)

For clean, isolated builds, install one of the following:

**Option 1: Multipass** (recommended for most users)
```bash
sudo snap install multipass
```

**Option 2: LXD** (alternative to Multipass)
```bash
sudo snap install lxd
sudo lxd init --auto
```

**Note**: The `build-snap.sh` script will automatically detect and use Multipass or LXD if available. If Multipass is installed, snapcraft will use it automatically without any additional flags. LXD requires the `--use-lxd` flag. Direct builds without either may leave build artifacts in your project directory.

## Building the Snap

### Method 1: Using the build script (recommended)

From the root of the project:

```bash
./build-snap.sh
```

This script will automatically detect and use:
- **Multipass** (if installed) - preferred, clean isolated environment
- **LXD** (if installed and Multipass is not) - alternative clean environment  
- **Direct build** (fallback) - builds on your host system

To clean previous builds before building:
```bash
./build-snap.sh clean
```

### Method 2: Using snapcraft directly

Basic build (uses Multipass automatically if installed):
```bash
snapcraft
```

This will create a `.snap` file in the current directory (e.g., `context-timer_0.1.0_amd64.snap`).

Building with LXD (if you have LXD but not Multipass):
```bash
snapcraft --use-lxd
```

### Building for multiple architectures

To build for arm64:
```bash
snapcraft --target-arch=arm64
```

## Installing the Snap Locally

After building:

```bash
sudo snap install context-timer_0.1.0_amd64.snap --dangerous
```

The `--dangerous` flag is needed for locally-built snaps that aren't signed by the Snap Store.

## Testing the Snap

Run the application:
```bash
snap run context-timer
```

Or simply:
```bash
context-timer
```

## Publishing to the Snap Store

1. Create an account on https://snapcraft.io/

2. Login with snapcraft:
   ```bash
   snapcraft login
   ```

3. Register the snap name:
   ```bash
   snapcraft register context-timer
   ```

4. Upload and release:
   ```bash
   snapcraft upload context-timer_0.1.0_amd64.snap --release=stable
   ```

## Snap Configuration

The snap uses:
- **Base**: core22 (Ubuntu 22.04 LTS base)
- **Confinement**: strict (fully confined for security)
- **Extensions**: gnome (provides Qt6 and desktop integration)
- **Plugs**: 
  - home (access to user's home directory)
  - desktop/wayland/x11 (GUI display)
  
## Data Location

When installed as a snap, the application stores data in:
```
~/snap/context-timer/current/.local/share/context-timer/
```

## Troubleshooting

### Build hangs or prompts for LXD installation

If `build-snap.sh` hangs or prompts to install LXD when you have Multipass installed:
- Make sure Multipass is running: `multipass version`
- The script should automatically detect and use Multipass
- If issues persist, try building directly with `snapcraft` which auto-detects Multipass

### Non-snapcraft files in snap/ directory warning

If you see warnings about non-snapcraft files in the `snap/` directory, ensure all documentation and extra files are in `snap/local/` (which is ignored by snapcraft).

### Qt platform plugin not found

If you see errors about missing Qt platform plugins, ensure you're using the GNOME extension which provides Qt6 support.

### Permission denied errors

The snap is strictly confined. If you need access to additional directories, use:
```bash
snap connect context-timer:home
```

### Checking logs

View snap logs:
```bash
snap logs context-timer
```

View application output:
```bash
snap run context-timer
```
