#!/usr/bin/env python3

import os
import sys
import re



while True:
    commandPrompt = os.environ.get("PS1", "$")
    try:
        userInput = input(commandPrompt).strip()
    except EOFError:
        sys.exit(0)

    #handles case where user 'enters' without input
    if userInput == '':
        continue

    #handles built-in command exit
    if userInput == 'exit':
        sys.exit(0)
    #handles built-in command cd
    elif userInput.startswith('cd'):
        #retrieves path
        path = userInput.split()
        #continue if no path was specified
        if len(path) < 2:
            continue
        else:
            try:
                #changes directory to new path
                os.chdir(path[1])
            except :
                #error message when path is invalid
                print("cd: no such file or directory: " + path[1])
    
    elif '>' in userInput:
        #redirection
        PID = os.fork()
    
    elif '<' in userInput:
        #redirection
        PID = os.fork()
    
    elif '|' in userInput:
        #pipe
        PID = os.fork()
    else:
        #handle simple command
        pass
        
        
