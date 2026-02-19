#!/usr/bin/env python3

import os
import sys
import re


command = ''

def checkValidCommand(command):
    if command != '':
        return command
    else:
        print(command + ": command not found")

        
 
childPID = os.fork()
PS1 = os.environ.get("PS1")

while True:
    if PS1:
        print("PS1" + command)
    else:
        print("$ " + command)
