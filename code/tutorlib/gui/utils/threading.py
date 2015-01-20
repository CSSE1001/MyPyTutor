from threading import Thread

from tutorlib.gui.utils.root import get_root_widget


def exec_sync(f, args=(), kwargs=None, sleep_time=1e-2):
    """
    Execute the given function synchronously on a background thread.

    The main thread will wake every sleep_time in order to process UI events.

    Blocks until the given function returns.

    """
    root = get_root_widget()

    th = Thread(target=f, args=args, kwargs=kwargs)
    th.start()

    while 1:
        th.join(sleep_time)
        if not th.is_alive():
            break

        root.update()
        root.update_idletasks()


def exec_async(f, args=(), kwargs=None):
    """
    Execute the given function asynchronously on a background thread.

    Included for API compatibility with exec_sync.

    Returns immediately.

    """
    th = Thread(target=f, args=args, kwargs=kwargs)
    th.start()
