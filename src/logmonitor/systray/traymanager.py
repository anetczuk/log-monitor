#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import logging
from enum import Enum, auto, unique

import pystray
from PIL import Image


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


_LOGGER = logging.getLogger(__name__)

logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)


@unique
class TrayManagerState(Enum):
    PROCESSING = auto()
    VALID = auto()
    ERROR = auto()


class TrayManager:
    def __init__(self, start_enabled=True):
        self._server_enabled: bool = start_enabled
        self._server_state: TrayManagerState = TrayManagerState.VALID

        self.server_callback = None
        self.refresh_callback = None
        self.open_log_callback = None

        self.ok_icon_image = load_icon("task-checkmark-icon-w.png")
        self.processing_icon_image = load_icon("task-sync-icon-w.png")
        self.disabled_icon_image = load_icon("task-remove-icon-w.png")
        self.error_icon_image = load_icon("task-error-icon-w.png")

        rss_server_item = pystray.MenuItem(
            "Run RSS Server", self._on_rss_server_clicked, checked=lambda item: self._server_enabled
        )

        rss_refresh_item = pystray.MenuItem("Refresh RSS", self._on_refresh_clicked)
        open_log_item = pystray.MenuItem("Open log", self._on_open_log_clicked)
        quit_item = pystray.MenuItem("Quit", self._on_quit_clicked)

        menu = pystray.Menu(rss_server_item, rss_refresh_item, open_log_item, quit_item)

        self.tray_icon = pystray.Icon(name="log-monitor", title="Log Monitor", menu=menu)
        self._set_icon()

    @property
    def server_enabled(self):
        return self._server_enabled

    @server_enabled.setter
    def server_enabled(self, new_state: bool):
        self._server_enabled = new_state
        self._set_icon()

    # @property
    # def is_error(self):
    #     return self._is_error
    #
    # @is_error.setter
    # def is_error(self, new_state: bool):
    #     self._is_error = new_state
    #     self._set_icon()

    def set_valid(self, new_state: bool):
        if new_state:
            self.set_state(TrayManagerState.VALID)
        else:
            self.set_state(TrayManagerState.ERROR)

    def set_state(self, new_state: TrayManagerState):
        self._server_state = new_state
        self._set_icon()

    def _set_icon(self):
        if not self._server_enabled:
            _LOGGER.info("server disabled - setting disabled icon")
            self.tray_icon.icon = self.disabled_icon_image
            return

        if self._server_state == TrayManagerState.ERROR:
            _LOGGER.info("error detected - setting error icon")
            self.tray_icon.icon = self.error_icon_image
            return
        if self._server_state == TrayManagerState.PROCESSING:
            _LOGGER.info("processing - setting processing icon")
            self.tray_icon.icon = self.processing_icon_image
            return

        _LOGGER.info("server operational - setting OK icon")
        self.tray_icon.icon = self.ok_icon_image

    def run_loop(self):
        """Execute event loop. Method have to be executed from main thread."""
        _LOGGER.info("starting systray loop")
        self.tray_icon.run()

    # =================================================

    # set callback for enable/disable RSS server
    def set_rss_server_callback(self, callback):
        self.server_callback = callback

    # set "refresh" callback
    def set_refresh_callback(self, callback):
        self.refresh_callback = callback

    # set open log callback
    def set_open_log_callback(self, callback):
        self.open_log_callback = callback

    # =================================================

    def _on_rss_server_clicked(self, icon, item):  # pylint: disable=W0613
        self._server_enabled = not item.checked
        self._set_icon()
        # icon.notify("server clicked")
        _LOGGER.info("server clicked to state %s", self._server_enabled)
        if self.server_callback is None:
            _LOGGER.info("server callback not set")
            return
        self.server_callback(self._server_enabled)

    def _on_refresh_clicked(self, icon, item):  # pylint: disable=W0613
        _LOGGER.info("refresh clicked")
        # icon.notify("refresh clicked")
        if self.refresh_callback is None:
            _LOGGER.info("refresh callback not set")
            return
        self.refresh_callback()

    def _on_open_log_clicked(self, icon, item):  # pylint: disable=W0613
        _LOGGER.info("open log clicked")
        # icon.notify("refresh clicked")
        if self.open_log_callback is None:
            _LOGGER.info("log callback not set")
            return
        self.open_log_callback()

    def _on_quit_clicked(self, icon, item):  # pylint: disable=W0613
        _LOGGER.info("quit clicked")
        icon.remove_notification()
        self.tray_icon.stop()


# ================================================================


def load_icon(icon_name):
    icon_path = os.path.join(SCRIPT_DIR, icon_name)
    icon_path = os.path.abspath(icon_path)
    return Image.open(icon_path)
