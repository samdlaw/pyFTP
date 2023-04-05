#!/usr/bin/env python3
#
# FTP implementation using Python.
# This is required to overcome the limitation in ftp.exe whic is available as part of Windows (cmd)
# which does not support Passive mode or Secure FTP over SSL/TLS (FTPS). This Python implementation
# can work in passive mode as well as over SSL/TLS (FTPS).
#
import os
import re
import argparse
import ftplib
import getpass
from datetime import datetime, timedelta

class ftpProcess():
    # avail (function availability): Possible values
    #   -1: When Not Connected
    #    0: Both Connected and disconnected mode
    #    1: Connected only
    commandValid = {
        '?'             : {'avail':  0, 'func': 'help'      },
        'active'        : {'avail':  1, 'func': 'active'    },
        'append'        : {'avail':  1, 'func': 'appe'      },
        'ascii'         : {'avail':  1, 'func': 'ascii'     },
        'binary'        : {'avail':  1, 'func': 'binary'    },
        'bye'           : {'avail':  0, 'func': 'quit'      },
        'cd'            : {'avail':  1, 'func': 'cwd'       },
        'cdup'          : {'avail':  1, 'func': 'cdup'      },
        'close'         : {'avail':  1, 'func': 'close'     },
        'datasecure'    : {'avail':  1, 'func': 'datasecure'},
        'debug'         : {'avail':  0, 'func': 'debug'     },
        'del'           : {'avail':  1, 'func': 'dele'      },
        'delete'        : {'avail':  1, 'func': 'dele'      },
        'dir'           : {'avail':  1, 'func': 'nlist'     },
        'disconnect'    : {'avail':  1, 'func': 'close'     },
        'exit'          : {'avail':  0, 'func': 'quit'      },
        'help'          : {'avail':  0, 'func': 'help'      },
        'quit'          : {'avail':  0, 'func': 'quit'      },
        'get'           : {'avail':  1, 'func': 'retr'      },
        'lcd'           : {'avail':  0, 'func': 'lcd'       },
        'literal'       : {'avail':  1, 'func': 'remotecmd' },
        'ls'            : {'avail':  1, 'func': 'nlist'     },
        'mdir'          : {'avail':  1, 'func': 'mlsdir'    },
        'mdelete'       : {'avail':  1, 'func': 'mdelete'   },
        'mget'          : {'avail':  1, 'func': 'mget'      },
        'mls'           : {'avail':  1, 'func': 'mlsdir'    },
        'mput'          : {'avail':  1, 'func': 'mput'      },
        'mk'            : {'avail':  1, 'func': 'mkd'       },
        'mkdir'         : {'avail':  1, 'func': 'mkd'       },
        'open'          : {'avail': -1, 'func': 'open'      },
        'passive'       : {'avail':  1, 'func': 'passive'   },
        'prompt'        : {'avail':  0, 'func': 'prompt'    },
        'put'           : {'avail':  1, 'func': 'stor'      },
        'pwd'           : {'avail':  1, 'func': 'pwd'       },
        'quote'         : {'avail':  1, 'func': 'remotecmd' },
        'recv'          : {'avail':  1, 'func': 'retr'      },
        'remotehelp'    : {'avail':  1, 'func': 'remotehelp'},
        'ren'           : {'avail':  1, 'func': 'rnfr'      },
        'rename'        : {'avail':  1, 'func': 'rnfr'      },
        'rm'            : {'avail':  1, 'func': 'rmd'       },
        'rmdir'         : {'avail':  1, 'func': 'rmd'       },
        'send'          : {'avail':  1, 'func': 'stor'      },
        'secure'        : {'avail': -1, 'func': 'secure'    },
        'status'        : {'avail':  0, 'func': 'status'    },
        'type'          : {'avail':  1, 'func': 'type'      },
        'user'          : {'avail':  1, 'func': 'user'      },
        'verbose'       : {'avail':  0, 'func': 'verbose'   },
    }
