#!/usr/bin/env python3

import os
import sys
#import re


def findPath(command):
    # if command includes a slash, treat it as a path (./x, ../x, /x)
    if "/" in command:
        if os.path.isfile(command) and os.access(command, os.X_OK):
            return command
        return None

    paths = os.environ.get("PATH", "").split(":")
    for directory in paths:
        if directory == "":
            directory = "."
        fullPath = os.path.join(directory, command)
        if os.path.isfile(fullPath) and os.access(fullPath, os.X_OK):
            return fullPath
    return None

def eprint(msg):
    os.write(2, (msg + "\n").encode())


while True:
    commandPrompt = os.environ.get("PS1", "$ ")
    try:
        userInput = input(commandPrompt).strip()
    except EOFError:
        sys.exit(0)

    #handles case where user 'enters' without input
    if userInput == '':
        continue

    background = False
    tokens = userInput.split()
    if tokens and tokens[-1] == '&':
        background = True
        userInput = " ".join(tokens[:-1]).strip()

    #handles built-in command exit
    if userInput == 'exit':
        os._exit(0)
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
                eprint("cd: no such file or directory: " + path[1])
    
    elif '>' in userInput:
        #split on '>' to get command and filename
        parts = userInput.split('>', 1)

        if len(parts) < 2 or parts[1].strip() == "":
            eprint("shell: syntax error")
            continue

        args = parts[0].strip().split()
        filename = parts[1].strip()
        
        path = findPath(args[0])
        if path is None:
            eprint(args[0] + ": command not found")
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
                os.execve(path, args, dict(os.environ))
                os._exit(1)
            else:
                #parent
                if not background:
                    _, status = os.waitpid(PID, 0)
                    exitCode = os.WEXITSTATUS(status)
                    if exitCode != 0:
                        eprint("Program terminated with exit code " + str(exitCode) + ".")
    
    elif '<' in userInput:
        #split on '>' to get command and filename
        parts = userInput.split('<', 1)

        if len(parts) < 2 or parts[1].strip() == "":
            eprint("shell: syntax error")
            continue

        args = parts[0].strip().split()
        filename = parts[1].strip()
        
        path = findPath(args[0])
        if path is None:
            eprint(args[0] + ": command not found")
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
                os.execve(path, args, dict(os.environ))
                os._exit(1)
            else:
                #parent
                if not background:
                    _, status = os.waitpid(PID, 0)
                    exitCode = os.WEXITSTATUS(status)
                    if exitCode != 0:
                        eprint("Program terminated with exit code " + str(exitCode) + ".")
    #TA suggestion: time pipes or manage pipes
    elif '|' in userInput:
        parts = userInput.split('|')
        prevRead = None
        pids = []

        for i, cmdString in enumerate(parts):
            args = cmdString.strip().split()
            if len(args) == 0:
                eprint("shell: syntax error")
                break

            path = findPath(args[0])
            
            if path is None:
                eprint(args[0] + ": command not found")
                break

            # create a pipe for every command except the last
            if i < len(parts) - 1:
                readEnd, writeEnd = os.pipe()
            
            PID = os.fork()
            if PID == 0:
                # hook up stdin from previous pipe
                if prevRead is not None:
                    os.dup2(prevRead, 0)
                    os.close(prevRead)
                # hook up stdout to current pipe (not for last command)
                if i < len(parts) - 1:
                    os.dup2(writeEnd, 1)
                    os.close(writeEnd)
                    os.close(readEnd)
                os.execve(path, args, dict(os.environ))
                os._exit(1)
            else:
                pids.append(PID)
                if prevRead is not None:
                    os.close(prevRead)
                if i < len(parts) - 1:
                    os.close(writeEnd)
                    prevRead = readEnd

        if not background:
            for pid in pids:
                os.waitpid(pid, 0)

    else:
        #handle simple command
        args = userInput.split()
        path = findPath(args[0])
        if path is None:
            eprint(args[0] + ": command not found")
        else:
            PID = os.fork()
            if PID == 0:
                #
                os.execve(path, args, dict(os.environ))
                os._exit(1)
            else:
                #
                if not background:
                    _, status = os.waitpid(PID, 0)
                    exitCode = os.WEXITSTATUS(status)
                    if exitCode != 0:
                        eprint("Program terminated with exit code " + str(exitCode) + ".")
        
        
