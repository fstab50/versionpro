#!/usr/bin/env bash

# GPL v3 License
#
# Copyright (c) 2018-2019 Blake Huber
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


function _complete_4_horsemen_commands(){
    local cmds="$1"
    local split='5'       # times to split screen width
    local ct="0"
    local IFS=$' \t\n'
    local formatted_cmds=( $(compgen -W "${cmds}" -- "${cur}") )

    for i in "${!formatted_cmds[@]}"; do
        formatted_cmds[$i]="$(printf '%*s' "-$(($COLUMNS/$split))"  "${formatted_cmds[$i]}")"
    done

    COMPREPLY=( "${formatted_cmds[@]}")
    return 0
    #
    # <-- end function _complete_region_subcommands -->
}


function _complete_4_horsemen_subcommands(){
    local cmds="$1"
    local split='3'       # times to split screen width
    local ct="0"
    local IFS=$' \t\n'
    local formatted_cmds=( $(compgen -W "${cmds}" -- "${cur}") )

    for i in "${!formatted_cmds[@]}"; do
        formatted_cmds[$i]="$(printf '%*s' "-$(($COLUMNS/$split))"  "${formatted_cmds[$i]}")"
    done

    COMPREPLY=( "${formatted_cmds[@]}")
    return 0
    #
    # <-- end function _complete_region_subcommands -->
}


function _complete_versionpro_commands(){
    local cmds="$1"
    local split='6'       # times to split screen width
    local ct="0"
    local IFS=$' \t\n'
    local formatted_cmds=( $(compgen -W "${cmds}" -- "${COMP_WORDS[1]}") )

    for i in "${!formatted_cmds[@]}"; do
        formatted_cmds[$i]="$(printf '%*s' "-$(($COLUMNS/$split))"  "${formatted_cmds[$i]}")"
    done

    COMPREPLY=( "${formatted_cmds[@]}")
    return 0
    #
    # <-- end function _complete_versionpro_commands -->
}


function _numargs(){
    ##
    ## Returns count of number of parameter args passed
    ##
    local parameters="$1"
    local numargs=0

    if [[ ! "$parameters" ]]; then
        printf -- '%s\n' "0"
    else
        for i in $(echo $parameters); do
            numargs=$(( $numargs + 1 ))
        done
        printf -- '%s\n' "$numargs"
    fi
    return 0
    #
    # <-- end function _numargs -->
}


function _parse_compwords(){
    ##
    ##  Interogate compwords to discover which of the  5 horsemen are missing
    ##
    compwords=("${!1}")
    four=("${!2}")

    declare -a missing_words

    for key in "${four[@]}"; do
        if [[ ! "$(echo "${compwords[@]}" | grep ${key##*-})" ]]; then
            missing_words=( "${missing_words[@]}" "$key" )
        fi
    done
    printf -- '%s\n' "${missing_words[@]}"
    #
    # <-- end function _parse_compwords -->
}


function _versionpro_completions(){
    ##
    ##  Completion structures for xlines exectuable
    ##
    local commands                  #  commandline parameters (--*)
    local subcommands               #  subcommands are parameters provided after a command
    local numargs                   #  num arg words: integer count of number of commands, subcommands
    local cur                       #  completion word at index position 0 in COMP_WORDS array
    local prev                      #  completion word at index position -1 in COMP_WORDS array
    local initcmd                   #  completion word at index position -2 in COMP_WORDS array

    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    initcmd="${COMP_WORDS[COMP_CWORD-2]}"

    # initialize vars
    COMPREPLY=()
    numargs="${#COMP_WORDS[@]}"

    options='--help --dryrun --debug --version'
    commands=' --update --force-set --pypi'


    case "${cur}" in

        '--h'*)
            COMPREPLY=( $(compgen -W '--help' -- ${cur}) )
            return 0
            ;;

        '--dr'*)
            COMPREPLY=( $(compgen -W '--dryrun' -- ${cur}) )
            return 0
            ;;

        '--p'*)
            COMPREPLY=( $(compgen -W '--pypi' -- ${cur}) )
            return 0
            ;;

        '--f'*)
            COMPREPLY=( $(compgen -W '--force-set' -- ${cur}) )
            return 0
            ;;

        '--u'*)
            COMPREPLY=( $(compgen -W '--update' -- ${cur}) )
            return 0
            ;;

        '--v'*)
            COMPREPLY=( $(compgen -W '--version' -- ${cur}) )
            return 0
            ;;

        'version' | 'versionp' | 'versionpr')
            COMPREPLY=( $(compgen -W "${commands} ${options}" -- ${cur}) )
            return 0
            ;;

    esac

    case "${prev}" in

        '--help' | '--version')
            return 0
            ;;

        '--dryrun')
            COMPREPLY=( $(compgen -W '--force-set' -- ${cur}) )
            return 0
            ;;


        '--update')
            ##
            ##  Return compreply with any of the 5 comp_words that
            ##  not already present on the command line
            ##
            declare -a horsemen
            horsemen=( '--debug' '--pypi' '--force-set' )
            subcommands=$(_parse_compwords COMP_WORDS[@] horsemen[@])
            numargs=$(_numargs "$subcommands")

            if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ] && (( "$numargs" > 2 )); then
                _complete_4_horsemen_subcommands "${subcommands}"
            else
                COMPREPLY=( $(compgen -W "${subcommands}" -- ${cur}) )
                #COMPREPLY=( $(compgen -W '--set-version --pypi --debug' -- ${cur}) )
            fi
            return 0
            ;;

        '--debug')
            ##
            ##  Return compreply with any of the 5 comp_words that
            ##  not already present on the command line
            ##
            declare -a horsemen
            horsemen=( '--update' '--pypi' '--force-set' )
            subcommands=$(_parse_compwords COMP_WORDS[@] horsemen[@])
            numargs=$(_numargs "$subcommands")

            if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ] && (( "$numargs" > 2 )); then
                _complete_4_horsemen_subcommands "${subcommands}"
            else
                COMPREPLY=( $(compgen -W "${subcommands}" -- ${cur}) )
                #COMPREPLY=( $(compgen -W '--set-version --pypi --debug' -- ${cur}) )
            fi
            return 0
            ;;

        '--pypi')
            ##
            ##  Return compreply with any of the 5 comp_words that
            ##  not already present on the command line
            ##
            declare -a horsemen
            horsemen=( '--debug' '--update' )
            subcommands=$(_parse_compwords COMP_WORDS[@] horsemen[@])
            numargs=$(_numargs "$subcommands")

            if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ] && (( "$numargs" > 2 )); then
                _complete_4_horsemen_subcommands "${subcommands}"
            else
                COMPREPLY=( $(compgen -W "${subcommands}" -- ${cur}) )
            fi
            return 0
            ;;

        '--force-set')
            ##
            ##  Return compreply with any of the 5 comp_words that
            ##  not already present on the command line
            ##
            declare -a horsemen
            horsemen=(  '--debug' '--update' )
            subcommands=$(_parse_compwords COMP_WORDS[@] horsemen[@])
            numargs=$(_numargs "$subcommands")

            if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ] && (( "$numargs" > 2 )); then
                _complete_4_horsemen_subcommands "${subcommands}"
            else
                COMPREPLY=( $(compgen -W "${subcommands}" -- ${cur}) )
            fi
            return 0
            ;;

        'versionpro')
            if [ "$cur" = "" ] || [ "$cur" = "-" ] || [ "$cur" = "--" ]; then

                _complete_versionpro_commands "${commands} ${options}"
                return 0

            fi
            ;;

    esac

    COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )

} && complete -F _versionpro_completions versionpro
