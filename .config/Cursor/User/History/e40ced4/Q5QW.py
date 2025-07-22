import psutil
from PySide6.QtCore import QObject, Property, Signal, Slot

class SystemInfo(QObject):
    uptimeChanged = Signal()
    memoryChanged = Signal()

    def __init__(self):
        super().__init__()
        self._uptime = self.get_uptime()
        self._memory = self.get_memory()

    def get_uptime(self):
        return int(psutil.boot_time())

    def get_memory(self):
        mem = psutil.virtual_memory()
        return f"{mem.used // (1024*1024)}MB / {mem.total // (1024*1024)}MB"

    @Property(int, notify=uptimeChanged)
    def uptime(self):
        return self.get_uptime()

    @Property(str, notify=memoryChanged)
    def memory(self):
        return self.get_memory() 