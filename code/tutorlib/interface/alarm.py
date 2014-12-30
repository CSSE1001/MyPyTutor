from threading import Thread
import _thread
import time


class Alarm(Thread):
    """
    An alarm for setting a timeout on user code execution.

    Attributes:
      secs (float): The time, in seconds, to sleep (before firing the alarm).
      do_interrupt (bool): Whether or not the alarm should fire after the
          sleep time has elapsed.

    """
    def __init__(self, secs):
        """
        Initialise a new Alarm object.

        Args:
          secs (float): The time, in seconds, to sleep (before firing the alarm).

        """
        self.secs = secs
        self.do_interrupt = True

        super().__init__()

    def run(self):
        """
        Sleep for `.secs` seconds, then, if the alarm has not been cancelled,
        interrupt the main thread.

        """
        time.sleep(self.secs)
        if self.do_interrupt:
            _thread.interrupt_main()

    def stop_interrupt(self):
        """
        Cancel the alarm.

        """
        self.do_interrupt = False