#
    ftpCmdList = {
        'active'        : {'args': 0, 'help': 'Change data transfer mode to active'},
        'appe'          : {'args': 1, 'help': 'Append to a file'}, 
        'ascii'         : {'args': 0, 'help': 'Set ascii transfer type'},
        'binary'        : {'args': 0, 'help': 'Set binary transfer type'},
        'close'         : {'args': 0, 'help': 'Terminate ftp session'},
        'cwd'           : {'args': 1, 'help': 'Change remote working directory'},
        'cdup'          : {'args': 0, 'help': 'Change remote to parent directory'},
        'datasecure'    : {'args': 0, 'help': 'Toggle data channel protection'},
        'debug'         : {'args': 0, 'help': 'Toggle debugging mode'},
        'dele'          : {'args': 1, 'help': 'Delete remote file'},
        'help'          : {'args': 1, 'help': 'Print local help information'},
        'lcd'           : {'args': 1, 'help': 'Change local working directory'},
        'mdelete'       : {'args': 1, 'help': 'Delete multiple files'},
        'mget'          : {'args': 1, 'help': 'Get multiple files'},
        'mkd'           : {'args': 1, 'help': 'Make directory on the remote machine'},
        'mlsdir'        : {'args': 1, 'help': 'List contents of multiple remote directories'},
        'mput'          : {'args': 1, 'help': 'Send multiple files'},
        'nlist'         : {'args': 1, 'help': 'List contents of remote directory'},
        'open'          : {'args': 1, 'help': 'Connect to remote ftp'},
        'passive'       : {'args': 0, 'help': 'Change data transfer mode to active'},
        'prompt'        : {'args': 0, 'help': 'Force interactive prompting on multiple commands'},
        'pwd'           : {'args': 0, 'help': 'Print working directory on remote machine'},
        'quit'          : {'args': 0, 'help': 'Terminate ftp session and exit'},
        'remotecmd'     : {'args': 1, 'help': 'Send arbitrary ftp command'},
        'remotehelp'    : {'args': 1, 'help': 'Get help from remote server'},
        'retr'          : {'args': 1, 'help': 'Receive file'},
        'rmd'           : {'args': 1, 'help': 'Remove directory on the remote machine'},
        'rnfr'          : {'args': 1, 'help': 'Rename file'},
        'secure'        : {'args': 0, 'help': 'Connect using FTP over SSL/TLS'},
        'status'        : {'args': 0, 'help': 'Show current status'},
        'stor'          : {'args': 1, 'help': 'Send one file'},
        'type'          : {'args': 1, 'help': 'Set file transfer type'},
        'user'          : {'args': 1, 'help': 'Send new user information'},
        'verbose'       : {'args': 0, 'help': 'Toggle verbose mode'},
    }
#
    systStatus = {
        'binary'        : False,
        'debug'         : False,
        'passive'       : True,
        'prompt'        : True,
        'secure'        : False,
        'datasecure'    : False,
        'verbose'       : True,
    }
#
    def __init__(self):
        self.loginHost = ''
        self.loginPort = 0
        self.loginUser = ''

        self.localDir = os.getcwd()
        self.remoteDir = ''
        self.DefaultRemoteDir = '/ENTER-DIRECTORY-NAME'

        self.ftpCommand = ''
        self.remoteLastCheck = None
        self.ftpConn = None
        self.ftpTerminate = False
#
# Process User Input Commands
# Main function to handle user command inputs
#
    def ftpProcessCommand(self, userInput):
        splitInput = userInput.strip().lower().split(' ', 1)
        userCommand = splitInput[0]
        userParams = ''
        if len(splitInput) > 1:
            userParams = splitInput[1]
        
        if self.ftpCheckCommand(userCommand) == False:
            return
        
        if len(self.commandValid[userCommand]['func']) == 0:
            print('Under development. Please contact developer for latest status.')
            return
        
        callFnName = self.commandValid[userCommand]['func']
        callFTPFn = getattr(self, 'ftpCommand_' + callFnName)
        if self.ftpCmdList[callFnName]['args'] > 0:
            callFTPFn(userParams)
        else:
            callFTPFn()
#
# Validate user commands
# Called from:
#   ftpProcessCommand
#
    def ftpCheckCommand(self, userCommand):
        if userCommand not in self.commandValid.keys():
            print('Invalid command.')
            return False
        
        commandErr = False
        hostLastConnected = datetime.now() - timedelta(minutes = 7)
        if self.commandValid[userCommand]['avail'] == -1 and len(self.loginHost) > 0:
            portInfo = ''
            if self.loginPort > 0:
                portInfo = f':{self.loginPort}'
            print(f'Already connected to {self.loginHost}{portInfo}, use disconnect first.')
            commandErr = True
        elif self.commandValid[userCommand]['avail'] == 1 and len(self.loginHost) == 0:
            print('Not connected.')
            commandErr = True
        elif self.commandValid[userCommand]['avail'] == 1:
            if (len(self.loginUser) > 0 and (self.remoteLastCheck <= hostLastConnected)) or \
                        (self.ftpConnectionActive() == False):
                print('Connection closed by remote host.')
                commandErr = True
        
        if commandErr == True:
            return False
        
        self.ftpCommand = userCommand
        return True
#
# Check connection active. sends NOOP to server
# Called from:
#   ftpCheckCommand
#
    def ftpConnectionActive(self):
        if self.ftpCommand_remotecmd('NOOP', -1)['cmdsuccess'] == False:
            self.loginHost = ''
            self.loginPort = 0
            self.loginUser = ''
            return False
        
        return True
