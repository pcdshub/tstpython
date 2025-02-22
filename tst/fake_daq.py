# BlueskyScan.py

import enum
from threading import Event, Thread

from ophyd.status import Status


class DaqState(enum.IntEnum):
    RESET = 0
    UNALLOCATED = 1
    ALLOCATED = 2
    CONNECTED = 3
    CONFIGURED = 4
    STARTING = 5
    PAUSED = 6
    RUNNING = 7


class FakeDaqLcls2:
    def __init__(self):
        # Misc to make scans work
        self.name = "daq"
        self.parent = None

        self.rate = 120  # 120 Hz fake triggers
        self.state = DaqState.ALLOCATED

        self.motors = []
        self.group_mask = 1
        self.events = 1
        self.record = False
        self.detname = "scan"
        self.scantype = "scan"
        self.serial_number = "1234"
        self.alg_name = "raw"
        self.alg_version = [1, 0, 0]
        self.seq_ctl = None

        self.interrupt_ev = Event()
        self.last_pos = None

    def _change_state(self, new_state: DaqState):
        # Change through states and print the changes
        self.interrupt_ev.set()
        while self.state != new_state:
            if new_state > self.state:
                next_state = DaqState(self.state.value + 1)
            else:
                next_state = DaqState(self.state.value - 1)
            if self.state == DaqState.CONFIGURED and next_state == DaqState.STARTING:
                print("STARTING RUN")
            elif self.state == DaqState.STARTING and next_state == DaqState.CONFIGURED:
                print("ENDING RUN")
            self.state = next_state
            print(f"State is now {self.state.name}")

    def read(self):
        return {}

    def describe(self):
        return {}

    def trigger(self):
        self.interrupt_ev.set()
        status = Status(self)
        if self.state in (
            DaqState.RESET,
            DaqState.UNALLOCATED,
            DaqState.ALLOCATED,
            DaqState.RUNNING,
        ):
            status.set_exception(
                RuntimeError(f"Invalid starting state {self.state} for trigger!")
            )
        else:
            self._change_state(DaqState.RUNNING)
            self.start_running_thread(status)
        return status

    def start_running_thread(self, status: Status):
        self.th = Thread(target=self._collection_thread, args=[status])
        self.th.start()

    def _collection_thread(self, status: Status):
        self.interrupt_ev.clear()
        try:
            for motor in self.motors:
                # This is checked in the real daq, so it will error here if invalid
                self.last_pos = motor.position
        except Exception:
            status.set_exception(
                RuntimeError("Daq requires real motor objects in motors config!")
            )
            return
        interrupted = self.interrupt_ev.wait(self.events / self.rate)
        if interrupted:
            status.set_exception(RuntimeError("Collection thread interrupted"))
        else:
            self._change_state(DaqState.STARTING)
            status.set_finished()

    def read_configuration(self):
        # done at the first read after a configure
        return {}

    def describe_configuration(self):
        # the metadata for read_configuration()
        return {}

    def configure(
        self,
        *,
        motors=None,
        group_mask=None,
        events=None,
        record=None,
        detname=None,
        scantype=None,
        serial_number=None,
        alg_name=None,
        alg_version=None,
        seq_ctl=None,
    ):
        if motors is not None:
            if isinstance(motors, list):
                self.motors = motors
            else:
                raise TypeError("motors must be of type list")
        if group_mask is not None:
            if isinstance(group_mask, int):
                self.group_mask = group_mask
            else:
                raise TypeError("group_mask must be of type int")
        if events is not None:
            if isinstance(events, int):
                self.events = events
            else:
                raise TypeError("events must be of type int")
        if record is not None:
            if isinstance(record, bool):
                self.record = record
            else:
                raise TypeError("record must be of type bool")
        if detname is not None:
            if isinstance(detname, str):
                self.detname = detname
            else:
                raise TypeError("detname must be of type str")
        if scantype is not None:
            if isinstance(scantype, str):
                self.scantype = scantype
            else:
                raise TypeError("scantype must be of type str")
        if serial_number is not None:
            if isinstance(serial_number, str):
                self.serial_number = serial_number
            else:
                raise TypeError("serial_number must be of type str")
        if alg_name is not None:
            if isinstance(alg_name, str):
                self.alg_name = alg_name
            else:
                raise TypeError("alg_name must be of type str")
        if alg_version is not None:
            if isinstance(alg_version, list):
                self.alg_version = alg_version
            else:
                raise TypeError("alg_version must be of type list")

        self.seq_ctl = None
        if seq_ctl is not None:
            if not isinstance(seq_ctl[0], str):
                raise TypeError("seq_ctl[0] must be of type str")
            if not isinstance(seq_ctl[1], int):
                raise TypeError("seq_ctl[1] must be of type int")
            if len(seq_ctl) > 2 and not isinstance(seq_ctl[2], str):
                raise TypeError("seq_ctl[2] must be of type str")
            self.seq_ctl = seq_ctl

        return ({}, {})

    def stage(self):
        self._change_state(DaqState.CONNECTED)
        return [self]

    def unstage(self):
        self._change_state(DaqState.CONNECTED)
        return [self]
