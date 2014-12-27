from threading import Thread
import _thread
import time


# An alarm for setting a timeout on user code execution.
class Alarm(Thread):
    def __init__(self, secs):
        self.secs = secs
        self.do_interrupt = True

        super().__init__()

    def run(self):
        time.sleep(self.secs)
        if self.do_interrupt:
            _thread.interrupt_main()

    def stop_interrupt(self):
        self.do_interrupt = False