#
# Toggle Debug mode
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_debug(self):
        self.ftpCommand_usermodes()

        self.ftpCommand_ftpdebug()
#
# Set Python FTP debugger
# Called from:
#   ftpCommand_debug
#   ftpCommand_open
#   ftpProcessCommand
#
    def ftpCommand_ftpdebug(self, debugFromConnect = False):
        if len(self.loginHost) == 0 and debugFromConnect == False:
            return
        
        if self.systStatus['debug'] == True:
            self.ftpConn.set_debuglevel(1)
        else:
            self.ftpConn.set_debuglevel(0)
#
# Toggle prompt for multiple files
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_prompt(self):
        self.ftpCommand_usermodes()
#
# Toggle Verbose mode
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_verbose(self):
        self.ftpCommand_usermodes()
#
# Toggle SSL/TLS for connection
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_secure(self):
        self.ftpCommand_usermodes()
#
# Toggle secure channel for data connection
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_datasecure(self):
        if self.systStatus['secure'] == False:
            print('Secure FTP not available. Disconnect and reconnect in secure mode.')
            return
        
        if self.systStatus['datasecure'] == False:
            self.ftpCommand_prot_p()
        else:
            self.ftpCommand_prot_c()
        
        self.ftpCommand_usermodes(True)
#
# Create Secure Data connection
# Called from:
#   ftpCommand_datasecure
#   ftpCommand_user
#
    def ftpCommand_prot_p(self):
        cmdResponse = self.ftpCommand_remotecmd(f'PBSZ 0', -1)
        if cmdResponse['cmdsuccess'] == False:
            return
        
        cmdResponse = self.ftpCommand_remotecmd(f'PROT P')
        if cmdResponse['cmdsuccess'] == True:
            self.systStatus['datasecure'] = True
#
# Clear the Secure Data connection
# Called from:
#   ftpCommand_datasecure
#
    def ftpCommand_prot_c(self):
        cmdResponse = self.ftpCommand_remotecmd(f'PROT C')
        if cmdResponse['cmdsuccess'] == True:
            self.systStatus['datasecure'] = False
#
# Update the existing user modes
# Called from:
#   ftpCommand_portpasv
#   ftpCommand_debug
#   ftpCommand_prompt
#   ftpCommand_verbose
#   ftpCommand_secure
#   ftpCommand_datasecure
#
    def ftpCommand_usermodes(self, statusOnly = False):
        statusName = self.ftpCommand

        if statusName not in self.systStatus.keys():
            return
        
        if statusOnly == False:
            if self.systStatus[statusName] == True:
                self.systStatus[statusName] = False
            else:
                self.systStatus[statusName] = True
        
        if self.systStatus[statusName] == True:
            modeStatus = 'On'
        else:
            modeStatus = 'Off'
        
        if statusName == 'binary':
            modeInfo = 'Binary Mode'
        elif statusName == 'debug':
            modeInfo = 'Debugging'
        elif statusName == 'prompt':
            modeInfo = 'Interactive mode'
        elif statusName == 'passive':
            modeInfo = 'Passive mode'
        elif statusName == 'secure':
            modeInfo = 'FTP over SSL/TLS (FTPS)'
        elif statusName == 'datasecure':
            modeInfo = 'Secure Data Channel'
        
        print(f'{modeInfo} {modeStatus} .')
#
# Change connection to active mode
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_active(self):
        self.ftpCommand_portpasv(False)
#
# Change connection to passive mode
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_passive(self):
        self.ftpCommand_portpasv(True)
#
# Update the existing connection mode
# Called from:
#   ftpCommand_active
#   ftpCommand_passive
#
    def ftpCommand_portpasv(self, newStatus):
        newStatus = None

        try:
            self.ftpConn.set_pasv(newStatus)
        except ftplib.all_errors as err:
            print(str(err))
            return
        
        self.ftpCommand = 'passive'
        self.systStatus['passive'] = newStatus
        self.ftpCommand_usermodes(True)
#
# Change Transfer Type to ascii. Overrides the function 'type'
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_ascii(self):
        self.ftpCommand = 'type'
        self.ftpCommand_type('ascii')
#
# Change Transfer Type to binary. Overrides the function 'type'
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_binary(self):
        self.ftpCommand = 'type'
        self.ftpCommand_type('binary')
#
# Change transfer type. Send TYPE to remote server
# Called from:
#   ftpCommand_ascii
#   ftpCommand_binary
#
    def ftpCommand_type(self, cmdParams = ''):
        if len(cmdParams) == 0:
            if self.systStatus['binary'] == True:
                strCommand = 'binary'
            else:
                strCommand = 'ascii'
        
            print(f'Using {strCommand} mode to transfer files.')
            return
        
        newStatus = None
        if cmdParams in ['ascii', 'a']:
            command = 'TYPE A'
            newStatus = False
        elif cmdParams in ['binary', 'i']:
            command = 'TYPE I'
            newStatus = True
        else:
            print(f'{cmdParams}: unknown mode.')
            return
        
        if self.ftpCommand_remotecmd(command)['cmdsuccess'] == True:
            self.systStatus['binary'] = newStatus
