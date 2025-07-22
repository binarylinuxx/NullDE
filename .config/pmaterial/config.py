#!/usr/bin/env python3
# pmaterial configuration file

def config():
    return {
        "waybar": {
            "input_template": "~/.config/pmaterial/waybar-template.css",
            "output_path": "~/.config/waybar/style.css"
        }
    }
