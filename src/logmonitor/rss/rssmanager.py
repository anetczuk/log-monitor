#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import logging
from typing import Dict, List
from enum import Enum, auto, unique
import threading

from logmonitor.utils import save_recent_date, get_recent_date, write_data
from logmonitor.configfileyaml import ConfigField
from logmonitor.rss.generator.rssgenerator import RSSGenerator
from logmonitor.rss.generatorspawn import spawn_generator_from_cfg


_LOGGER = logging.getLogger(__name__)


# =========================================================================


#
class RSSManager:
    class State:
        """Container for generator and it's state."""

        def __init__(self, gentype, generator: RSSGenerator = None):
            self.generator: RSSGenerator = generator
            self.type = gentype
            self.valid = True  # answers question: is problem with generator?

    # =================================

    def __init__(self, parameters=None):
        if parameters is None:
            parameters = {}
        self._params = parameters.copy()
        self._generators: List[RSSManager.State] = None

    def is_gen_valid(self):
        """Check if all generators are valid.

        Return 'True' if valid, otherwise 'False'.
        """
        if not self._generators:
            # not initialized
            _LOGGER.warning("invalid state - no generators")
            return False
        for gen_state in self._generators:
            gen_type = gen_state.type
            if not gen_state.valid:
                _LOGGER.warning("invalid generator: %s", gen_type)
                return False
        # everything ok
        return True

    # returns 'True' if everything is OK, otherwise 'False'
    def generate_data(self):
        if self._generators is None:
            self._initialize_generators()
        if not self._generators:
            _LOGGER.warning("generators not initialized")
            return

        _LOGGER.info("========== generating RSS data ==========")
        recent_datetime = get_recent_date()

        for gen_state in self._generators:
            gen_type = gen_state.type
            gen = gen_state.generator
            gen_name = gen.get_name()
            _LOGGER.info("----- running generator %s -----", gen_name)
            try:
                gen_data: Dict[str, str] = gen.generate()
            except Exception:  # pylint: disable=W0703
                _LOGGER.exception("exception raised during generator execution")
                gen_state.valid = False
                continue

            if not gen_data:
                _LOGGER.info("generation not completed for generator '%s'", gen_type)
                gen_state.valid = False
            else:
                gen_state.valid = True
            self._write_data(gen_type, gen_data)

        save_recent_date(recent_datetime)
        _LOGGER.info("========== generation ended ==========")

    def close(self):
        if self._generators:
            for gen_state in self._generators:
                gen = gen_state.generator
                gen.close()

    def _initialize_generators(self):
        self._generators = []

        gen_items = self._params.get(ConfigField.GENITEM.value, [])  # list of dicts
        if not gen_items:
            _LOGGER.warning("could not get generators configuration")
            return

        for gen_params in gen_items:
            gen_state = spawn_generator_from_cfg(gen_params)
            if gen_state is not None:
                state = RSSManager.State(*gen_state)
                self._generators.append(state)

        _LOGGER.info("generators initialized: %s", len(self._generators))

    def _write_data(self, generator_type, generator_data: Dict[str, str]):
        if not generator_data:
            return
        data_root_dir = self._params.get(ConfigField.GENERAL.value, {}).get(ConfigField.DATAROOT.value)
        for rss_out, content in generator_data.items():
            if content is None:
                continue
            feed_path = os.path.join(data_root_dir, rss_out)
            feed_dir = os.path.dirname(feed_path)
            os.makedirs(feed_dir, exist_ok=True)
            _LOGGER.info("writing %s content to file: %s", generator_type, feed_path)
            write_data(feed_path, content)


@unique
class RSSManagerState(Enum):
    PROCESSING = auto()
    VALID = auto()
    ERROR = auto()


#
class ThreadedRSSManager:
    def __init__(self, manager: RSSManager):
        self._manager: RSSManager = manager
        self._execute_loop = False  # flag to stop thread loop
        self._state_callback = None
        self._lock = threading.RLock()
        self._wait_object = threading.Condition()
        self._thread = None

    # set generator state (error) callback
    def set_state_callback(self, callback):
        self._state_callback = callback

    def start(self, refresh_time, startupdelay):
        """Start thread."""
        with self._lock:
            if self._execute_loop:
                _LOGGER.warning("thread already running")
                return
            self._execute_loop = True
            self._thread = threading.Thread(target=self._run_loop, args=[refresh_time, startupdelay])
            _LOGGER.info("starting thread")
            self._thread.start()

    def stop(self):
        with self._lock:
            if not self._execute_loop:
                _LOGGER.warning("thread already stopped")
                return
            _LOGGER.info("stopping thread")
            self._execute_loop = False
            try:
                with self._wait_object:
                    self._wait_object.notifyAll()  # pylint: disable=W4902
            except RuntimeError:
                # no threads wait for notification
                _LOGGER.info("thread does not wait")

    def execute_loop(self, refresh_time, startupdelay):
        """Start run loop without additional threads."""
        with self._lock:
            self._execute_loop = True
        self._run_loop(refresh_time, startupdelay)

    def execute_single(self):
        """Trigger single generation."""
        with self._lock:
            if not self._thread:
                _LOGGER.info("executing RSS manager")
                self._call_gen()
                return

            try:
                with self._wait_object:
                    _LOGGER.info("waking up RSS thread")
                    self._wait_object.notifyAll()  # pylint: disable=W4902
            except RuntimeError:
                # no threads wait for notification
                _LOGGER.info("thread does not wait")

    def _run_loop(self, refresh_time, startupdelay):
        try:
            if startupdelay > 0:
                _LOGGER.info("waiting %s seconds (startup delay)", startupdelay)
                with self._wait_object:
                    self._wait_object.wait(startupdelay)

            while True:
                with self._lock:
                    if not self._execute_loop:
                        break

                self._call_gen()

                with self._wait_object:
                    with self._lock:
                        if not self._execute_loop:
                            break
                    _LOGGER.info("waiting %s seconds before next fetch", refresh_time)
                    self._wait_object.wait(refresh_time)

            _LOGGER.info("thread loop ended")
            return

        except KeyboardInterrupt:
            _LOGGER.error("keyboard interrupt")
            self._callback_state(RSSManagerState.ERROR)
            # executed in case of exception
            raise

        except BaseException as exc:
            _LOGGER.exception("exception occurred in thread loop: %s", exc)
            self._callback_state(RSSManagerState.ERROR)
            # executed in case of exception
            raise

        finally:
            with self._lock:
                self._execute_loop = False

    def _call_gen(self):
        self._callback_state(RSSManagerState.PROCESSING)

        try:
            self._manager.generate_data()

        except RuntimeError as exc:
            _LOGGER.error("exception occurred when calling generator: %s", exc)

        if self._state_callback:
            valid = self._manager.is_gen_valid()
            if valid:
                self._callback_state(RSSManagerState.VALID)
            else:
                self._callback_state(RSSManagerState.ERROR)

    def _callback_state(self, state: RSSManagerState):
        if not self._state_callback:
            return
        self._state_callback(state)

    def join(self):
        with self._lock:
            if not self._thread:
                return
            _LOGGER.info("joining thread")
        self._thread.join()
        with self._lock:
            self._thread = None
        _LOGGER.info("thread terminated")
