#!/bin/bash

stop_prompt() {
    local options=("Yes" "No")
    local selected=0

    tput civis 

    while true; do
        echo -ne "\rWould you like to stop your Postgre Server?  \033[K"
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

CURR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export DB_NAME=$USER"_eBay_DB"

source "$CURR_DIR/startPostgreSQL.sh"
source "$CURR_DIR/createPostgreDB.sh"
cs166_psql -p $PGPORT $DB_NAME < "$CURR_DIR/create_tables.sql"