#!/bin/bash

# Cache directory for thumbnails
CACHE_DIR="$HOME/.cache/eww/mpris_art"
mkdir -p "$CACHE_DIR"

get_thumbnail_path() {
    local art_url="$1"
    
    if [[ -z "$art_url" ]]; then
        echo ""
        return
    fi
    
    # URL decode
    art_url=$(python3 -c "import urllib.parse; print(urllib.parse.unquote('$art_url'))" 2>/dev/null || echo "$art_url")
    
    # Handle file:// URLs
    if [[ "$art_url" == file://* ]]; then
        echo "${art_url#file://}"
        return
    fi
    
    # Handle base64 encoded images (simplified - just return empty for now)
    if [[ "$art_url" == data:image/* ]]; then
        echo ""
        return
    fi
    
    # Handle web URLs
    if [[ "$art_url" == http://* ]] || [[ "$art_url" == https://* ]]; then
        local ext="jpg"
        if [[ "$art_url" == *.png* ]]; then ext="png"; fi
        if [[ "$art_url" == *.gif* ]]; then ext="gif"; fi
        if [[ "$art_url" == *.jpeg* ]]; then ext="jpeg"; fi
        
        local cache_file="$CACHE_DIR/current_art.$ext"
        
        # Download with timeout
        if curl -s --max-time 2 -o "$cache_file" "$art_url" 2>/dev/null; then
            echo "$cache_file"
        else
            echo ""
        fi
        return
    fi
    
    echo ""
}

get_mpris_info() {
    # Find MPRIS players
    local players=($(dbus-send --session --dest=org.freedesktop.DBus --type=method_call --print-reply /org/freedesktop/DBus org.freedesktop.DBus.ListNames 2>/dev/null | grep -o 'org\.mpris\.MediaPlayer2\.[^"]*' | head -1))
    
    if [[ ${#players[@]} -eq 0 ]]; then
        echo "PERCENT:0"
        echo "DISPLAY_TEXT:No media playing"
        echo "TOOLTIP_TEXT:"
        echo "THUMBNAIL_PATH:"
        return
    fi
    
    local player="${players[0]}"
    
    # Get metadata
    local metadata=$(dbus-send --session --print-reply --dest="$player" /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get string:'org.mpris.MediaPlayer2.Player' string:'Metadata' 2>/dev/null)
    
    if [[ -z "$metadata" ]]; then
        echo "PERCENT:0"
        echo "DISPLAY_TEXT:MPRIS Error"
        echo "TOOLTIP_TEXT:Could not get metadata"
        echo "THUMBNAIL_PATH:"
        return
    fi
    
    # Extract title and artist (improved parsing)
    local title=$(echo "$metadata" | grep -A1 'xesam:title' | grep 'variant' | sed 's/.*string "\([^"]*\)".*/\1/' | head -1)
    
    # Artist parsing - handle array format
    local artist=$(echo "$metadata" | sed -n '/xesam:artist/,/variant/p' | grep 'string' | sed 's/.*string "\([^"]*\)".*/\1/' | head -1)
    
    # If that didn't work, try alternative parsing
    if [[ -z "$artist" ]]; then
        artist=$(echo "$metadata" | grep -A5 'xesam:artist' | grep 'string' | sed 's/.*string "\([^"]*\)".*/\1/' | head -1)
    fi
    local art_url=$(echo "$metadata" | grep -A1 'mpris:artUrl' | grep 'variant' | sed 's/.*string "\([^"]*\)".*/\1/' | head -1)
    local length=$(echo "$metadata" | grep -A1 'mpris:length' | grep 'variant' | sed 's/.*int64 \([0-9]*\).*/\1/' | head -1)
    
    # Get position
    local position=$(dbus-send --session --print-reply --dest="$player" /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get string:'org.mpris.MediaPlayer2.Player' string:'Position' 2>/dev/null | grep 'variant' | sed 's/.*int64 \([0-9]*\).*/\1/')
    
    # Set defaults if empty
    title=${title:-"Unknown Track"}
    artist=${artist:-"Unknown Artist"}
    length=${length:-1}
    position=${position:-0}
    
    # Calculate percentage
    local percent=0
    if [[ $length -gt 0 ]]; then
        percent=$((position * 100 / length))
    fi
    
    # Format display text
    local display_text="$title - $artist"
    
    # Format time
    local pos_sec=$((position / 1000000))
    local len_sec=$((length / 1000000))
    local pos_min=$((pos_sec / 60))
    local pos_sec_remainder=$((pos_sec % 60))
    local len_min=$((len_sec / 60))
    local len_sec_remainder=$((len_sec % 60))
    
    local tooltip_text=$(printf "%d:%02d / %d:%02d" $pos_min $pos_sec_remainder $len_min $len_sec_remainder)
    
    # Get thumbnail
    local thumbnail_path=$(get_thumbnail_path "$art_url")
    
    echo "PERCENT:$percent"
    echo "DISPLAY_TEXT:$display_text"
    echo "TOOLTIP_TEXT:$tooltip_text"
    echo "THUMBNAIL_PATH:$thumbnail_path"
}

# Main execution
if [[ $# -gt 0 ]]; then
    field=$(echo "$1" | tr '[:lower:]' '[:upper:]')
    if [[ "$field" == "SIMPLE" ]]; then
        # Just output title - artist for simple widget
        info=$(get_mpris_info)
        display_text=$(echo "$info" | grep "^DISPLAY_TEXT:" | cut -d':' -f2-)
        if [[ "$display_text" == "No media playing" ]]; then
            echo ""
        else
            echo "$display_text"
        fi
    else
        get_mpris_info | grep "^$field:" | cut -d':' -f2-
    fi
else
    get_mpris_info
fi
