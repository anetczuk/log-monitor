# log-monitor

Parse log files and expose data in form of RSS feed.


## Installation

Installation of package can be done by:
 - to install package from downloaded ZIP file execute: `pip3 install --user -I file:log-monitor-master.zip#subdirectory=src`
 - to install package directly from GitHub execute: `pip3 install --user -I git+https://github.com/anetczuk/log-monitor.git#subdirectory=src`
 - uninstall: `pip3 uninstall logmonitor`

Installation For development:
 - `install-deps.sh` to install package dependencies only (`requirements.txt`)
 - `install-package.sh` to install package in standard way through `pip` (with dependencies)
 - `install-package-dev.sh` to install package in developer mode using `pip` (with dependencies)


## Config file

There is [example configuration file](examples/config_example.yaml) in examples. It has following content:

<!-- insertstart include="examples/config_example.yaml" pre="\n\n```\n" post="\n```\n\n" -->

```
# configuration file

general:
    trayicon: true             # enable or disable tray icon
    genloop: true              # enable or disable RSS generation loop (if set to 'false' then generation will be triggered only once)
    startupdelay: 15           # set delay in seconds before first generation (useful on startup to wait for KeePassXC to start before) 
    startserver: true          # set 'false' to prevent starting RSS server (just store data to local files), default: true
    port: 8080                 # RSS feed port, default 8080
    refreshtime: 3600          # time in seconds between consecutive RSS generator loop iterations, default 3600
    dataroot: "data"           # path to store data; path absolute or relative to config directory
                               # default value is app dir inside user home directory
    logdir: "log"              # path to store logs; path absolute or relative to config directory
                               # default value is app dir inside user home directory
    logviewer: "gedit %s"      # command line to view log file, %s will be replaced with log path

item:
    - parser: "logging"                     # parser identifier
      enabled: true                         # is parser enabled
      params:
        name: "app"                         # parser name (part of output path) 
        logfile: "/var/log/app_log.txt"     # iniput log file path
        # log entry format as in configuration of Python's logging module
        fmt: "%(asctime)s,%(msecs)-3d %(levelname)-8s %(threadName)s %(name)s:%(funcName)s [%(filename)s:%(lineno)d] %(message)s"
        datefmt: "%Y-%m-%d %H:%M:%S"        # datetime format as in configuration of Python's logging module
        loglevel: "WARNING"                 # log level threshold (same as in Python's logging module)

```

<!-- insertend -->

Fields are quite self-descriptive. There are two possible methods of authentication:
- raw data stored inside the file
- KeePassXC deamon.

For KeePassXC there is `itemurl` field identifying item in the database.

Moreover application can be executed without RSS server (`startserver = false`) or detached from system tray (`trayicon = true`).

Some fields are common for config file and command-line arguments. In such cases command-line version has precedence 
over values in the file (overrides values taken from config file).


## References

- [grok description](https://github.com/garyelephant/pygrok/tree/master)


## License

BSD 3-Clause License

Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


## Icons License

Icons are downloaded from [https://uxwing.com](https://uxwing.com) under following [license](https://uxwing.com/license/).
