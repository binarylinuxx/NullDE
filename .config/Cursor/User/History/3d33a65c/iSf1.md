# HYPRSETTINGS
A simple control panel designed for Hyprland. This project was originally for my own dotfiles but is open for everyone to use in their projects.

## Quick Start

```sh
git clone https://github.com/binarylinuxx/hyprsettings.git
cd hyprsettings
make prepare
sudo make install
```

Or, for Arch-based systems:
```sh
makepkg -si
```

Or, use the install script (Void, Fedora, Arch):
```sh
chmod +x install.sh && ./install.sh
```

Or, manual Python install:
```sh
python setup.py build
sudo python setup.py install
```

## Overview
This program helps manage screen light, wallpaper, audio, and provides system information.

## Dependencies
- Python 3.11+
- PyGObject (python-gobject)
- GTK4
- Libadwaita theme (or modify source for your preferred GTK theme)
- [matugen](https://github.com/InioX/matugen) (for color generation)
- [swaybg](https://github.com/swaywm/swaybg) (wallpaper backend)
- [pamixer](https://github.com/cdemoulins/pamixer) (audio control)

## Features
- Change wallpaper and generate color scheme
- Screen light presets (Default, Night Light, Candlelight, etc.)
- Manual gamma and temperature controls
- Audio volume and mute controls
- System information (OS, CPU, RAM, disk, GPU, WM)

## Screenshots

**Desktop:**
![Desktop](img/desk_layout.png)

**Screen:**
![Screen](img/screen_layout.png)

**Audio:**
![Audio](img/audiomixer_layout.png)

**Sysinfo:**
![Sysinfo](img/sysinfo_layout.png)

## Layouts Overview
- **Desk:** Change wallpaper, generate scheme with Matugen, backend Swaybg.
- **Screen:** Choose presets, adjust gamma/temperature, use hyprsunset for screen light modes.
- **Audio:** Mute/change volume, pamixer backend (Pipewire or Pulseaudio).
- **Sysinfo:** OS, CPU, RAM, disk, GPU, WM info.

## Contributing
Fork the repo, make your changes, and create a Pull Request.

**Pull Request Rules:**
1. Describe what you added or changed.
2. Provide screenshots or video recordings to demonstrate changes.
3. Test it yourself before creating a Pull Request.

Or, create an Issue for bug reports.

Any help and support is appreciated.

## Maintaining
If you become a maintainer or want to be credited, or have questions, contact:
- [Gmail](mailto:nrw58886@gmail.com)
- [Telegram](https://t.me/Binarnik_Linux)

## Credits
- [iwnuplylo](https://github.com/IwnuplyNotTyan) – Arch Linux Package

## To-Do
- Allow changing screen brightness (currently only gamma/temperature)
- Bluetooth control
- Microphone control

## Stars
[![Stargazers over time](https://starchart.cc/binarylinuxx/hyprsettings.svg?background=%231d1d1d&axis=%23ffffff&line=%23ff2525)](https://starchart.cc/binarylinuxx/hyprsettings)
