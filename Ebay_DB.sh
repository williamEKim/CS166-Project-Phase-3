#!/bin/bash

python_prompt() {
    local options=("Yes" "No")
    local selected=0

    tput civis 

    while true; do
        echo -ne "\rWould you like to execute the Python Script?  \033[K"
        for i in "${!options[@]}"; do
            if [ "$i" -eq "$selected" ]; then
                echo -ne "\e[1;32m[ ${options[$i]} ]\e[0m  "
            else
                echo -ne "  ${options[$i]}   "
            fi
        done

        read -rsn1 key
        if [[ "$key" == $'\x1b' ]]; then
            read -rsn2 key
            case "$key" in
                "[C") selected=$(( (selected + 1) % 2 )) ;;
                "[D") selected=$(( (selected - 1 + 2) % 2 )) ;;
            esac
        elif [[ "$key" == "" ]]; then
            break
        fi
    done

    tput cnorm
    echo ""
    return $selected
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/cs166_server/psql.sh"

export DB_NAME=$USER"_eBay_DB"

python_prompt

if [ $? -eq 0 ]; then
    echo "Executing the Python Script..."
    python3 "$SCRIPT_DIR/backend/main.py" "$DB_NAME" "$PGPORT" "$USER"
else
    echo "Skipping Python Script."
fi

stop_prompt

if [ $? -eq 0 ]; then
    echo "Stopping the Postgre Server..."
    source "$SCRIPT_DIR/cs166_server/stopPostgreDB.sh"
else
    echo "Skipping Server Stop."
fi