#
# Print help
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_help(self, helpString = ''):
        userInputs = getInputParams(helpString)
        if len(userInputs) == 0:
            printLine = ''
            printItem = 0
            helpList = list(self.commandValid.keys())
            helpList.sort()
            for helpItem in helpList:
                if len(printLine) > 0:
                    printLine += ' '
                
                printLine = f'{printLine}{helpItem:<15}'
                printItem += 1
                if printItem >= 5:
                    print(printLine)
                    printLine = ''
                    printItem = 0
        else:
            for helpItem in userInputs:
                if helpItem not in self.commandValid.keys():
                    print(f'Invalid help command {helpItem}')
                else:
                    helpFunc = self.commandValid[helpItem]['func']
                    helpStr = self.ftpCmdList[helpFunc]['help']
                    print(f'{helpItem:<15} {helpStr}')
#
# Print remotehelp
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_remotehelp(self, helpString = ''):
        helpString = getInputParams(helpString)

        if len(helpString) == 0:
            helpString = ''
        else:
            helpString = helpString[0]
        
        self.ftpCommand_remotecmd(f'HELP {helpString}', 1)
#
# Print the status
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_status(self):
        for statKeys in self.systStatus.keys():
            if self.systStatus[statKeys] == True:
                strStatus = 'On'
            else:
                strStatus = 'Off'
            
            print(f'{statKeys:<15}: {strStatus}')
#
# Connect to remote host. Sends OPEN to connect
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_open(self, host = ''):
        host = getUserInput('To:', host, False, 'open host [port]')

        if len(host) == 0:
            return
        
        userInputs = getInputParams(host)
        host = userInputs[0]
        port = 0
        portInfo = ''
        if len(userInputs) > 1:
            port = int(userInputs[1])
            portInfo = f':{port}'
        
        connectInfo = f'{host}{portInfo}'

        if self.systStatus['secure'] == True:
            self.ftpConn = ftplib.FTP_TLS()
        else:
            self.ftpConn = ftplib.FTP()
        
        self.ftpCommand_ftpdebug(True)
        try:
            ftpResponse = self.ftpConn.connect(host,port)
        except ftplib.all_errors as err:
            if str(err)[:13] == '[Errno 11001]':
                print(f'Unknown host {connectInfo}')
            else:
                print('> ftp: connect :Connection refused')
        else:
            self.loginHost = host
            self.loginPort = port
            print(f'Connected to {connectInfo}.')
            print(ftpResponse)
            self.ftpCommand_auth()
            self.ftpCommand_user()
#
# Sends AUTH info for SSL/TLS connection
# Called from:
#   ftpCommand_open
#
    def ftpCommand_auth(self):
        if self.systStatus['secure'] == False:
            return
        
        self.ftpConn.auth()
#
# Get User ID, Password & Account for login. Sends USER to login and passes further PASS and AUTH as requested by using ftpCommand 'userAuth' function
# Called from:
#   ftpProcessCommand
#   ftpCommand_open
#
    def ftpCommand_user(self, userParams = ''):
        loginDetails = getUserInput(f'User ({self.loginHost}:({getpass.getuser()})):', userParams, False, 'user username [password] [account]')
        userInputs = getInputParams(loginDetails)
        try:
            loginID = userInputs[0]
        except:
            loginID = ''
        
        try:
            loginPass = userInputs[1]
        except:
            loginPass = ''
        
        try:
            loginAcct = userInputs[2]
        except:
            loginAcct = ''
        
        if len(loginID) == 0:
            return
        
        cmdResponse = self.ftpCommand_remotecmd(f'USER {loginID}')
        while self.ftpCommand_errorCode(cmdResponse) in range(300, 400):
            checkStatus = self.ftpCommand_errorCode(cmdResponse)
            if checkStatus == 331:
                cmdResponse = self.ftpCommand_userAuth('PASS', loginPass)
                loginPass = cmdResponse[0]
                cmdResponse = cmdResponse[1]
            elif checkStatus == 332:
                cmdResponse = self.ftpCommand_userAuth('ACCT', loginAcct)
                loginAcct = cmdResponse[0]
                cmdResponse = cmdResponse[1]
            else:
                cmdResponse['cmdsuccess'] = False
            
        if cmdResponse['cmdsuccess'] == False:
            print('Login failed.')
        elif self.ftpCommand_errorCode(cmdResponse) in [230, 232]:
            self.loginUser = loginID
            self.DefaultRemoteDir = self.ftpConn.pwd()
            self.remoteLastCheck = datetime.now()
            if self.systStatus['secure'] == True:
                self.ftpCommand_prot_p()
