#!/usr/bin/python3
#
# MIT License
#
# Copyright (c) 2024 Arkadiusz Netczuk <dev.arnet@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

try:
    ## following import success only when file is directly executed from command line
    ## otherwise will throw exception when executing as parameter for "python -m"
    # pylint: disable=W0611
    import __init__
except ImportError:
    ## when import fails then it means that the script was executed indirectly
    ## in this case __init__ is already loaded
    pass


import sys
import os
import argparse
import logging
import time
import subprocess  # nosec

from logmonitor import logger
from logmonitor.configfileyaml import load_config, ConfigField
from logmonitor.rss.rssmanager import ThreadedRSSManager, RSSManager, RSSManagerState
from logmonitor.rss.rssserver import RSSServerManager
from logmonitor.systray.traymanager import TrayManager, TrayManagerState


_LOGGER = logging.getLogger(__name__)


def open_log(log_viewer, log_path):
    try:
        command = log_viewer % log_path + " &"
    except TypeError:
        _LOGGER.exception("unable to run logger, command: %s log path: %s", log_viewer, log_path)
        return
    _LOGGER.info("opening log viewer: %s", command)
    with subprocess.Popen(command, shell=True):  # nosec
        pass


def state_converter(manager_state: RSSManagerState, tray_manager: ThreadedRSSManager):
    if manager_state is RSSManagerState.PROCESSING:
        tray_manager.set_state(TrayManagerState.PROCESSING)
        return
    if manager_state is RSSManagerState.VALID:
        tray_manager.set_valid(True)
        return
    if manager_state is RSSManagerState.ERROR:
        tray_manager.set_valid(False)
        return
    tray_manager.set_valid(False)
    raise RuntimeError(f"unhandled manager state: {manager_state.name}")


def start_with_tray(parameters):
    if parameters is None:
        parameters = {}
    general_section = parameters.get(ConfigField.GENERAL.value, {})
    data_root = general_section.get(ConfigField.DATAROOT.value)
    log_dir = general_section.get(ConfigField.LOGDIR.value, "")
    log_viewer = general_section.get(ConfigField.LOGVIEWER.value)
    refresh_time = general_section.get(ConfigField.REFRESHTIME.value, 3600)
    start_server = general_section.get(ConfigField.STARTSERVER.value, True)
    rss_port = general_section.get(ConfigField.PORT.value, 8080)
    startupdelay = general_section.get(ConfigField.STARTUPDELAY.value, 0)

    tray_manager = TrayManager(start_enabled=start_server)

    # async start of RSS server
    rss_server = RSSServerManager()
    rss_server.port = rss_port
    rss_server.rootDir = data_root

    if start_server:
        rss_server.start()
    else:
        _LOGGER.info("starting RSS server disabled")

    manager = RSSManager(parameters)
    threaded_manager = ThreadedRSSManager(manager)

    tray_manager.set_rss_server_callback(rss_server.switch_state)
    tray_manager.set_refresh_callback(threaded_manager.execute_single)

    threaded_manager.set_state_callback(lambda manager_state: state_converter(manager_state, tray_manager))

    log_path = os.path.join(log_dir, "log.txt")
    tray_manager.set_open_log_callback(lambda: open_log(log_viewer, log_path))

    # data generation main loop
    exit_code = 0
    try:
        # run in loop
        threaded_manager.start(refresh_time, startupdelay)
        tray_manager.run_loop()  # run tray main loop

    except KeyboardInterrupt:
        _LOGGER.info("keyboard interrupt detected - stopping")

    except:  # noqa pylint: disable=W0702
        _LOGGER.exception("unhandled exception detected - exiting")
        exit_code = 1

    finally:
        manager.close()
        threaded_manager.stop()
        threaded_manager.join()
        rss_server.stop()

    return exit_code


