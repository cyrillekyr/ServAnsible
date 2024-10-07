# ~/.bashrc: executed by bash(1) for non-login shells.

# Note: PS1 and umask are already set in /etc/profile. You should not
# need this unless you want different defaults for root.
# PS1='${debian_chroot:+($debian_chroot)}\h:\w\$ '
# umask 022

# You may uncomment the following lines if you want `ls' to be colorized:
# export LS_OPTIONS='--color=auto'
# eval "$(dircolors)"
# alias ls='ls $LS_OPTIONS'
# alias ll='ls $LS_OPTIONS -l'
# alias l='ls $LS_OPTIONS -lA'
#
# Some more alias to avoid making mistakes:
# alias rm='rm -i'
# alias cp='cp -i'
# alias mv='mv -i'

#Alias Perso

alias ll='ls -l'
alias la='ls -la'
alias sys='sudo su - sysadmin'
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

# Fonction pour obtenir le caractère du prompt en fonction de l'utilisateur
get_prompt_char() {
    if [ $EUID -eq 0 ]; then
        echo "#"
    else
        echo "$"
    fi
}


# Fonction pour obtenir la couleur du prompt en fonction de l'utilisateur
get_prompt_color() {
    local user_color="\[\e[97m\]" 
    if [[ "$USER" == "sysadmin" ]]; then
        if [[ "$HOSTNAME" == "sysadmin-rebond" ]]; then
            user_color="\[\033[41m\]"
        else
            user_color="\[\e[32m\]"
        fi
    fi
    echo -e "$user_color"
}

# Fonction pour définir le format du prompt
set_custom_prompt() {
    local user="$(whoami)"
    local host="$(hostname)"
    local path="\w"
    local date_time="$(date +'%d-%m-%Y - %T')"
    local prompt_color="$(get_prompt_color)"
    local prompt_char="$(get_prompt_char)"
    
    
    #  [16-04-2024 09:26:57 sysadmin@gitlab:~]$
    
    PS1="[$date_time $prompt_color$user@$host:$path\[\e[0m\]]$prompt_char "
}

# Appeler la fonction pour définir le format du prompt
PROMPT_COMMAND='set_custom_prompt'
set_custom_prompt
HISTTIMEFORMAT="%F %T "