#
# Gets additional details to be sent to remote server for user authentication
# Called from:
#   ftpCommand_user
#
    def ftpCommand_userAuth(self, command, userParams = '', ):
        reqStr = ''
        if command == 'PASS':
            reqStr = f'Password:'
        elif command == 'ACCT':
            reqStr = f'Account:'

        loginDetails = getUserInput(reqStr, userParams, True)
        userInputs = getInputParams(loginDetails)
        try:
            loginDetails = userInputs[0]
        except:
            loginDetails = ''
        
        cmdResponse = self.ftpCommand_remotecmd(f'{command} {loginDetails}')

        return [loginDetails, cmdResponse]
#
# Disconnect from remote host. Could've used QUIT and may be redundant code
# Called from:
#   ftpProcessCommand
#   ftpCommand_quit
#
    def ftpCommand_close(self):
        if len(self.loginHost) == 0:
            return
        
        try:
            ftpResponse = self.ftpConn.quit()
        except:
            ftpResponse = self.ftpConn.close()
        finally:
            self.loginHost = ''
            self.loginPort = 0
            self.loginUser = ''
            if ftpResponse != None:
                print(ftpResponse)
#
# Disconnect & terminate the process
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_quit(self):
        self.ftpCommand_close()
        self.ftpTerminate = True
#
# Change local directory
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_lcd(self, newLocalDir = ''):
        localDir = os.getcwd()

        if len(newLocalDir) > 0:
            localDir = newLocalDir
        
        if os.path.exists(localDir) and os.path.isdir(localDir):
            self.localDir = localDir
            print(f'Local directory now {localDir}.')
        else:
            print(f'{localDir}: File not found')
#
# Get Remote Directory Filenames
# ls --> NLST
# dir --> LIST
# Should've user PORT/EPRT for Active Mode or PASV/EPSV for Passive mode before performing the directory listing but this works
# Called from:
#   ftpProcessCommand
#   ftpCommand_mlsdir
#
    def ftpCommand_nlist(self, remoteDir = '', localFile = '', appendFile = False):
        outputError = False
        file2write = None
        if len(localFile) > 0:
            fileMode = 'w'
            if appendFile == True:
                fileMode = 'a'
            file2write = open(localFile, fileMode)
        
        sendRemoteCmd = 'NLST'
        if self.ftpCommand == 'ls':
            sendRemoteCmd = 'NLST'
        elif self.ftpCommand == 'dir':
            sendRemoteCmd = 'LIST'
        
        dir_list = []
        try:
            ftpResponse = self.ftpConn.retrlines(f'{sendRemoteCmd} {remoteDir}', dir_list.append)
        except ftplib.all_errors as err:
            print(str(err))
            outputError = True
        else:
            for fileEntry in dir_list:
                if len(localFile) > 0:
                    file2write.write(fileEntry + '\n')
                else:
                    print(fileEntry)
            print(ftpResponse)
        
        if len(localFile) > 0:
            file2write.close()
            if outputError == True:
                os.remove(localFile)
        
        return not(outputError)
#
# List multiple directory from remote server to local file. Calls ftpCommand 'nlist' function to get details in required format
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_mlsdir(self, dirList = ''):
        dirList = getUserInput('Remote files:', dirList)

        userInputs = getInputParams(dirList)
        if len(userInputs) < 2:
            dirList = getUserInput('Local file:')
            userInputs += getInputParams(dirList)
        
        if len(userInputs) < 2:
            print(f'{self.ftpCommand["command"]} remote files local file.')
            return
        
        remoteFileList = userInputs[:-1]
        localFileName  = userInputs[-1]
        if (localFileName == '-'):
            localFileName = ''
        elif self.systStatus['prompt'] == True:
            userOption = getYorN(f'Output to local-file: {localFileName}')
            if userOption in ['n', 'q']:
                return
        
        filePresent = False
        if self.ftpCommand == 'mls':
            self.ftpCommand = 'ls'
        elif self.ftpCommand == 'mdir':
            self.ftpCommand = 'dir'
        else:
            return
        
        for remoteFile in remoteFileList:
            newStatus = self.ftpCommand_nlist(remoteFile, localFileName, filePresent)
            filePresent = filePresent or newStatus
#
# Sends multiple files to remote server
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_mput(self, filList = ''):
        filList = getUserInput('Local files:', filList, False, f'{self.ftpCommand} Local files')

        userInputs = getInputParams(filList)
        if len(userInputs) < 1:
            return
        
        for inputFil in userInputs:
            if self.systStatus['prompt'] == True:
                userOption = getYorN(f'{self.ftpCommand} {inputFil}')
                if userOption == 'q':
                    return
                elif userOption == 'n':
                    continue
            
            self.ftpCommand_stor(inputFil, inputFil)
