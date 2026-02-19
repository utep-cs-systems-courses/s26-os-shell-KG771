#!/usr/bin/env python3

import os
import sys
import re


command = ''

def verifyCommand(command):
    return command

while True:
    commandPrompt = os.environ.get("PS1", "$")
    try:
        userInput = input(commandPrompt).strip()
    except EOFError:
        sys.exit(0)

    #handles case where user enters without input
    if userInput == '':
        continue

    if userInput == 'exit':
        sys.exit(0)
    elif userInput.startswith('cd'):
        os.chdir()
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
        
        
