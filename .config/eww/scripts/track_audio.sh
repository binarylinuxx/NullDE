#!/bin/bash

# Ensure EWW is running
if ! pgrep -x "eww" > /dev/null; then
  eww daemon
fi

# Open the OSD window
eww open audio-osd

# Function to update EWW variables and show OSD
update_osd() {
  local sink_name="$1"
  local volume="$2"
  eww update sink_name="$sink_name"
  eww update volume_text="$volume%"
}

# Function to get current default sink
get_default_sink() {
  wpctl status | grep -A 10 "Sinks:" | grep '*' | sed -n 's/.*\[\([0-9]*\)\].*\.\(.*\)/\2/p' | tr -d ' '
}

# Function to get current volume
get_volume() {
  wpctl get-volume @DEFAULT_SINK@ | awk '{print int($2 * 100)}'
}

# Initial update
current_sink=$(get_default_sink)
current_volume=$(get_volume)
update_osd "$current_sink" "$current_volume"

# Monitor for sink changes
pw-dump | jq -r '.[] | select(.type == "PipeWire:Interface:Node" and .info.props["media.class"] == "Audio/Sink") | .info.props["node.name"]' | while read -r sink; do
  current_sink=$(get_default_sink)
  current_volume=$(get_volume)
  update_osd "$current_sink" "$current_volume"
  sleep 0.5
done &

# Trap to close OSD on script exit
trap 'eww close audio-osd' EXIT

# Keep script running
while true; do
  sleep 1
done