#
# Calls ftpCommand 'remfiles' for processing multiple files - get only
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_mget(self, dirList = ''):
        self.ftpCommand_remfiles(dirList)
#
# Calls ftpCommand 'remfiles' for processing multiple files - delete only
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_mdelete(self, dirList = ''):
        self.ftpCommand_remfiles(dirList)
#
# Depending on user call, it'll get multiple files or delete multiple files from a directory list
# Called from:
#   ftpProcessCommand_mget
#   ftpProcessCommand_mdelete
#
    def ftpCommand_remfiles(self, dirList = ''):
        dirList = getUserInput('Remote files:', dirList, False, f'{self.ftpCommand} remote files')

        userInputs = getInputParams(dirList)
        if len(userInputs) < 1:
            return
        
        for inputDir in userInputs:
            fileList = []
            try:
                ftpResponse = self.ftpConn.retrlines(f'NLST {inputDir}', fileList.append)
            except ftplib.all_errors as err:
                print(str(err))
                continue
            else:
                for fileItem in fileList:
                    if self.systStatus['prompt'] == True:
                        userOption = getYorN(f'{self.ftpCommand} {fileItem}')
                        if userOption == 'q':
                            return
                        elif userOption == 'n':
                            continue
                    if self.ftpCommand == 'mget':
                        self.ftpCommand_retr(fileItem, fileItem)
                    elif self.ftpCommand == 'mdelete':
                        self.ftpCommand_dele(fileItem)
#
# Change Remote Working Directory. send CWD to remote server
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_cwd(self, remoteDir = ''):
        remoteDir = getUserInput('Remote directory:', remoteDir, False, f'{self.ftpCommand} remote directory')

        if len(remoteDir) == 0:
            return
        
        userInputs = getInputParams(remoteDir)
        remoteDir = userInputs[0]

        cmdResponse = self.ftpCommand_remotecmd(f'CWD {remoteDir}')
        if cmdResponse['cmdsuccess'] == True:
            getRemoteFile = cmdResponse['response'].strip().find(' : ') + 3
            self.remoteDir = cmdResponse['response'][getRemoteFile:]
#
# Get Present Working Directory. Send PWD to remote server
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_pwd(self):
        cmdResponse = self.ftpCommand_remotecmd(f'PWD', 1)
        if cmdResponse['cmdsuccess'] == True:
            getDir = re.search('\"(.+)\"', cmdResponse['response'])
            if len(getDir.groups()) > 0:
                self.remoteDir = getDir.group(1)
#
# Get to Parent Working Directory. Send CDUP to remote server
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_cdup(self):
        cmdResponse = self.ftpCommand_remotecmd(f'CDUP')
        self.remoteDir = self.ftpConn.pwd()
#
# Delete remote file. Send DELE to remote server
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_dele(self, remoteFile = ''):
        remoteFile = getUserInput('Remote file:', remoteFile, False, f'{self.ftpCommand} remote file.')

        if len(remoteFile) == 0:
            return
        
        userInputs = getInputParams(remoteFile)
        remoteFile = userInputs[0]

        self.ftpCommand_remotecmd(f'DELE {remoteFile}')
#
# Delete remote directory. Send RMD to remote server
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_rmd(self, remoteDir = ''):
        remoteDir = getUserInput('Directory name:', remoteDir, False, f'{self.ftpCommand} directory-name')

        if len(remoteDir) == 0:
            return
        
        userInputs = getInputParams(remoteDir)
        remoteDir = userInputs[0]

        self.ftpCommand_remotecmd(f'RMD {remoteDir}')
#
# Uses RETR to get file from remote server
# Called from:
#   ftpProcessCommand
#   ftpCommand_remfiles
#
    def ftpCommand_retr(self, remoteFile = '', localFile = '', appendFile = False):
        remoteFile = getUserInput('Remote file:', f'{remoteFile} {localFile}', False, f'{self.ftpCommand} Remote file')

        userInputs = getInputParams(remoteFile)
        try:
            remoteFile = userInputs[0]
        except:
            remoteFile = ''
        
        try:
            localFile = userInputs[1]
        except:
            localFile = ''
        
        if len(remoteFile) == 0:
            return
        
        localFile = getUserInput('Local file:', localFile)
        userInputs = getInputParams(localFile)
        try:
            localFile = userInputs[0]
        except:
            localFile = ''

        fileLocalPath = os.path.dirname(localFile)
        fileLocalBase = os.path.basename(localFile)

        if len(fileLocalPath) == 0 or not os.path.exists(fileLocalPath):
            fileLocalPath = self.localDir
        
        localFile = os.path.join(fileLocalPath, fileLocalBase)
        if os.path.exists(localFile) and os.path.isdir(localFile):
            fileLocalPath = localFile
            fileLocalBase = re.sub('[\$\*\/\(\)]', '_', remoteFile)
            localFile = os.path.join(fileLocalPath, fileLocalBase)
        
        fileUsageMode = 'w'
        if appendFile == True:
            fileUsageMode = 'a'
        
        if self.systStatus['binary'] == True:
            fileUsageMode += 'b'
        
        outputError = False
        file2write = open(localFile, fileUsageMode)

        try:
            if self.systStatus['binary'] == True:
                ftpResponse = self.ftpConn.retrbinary(f'RETR {remoteFile}', lambda x: file2write.write(x))
            else:
                ftpResponse = self.ftpConn.retrlines(f'RETR {remoteFile}', lambda x: file2write.write(x + '\n'))
        except ftplib.all_errors as err:
            print(str(err))
            outputError = True
        else:
            print(ftpResponse)
        
        file2write.close()
        if outputError == True:
            os.remove(localFile)
