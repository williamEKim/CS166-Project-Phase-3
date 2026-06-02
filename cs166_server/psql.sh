#!/bin/bash

arrow_prompt() {
    local options=("Yes" "No")
    local selected=0

    # Hide cursor
    tput civis

    while true; do
        # Print options
        echo -ne "\rWould you like to Initiate PostgreSQL Terminal Window?  "
        for i in "${!options[@]}"; do
            if [ "$i" -eq "$selected" ]; then
                echo -ne "\e[1;32m[ ${options[$i]} ]\e[0m  "   # Highlighted in green
            else
                echo -ne "  ${options[$i]}   "
            fi
        done

        # Read a single keypress
        read -rsn1 key

        # Handle arrow keys (they send 3 chars: ESC [ A/B/C/D)
        if [[ "$key" == $'\x1b' ]]; then
            read -rsn2 key
            case "$key" in
                "[C") selected=$(( (selected + 1) % 2 )) ;;   # Right arrow
                "[D") selected=$(( (selected - 1 + 2) % 2 )) ;;  # Left arrow
            esac
        elif [[ "$key" == "" ]]; then
            break  # Enter key pressed
        fi
    done

    # Show cursor again
    tput cnorm
    echo ""

    return $selected
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export DB_NAME=$USER"_eBay_DB"

cs166_psql -p $PGPORT $DB_NAME < "$SCRIPT_DIR/create_tables.sql"

arrow_prompt

if [ $? -eq 0 ]; then
    echo "Starting PostgreSQL Terminal..."
    cs166_psql -p $PGPORT $DB_NAME
else
    echo "Skipping PostgreSQL Terminal."
fi