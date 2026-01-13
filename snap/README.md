# Building the Context Timer Snap

This directory contains the files necessary to build a snap package for Context Timer.

## Prerequisites

Install snapcraft:
```bash
sudo snap install snapcraft --classic
```

If building on a non-Linux system or you want a clean build environment, also install LXD:
```bash
sudo snap install lxd
sudo lxd init --auto
```

## Building the Snap

From the root of the project:

```bash
snapcraft
```

This will create a `.snap` file in the current directory (e.g., `context-timer_0.1.0_amd64.snap`).

### Building with LXD (recommended for clean builds)

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