#
# Calls the ftpCommand 'stor' function to override for append
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_appe(self, inputParams = ''):
        self.ftpCommand_stor(inputParams, '', True)
#
# Uses STOR to send file to remote server
# Called from:
#   ftpProcessCommand
#   ftpCommand_mput
#   ftpCommand_appe
#
    def ftpCommand_stor(self, localFile = '', remoteFile = '', appendFile = False):
        localFile = getUserInput('Local file:', f'{localFile} {remoteFile}', False, f'{self.ftpCommand} Local file')

        userInputs = getInputParams(localFile)
        try:
            localFile = userInputs[0]
        except:
            localFile = ''
        
        try:
            remoteFile = userInputs[1]
        except:
            remoteFile = ''
        
        if len(localFile) == 0:
            return
        
        if not os.path.exists(localFile) or not os.path.isfile(localFile):
            print(f'{localFile}: File not found')
            return
        
        remoteFile = getUserInput('Remote file:', remoteFile)
        userInputs = getInputParams(remoteFile)
        try:
            remoteFile = userInputs[0]
        except:
            remoteFile = ''
        
        fileSendCommand = 'STOR'
        if appendFile == True:
            fileSendCommand = 'APPE'
        
        file2send = open(localFile, 'rb')

        try:
            if self.systStatus['binary'] == True:
                ftpResponse = self.ftpConn.storbinary(f'{fileSendCommand} {remoteFile}', file2send)
            else:
                ftpResponse = self.ftpConn.storlines(f'{fileSendCommand} {remoteFile}', file2send)
        except ftplib.all_errors as err:
            print(str(err))
        else:
            print(ftpResponse)
        
        file2send.close()
#
# Uses RNFR followed by RNTO to rename file on remote server
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_rnfr(self, oldName = '', newName = ''):
        oldName = getUserInput('From name:', f'{oldName} {newName}', False, f'{self.ftpCommand} from-name to-name.')

        userInputs = getInputParams(oldName)
        try:
            oldName = userInputs[0]
        except:
            oldName = ''

        try:
            newName = userInputs[1]
        except:
            newName = ''

        if len(oldName) == 0:
            return
        
        newName = getUserInput('To name:', newName, False, f'{self.ftpCommand} from-name to-name.')
        userInputs = getInputParams(newName)
        try:
            newName = userInputs[0]
        except:
            newName = ''
        
        if len(newName) == 0:
            return
        
        cmdResponse = self.ftpCommand_remotecmd(f'RNFR {oldName}')
        while self.ftpCommand_errorCode(cmdResponse) in range(300, 400):
            checkStatus = self.ftpCommand_errorCode(cmdResponse)
            if checkStatus == 350:
                cmdResponse = self.ftpCommand_remotecmd(f'RNTO {newName}')
            else:
                cmdResponse['cmdsuccess'] = False
        
        if cmdResponse['cmdsuccess'] == False:
            print('Rename failed.')
#
# Creates a new remote directory. Send MKD to remote server
# Called from:
#   ftpProcessCommand
#
    def ftpCommand_mkd(self, newDir = ''):
        newDir = getUserInput('Directory name:', newDir, False, f'{self.ftpCommand} directory-name.')

        if len(newDir) == 0:
            return
        
        userInputs = getInputParams(newDir)
        newDir = userInputs[0]

        self.ftpCommand_remotecmd(f'MKD {newDir}')
