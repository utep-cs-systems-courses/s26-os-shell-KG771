#!/usr/bin/env python3

import os
import sys
import re


def findPath(command):
    if command.startswith('/'):
        return command
    paths = os.environ.get("PATH", "").split(":")
    for directory in paths:
        fullPath = os.path.join(directory, command)
        if os.access(fullPath, os.X_OK):
            return fullPath
    return None


while True:
    commandPrompt = os.environ.get("PS1", "$ ")
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
            except FileNotFoundError:
                #error message when path is invalid
                print("cd: no such file or directory: " + path[1])
    
    elif '>' in userInput:
        #split on '>' to get command and filename
        parts = userInput.split('>')
        args = parts[0].strip().split()
        filename = parts[1].strip()
        
        path = findPath(args[0])
        if path is None:
            print(args[0] + ": command not found")
        else:
            PID = os.fork()
            if PID == 0:
                #child 
                fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
                #
                os.dup2(fd, 1)
                #
                os.close(fd)
                # 
                os.execve(path, args, os.environ)
                sys.exit(1)
            else:
                #parent
                _, status = os.wait()
                exitCode = os.WEXITSTATUS(status)
                if exitCode != 0:
                    print("Program terminated with exit code " + str(exitCode))
    
    elif '<' in userInput:
        #split on '>' to get command and filename
        parts = userInput.split('<')
        args = parts[0].strip().split()
        filename = parts[1].strip()
        
        path = findPath(args[0])
        if path is None:
            print(args[0] + ": command not found")
        else:
            PID = os.fork()
            #should handle case where pid < 0?
            if PID == 0:
                #child
                fd = os.open(filename, os.O_RDONLY)
                #
                os.dup2(fd, 0)
                #
                os.close(fd)
                #
                os.execve(path, args, os.environ)
                sys.exit(1)
            else:
                #parent
                _, status = os.wait()
                exitCode = os.WEXITSTATUS(status)
                if exitCode != 0:
                    print("Program terminated with exit code " + str(exitCode))
    #TA suggestion: time pipes or manage pipes
    elif '|' in userInput:
        parts = userInput.split('|')
        leftArgs = parts[0].strip().split()
        rightArgs = parts[1].strip().split()

        leftPath = findPath(leftArgs[0])
        rightPath = findPath(rightArgs[0])

        if leftPath is None:
            print(leftArgs[0] + ": command not found")
        elif rightPath is None:
            print(rightArgs[0] + ": command not found")
        else:
            readEnd, writeEnd = os.pipe()
        
            #first child runs left command
            PID1 = os.fork()
            if PID1 == 0:
                os.close(readEnd)          
                os.dup2(writeEnd, 1)        
                os.close(writeEnd)          
                os.execve(leftPath, leftArgs, os.environ)
                sys.exit(1)
            
            #second child runs right command
            PID2 = os.fork()
            if PID2 == 0:
                os.close(writeEnd)         
                os.dup2(readEnd, 0)       
                os.close(readEnd)          
                os.execve(rightPath, rightArgs, os.environ)
                sys.exit(1)
            
            #parent
            os.close(readEnd)
            os.close(writeEnd)
            os.wait()
            os.wait()
    elif '&' in userInput:
        #
        args = userInput.replace('&', '').strip().split()
        path = findPath(args[0])
        
        if path is None:
            print(args[0] + ": command not found")
        else:
            PID = os.fork()
            if PID == 0:
                #
                os.execve(path, args, os.environ)
                sys.exit(1)
            else:
                #
                pass
    else:
        #handle simple command
        args = userInput.split()
        path = findPath(args[0])
        if path is None:
            print(args[0] + ": command not found")
        else:
            PID = os.fork()
            if PID == 0:
                #
                os.execve(path, args, os.environ)
                sys.exit(1)
            else:
                #
                _, status = os.wait()
                #
                exitCode = os.WEXITSTATUS(status)
                if exitCode != 0:
                    print("Program terminated with exit code " + str(exitCode))
        
        
