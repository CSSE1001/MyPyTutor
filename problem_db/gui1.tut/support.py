def _get_window():
    # something is going on with exec which is causing _get_window not to have
    # a reference to _TestWindow (even if defined without an underscore) when
    # it is defined at global scope
    # I don't have time to track down the specific issue right now, so I'm
    # going to take the lazy route out, and just nest it
    import tkinter as tk

    class _TestWindow(tk.Toplevel):
        def __init__(self, master, title):
            super().__init__(master)

            self.configure(borderwidth=5)
            self.geometry("400x200+30+30")
            self.resizable(height=tk.FALSE, width=tk.FALSE)
            self.protocol("WM_DELETE_WINDOW", self.ok)
            self.title(title)

            frame_main = tk.Frame(self)
            frame_main.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)
            tk.Label(
                frame_main,
                text="Your layout should appear in the frame below",
            ).pack()

            self.frame_problem = tk.Frame(
                frame_main,
                borderwidth=2,
                relief=tk.SUNKEN,
                bg="#ffffaa",
            )
            self.frame_problem.pack(fill=tk.BOTH, expand=tk.TRUE)

            frame_buttons = tk.Frame(self)
            frame_buttons.pack(fill=tk.X)

            self.btn_ok = tk.Button(
                frame_buttons,
                text='Close',
                command=self.ok,
            )
            self.btn_ok.pack()

            self.btn_ok.focus_set()
            self.bind('<Return>', self.ok)
            self.bind('<Escape>', self.ok)

        def ok(self, event=None):
            self.destroy()

    tw = _TestWindow(None, 'Layout')  # no master: root window
    return tw, tw.frame_problem