#
# Send arbitrary command to remote server. This is also called from multiple functions
# printResponse values:
#   -1: No output
#    0: Default output (Depending on Verbose mode)
#    1: Forced output (Always)
# Called from:
#   ftpProcessCommand
#   ftpConnectionActive     (No output)
#   ftpCommand_prot_p       (No output - partially)
#   ftpCommand_prot_c
#   ftpCommand_type
#   ftpCommand_remotehelp   (Forced output)
#   ftpCommand_user
#   ftpCommand_userAuth
#   ftpCommand_cwd
#   ftpCommand_pwd          (Forced output)
#   ftpCommand_cdup
#   ftpCommand_dele
#   ftpCommand_rmd
#   ftpCommand_rnfr
#   ftpCommand_mkd
#
    def ftpCommand_remotecmd(self, commandToSend, printResponse = 0):
        commandStatus = {'cmdsuccess': False, 'response': ''}

        try:
            ftpResponse = self.ftpConn.sendcmd(commandToSend)
        except ftplib.all_errors as err:
            commandStatus['cmdsuccess'] = False
            commandStatus['response'] = str(err)
        else:
            commandStatus['cmdsuccess'] = True
            commandStatus['response'] = ftpResponse
        
        if printResponse == 1 or (printResponse == 0 and self.systStatus['verbose'] == True):
            print(commandStatus['response'])
        
        return commandStatus
#
# Pass the ftpCommand 'remotecmd' response to get the error code in number format
# Called from:
#   ftpCommand_user
#   ftpCommand_rnfr
#
    def ftpCommand_errorCode(self, ftpResponse):
        response = ftpResponse['response'][0:3].strip()

        if response.isdigit() == False:
            response = 0
        
        return int(response)
###############################################################################
def getUserInput(userPrompt = '', inputValue = '', getPassword = False, help = ''):
    defaultPrompt = 'pyFTP>'
    inputValue = inputValue.strip()
    if len(inputValue) > 0:
        return inputValue

    userPrompt = userPrompt.strip()
    if len(userPrompt) > 0:
        newPrompt = f'{userPrompt}'
    else:
        newPrompt = f'{defaultPrompt}'
    
    if getPassword == False:
        inputValue = input(f'{newPrompt} ').strip()
    else:
        inputValue = getpass.getpass(f'{newPrompt} ').strip()
    
    if len(inputValue) == 0 and len(help) > 0:
        print(f'Usage: {help}')
        
    return inputValue
###############################################################################
def getYorN(userPrompt, validOptions = ['y', 'n', 'q']):
    userOption = ''
    optionStr = '/'.join(validOptions)
    while userOption not in validOptions:
        userOption = getUserInput(f'{userPrompt} {optionStr}?').lower()

    return userOption
###############################################################################
def getInputParams(strInput = ''):
    patternFile = "\w\@\$\*\(\)\-\[\]\{\}\:\.\\\/\?"
    matchPattern = "(?<=\")[" + patternFile + " ]+(?=\")|" \
                    "[" + patternFile + "]+"
    return re.findall(matchPattern, strInput)
###############################################################################
if __name__ == "__main__":
    defaultFolder = os.path.expanduser('~')
    ftpUser = ftpProcess()

    parser = argparse.ArgumentParser(
        description = 'FTP implementation using Python. Windows ftp.exe does not support Passive mode or FTP over SSL/TLS (FTPS). ' + \
            'This implementation can work in passive mode as well as over SSL/TLS.',
        epilog = 'Contact Sabyasachi \"SAM\" Mohapatra in case of issues'
    )

    parser.add_argument('-v', dest='verbose', default=False, action='store_true', help="Suppresses display of remote server responses.")
    parser.add_argument('-i', dest='prompt', default=False, action='store_true', help="Turns off interactive prompting during multiple file transfers")
    parser.add_argument('-d', dest='debug', default=False, action='store_true', help="Enables debugging")
    parser.add_argument('-t', dest='ssltls', default=False, action='store_true', help="Enables FTP over SSL/TLS (FTPS)")
    parser.add_argument('-s', dest='ftpcommandfile', metavar='filename', help="Specifies a text file containing FTP commands; the commands will automatically run after FTP starts.")
    parser.add_argument('host', nargs='?', help="Specifies the host name or IP addess of the remote host to connect to.")
    args = parser.parse_args()

    if args.verbose:
        ftpUser.systStatus['verbose'] = False

    if args.prompt:
        ftpUser.systStatus['prompt'] = False

    if args.debug:
        ftpUser.systStatus['debug'] = True

    if args.ssltls:
        ftpUser.systStatus['secure'] = True

    if args.host:
        ftpUser.ftpCommand_open(args.host)
    
    if args.ftpcommandfile:
        try:
            scriptFile = open(args.ftpcommandfile, 'r')
        except:
            print(f'Error opening script file {args.ftpcommandfile}.')
            ftpUser.ftpTerminate = True
        else:
            for scriptLine in scriptFile:
                ftpUser.ftpProcessCommand(scriptLine)
            scriptFile.close()
        
    while(ftpUser.ftpTerminate == False):
        getUserCommand = getUserInput()
        ftpUser.ftpProcessCommand(getUserCommand)