def generate_data(parameters):
    """Start raw generation loop."""
    general_section = parameters.get(ConfigField.GENERAL.value, {})
    startupdelay = general_section.get(ConfigField.STARTUPDELAY.value, 0)

    manager = RSSManager(parameters)

    # data generation main loop
    exit_code = 0
    try:
        # generate data and exit
        if startupdelay > 0:
            _LOGGER.info("waiting %s seconds (startup delay)", startupdelay)
            time.sleep(startupdelay)
        _LOGGER.info("generating RSS data only once")
        manager.generate_data()

    except KeyboardInterrupt:
        _LOGGER.info("keyboard interrupt detected - stopping")

    except:  # noqa pylint: disable=W0702
        _LOGGER.exception("unhandled exception detected - exiting")
        exit_code = 1

    return exit_code


# =======================================================================


def process_start(args):
    _LOGGER.info("starting with tray")
    _LOGGER.debug("logging to file: %s", logger.log_file)
    parameters = load_config(args.config)
    exit_code = start_with_tray(parameters)
    return exit_code


def process_generate(args):
    _LOGGER.info("starting generator")
    _LOGGER.debug("logging to file: %s", logger.log_file)
    parameters = load_config(args.config)

    if args.startupdelay is not None:
        general_section = parameters.get(ConfigField.GENERAL.value, {})
        general_section[ConfigField.STARTUPDELAY.value] = args.startupdelay

    exit_code = generate_data(parameters)
    return exit_code


# =======================================================================


def main():
    parser = argparse.ArgumentParser(description="log monitor", prog="logmonitor.main")
    parser.add_argument("-la", "--logall", action="store_true", help="Log all messages")
    # have to be implemented as parameter instead of command (because access to 'subparsers' object)
    parser.add_argument("--listtools", action="store_true", help="List tools")
    parser.set_defaults(func=None)

    subparsers = parser.add_subparsers(help="one of tools", description="use one of tools", dest="tool", required=False)

    ## =================================================

    description = "start server"
    subparser = subparsers.add_parser("start", help=description)
    subparser.description = description
    subparser.set_defaults(func=process_start)
    subparser.add_argument("-c", "--config", action="store", required=False, help="Path to YAML config file")
    # subparser.add_argument("-la", "--logall", action="store_true", help="Log all messages")
    # subparser.add_argument("-f", "--files", nargs="+", default=[], help="Files to analyze")
    # subparser.add_argument(
    #     "-d", "--dirs", nargs="+", default=[], help="Directories to analyze (will recursively search for JSON files)"
    # )
    # subparser.add_argument(
    #     "--exclude", nargs="+", default=[], help="Space separated list of items to exclude. e.g. '/usr/*'"
    # )
    # subparser.add_argument("--outfile", action="store", required=False, help="Path to output file")

    ## =================================================

    description = "generate data"
    subparser = subparsers.add_parser("generate", help=description)
    subparser.description = description
    subparser.set_defaults(func=process_generate)
    subparser.add_argument("-c", "--config", action="store", required=False, help="Path to YAML config file")

    subparser.add_argument(
        "--startupdelay", type=int, default=None, required=False, help="Set delay in seconds before first generation"
    )

    # subparser.add_argument("-la", "--logall", action="store_true", help="Log all messages")
    # subparser.add_argument("-f", "--files", nargs="+", default=[], help="Files to analyze")
    # subparser.add_argument(
    #     "-d", "--dirs", nargs="+", default=[], help="Directories to analyze (will recursively search for JSON files)"
    # )
    # subparser.add_argument(
    #     "--exclude", nargs="+", default=[], help="Space separated list of items to exclude. e.g. '/usr/*'"
    # )
    # subparser.add_argument("--outfile", action="store", required=False, help="Path to output file")

    ## =================================================

    args = parser.parse_args()

    if args.listtools is True:
        tools_list = list(subparsers.choices.keys())
        print(", ".join(tools_list))
        return 0

    if args.logall is True:
        logger.configure(logLevel=logging.DEBUG)
    else:
        logger.configure(logLevel=logging.INFO)

    if "func" not in args or args.func is None:
        ## no command given -- print help message
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    code = main()
    sys.exit(code)
