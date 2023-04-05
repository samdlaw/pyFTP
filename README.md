# pyFTP
## Introduction
If you are not using 3rd party tools like WinSCP or FileZilla, the ftp.exe provided on Windows (any version), does not support passive mode nor FTP over SSL/TLS (FTPS).

There must be a compelling reason to use command line interface for FTP and if you are part of this limited set of people, this Python implementation of FTP supports inbuilt functions as well as sending commands to remote server to accomplish FTP functionality in active mode, passive mode as well as SSL/TLS.

Note: SFTP (SSH FTP) is different from FTPS (FTP over SSL/TLS)

## License
This has been created as a learning experience. Not familiar with licensing agreements but just in case:
- Free for personal use and commercial use
- If you identify any fixes, make sure it is shared to the developer so that it can be merged with main code and shared with other users
- If you are using it as part of commercial application which is paid or free with ads (i.e. makes money in any form), please contribute to [Python Software Foundation][1]
## Help
You can run it as any python program. This has inbuilt help menu which can be used with `-h` option.

```
python3 pyftp.py -h
```

FTP commands used in ftp.exe should work as-is however command line argument may not work. Please refer the help for available options.
Note: the change in usage of passing of FTP command file as part of command line (there is no colon between `-s` flag and filename).

[1]: https://www.python.org/psf-landing/