## <a name="main_help"></a> python3 -m logmonitor.main --help
```
usage: logmonitor.main [-h] [-la] [--listtools] {start,generate} ...

log monitor

options:
  -h, --help        show this help message and exit
  -la, --logall     Log all messages
  --listtools       List tools

subcommands:
  use one of tools

  {start,generate}  one of tools
    start           start server
    generate        generate data
```



## <a name="start_help"></a> python3 -m logmonitor.main start --help
```
usage: logmonitor.main start [-h] [-c CONFIG]

start server

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to YAML config file
```



## <a name="generate_help"></a> python3 -m logmonitor.main generate --help
```
usage: logmonitor.main generate [-h] [-c CONFIG] [--startupdelay STARTUPDELAY]

generate data

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to YAML config file
  --startupdelay STARTUPDELAY
                        Set delay in seconds before first generation
```
