from abc import ABCMeta, abstractmethod
import string
import tkinter as tk


MENU_STRUCTURE = [
    ('Problems', [
        ('Next Tutorial', 'N', 'next'),
        ('Previous Tutorial', 'P', 'previous'),
    ]),
    ('Online', [
        ('Login', None, None),
        ('Logout', None, None),
        (None, None, None),
        ('Submit Answer', 'F6', 'submit'),
        ('Show Submissions', None, 'submissions'),
    ]),
    ('Preferences', [
        ('Configure Tutor Fonts', None, 'fonts'),
        ('Configure Tutorial Folder', None, 'tutorial_directory'),
        ('Configure Answers Folder', None, 'answers_directory'),
        (None, None, None),
        ('Set As Default Tutorial', None, 'set_default'),
        ('Add New Tutorial', None, 'add_tutorial'),
        ('Remove Current Tutorial', None, 'remove_current_tutorial'),
    ]),
    ('Feedback', [
        ('Problem Feedback', None, 'problem'),
        ('General Feedback', None, 'general'),
    ]),
    ('Help', [
        ('About MyPyTutor', None, 'about'),
        ('Help', 'F1', 'help'),
    ]),
]


class TutorialMenuDelegate(metaclass=ABCMeta):
    # problems
    @abstractmethod
    def change_problem(self, increment=None, problem=None):
        pass

    # online
    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def logout(self):
        pass

    @abstractmethod
    def submit(self):
        pass

    @abstractmethod
    def show_submissions(self):
        pass

    # preferences
    @abstractmethod
    def configure_fonts(self):
        pass

    @abstractmethod
    def change_tutorial_directory(self):
        pass

    @abstractmethod
    def change_answers_directory(self):
        pass

    @abstractmethod
    def set_as_default_tutorial(self):
        pass

    @abstractmethod
    def add_tutorial(self):
        pass

    @abstractmethod
    def remove_current_tutorial(self):
        pass

    # feedback
    @abstractmethod
    def feedback(self, problem_feedback=False):
        pass

    # help
    @abstractmethod
    def show_help_dialog(self):
        pass

    @abstractmethod
    def show_about_dialog(self):
        pass


class TutorialMenu(tk.Menu):
    DYNAMIC_PROBLEMS_MENU = 'Problems'

    def __init__(self, master, delegate=None, structure=MENU_STRUCTURE):
        super().__init__(master)

        assert delegate is None or isinstance(delegate, TutorialMenuDelegate)
        self.delegate = delegate

        self._structure = structure
        self._tutorial_package = None

        for submenu_name, submenu_entries in self._structure:
            submenu = tk.Menu(self, tearoff=tk.FALSE)
            self.add_cascade(label=submenu_name, menu=submenu)

            if submenu_name == TutorialMenu.DYNAMIC_PROBLEMS_MENU:
                submenu.config(postcommand=self.build_dynamic_problems_menu)
                self._dynamic_problems_menu = submenu
                continue

            for entry_name, entry_hotkey, entry_cb_name in submenu_entries:
                self._add_static_entry(
                    submenu,
                    submenu_name,
                    entry_name,
                    entry_hotkey,
                    entry_cb_name
                )

    def _add_static_entry(self, submenu, submenu_name, entry_name,
                entry_hotkey, entry_cb_name):
        if entry_name is None:
            submenu.add_separator()
            return

        if entry_cb_name is None:
            entry_cb_name = entry_name

        cb_name = '{}_{}'.format(submenu_name, entry_cb_name)
        cb_name = cb_name.lower()
        valid_chars = string.ascii_lowercase + '_'
        assert all(c in valid_chars for c in cb_name), \
            'Invalid callback name: {}'.format(cb_name)

        # remember that we need to put a closure around the callback
        # name to make python capture it by value (cf by reference)
        callback = (lambda n=cb_name: lambda: self.callback(n))()

        submenu.add_command(label=entry_name, command=callback)

        # TODO: entry_hotkey
        # TODO: need to treat as both accellerator and binding (eg F6)

    def set_tutorial_package(self, tutorial_package):
        self._tutorial_package = tutorial_package

    def callback(self, name):
        if self.delegate is None:
            return

        method_name = 'menu_{}'.format(name)
        method = getattr(self, method_name, None)

        if method is not None:
            return method()

        return self.generic_menu_callback(name)

    def problem_callback(self, tutorial):
        self.delegate.change_problem(problem=tutorial)

    def build_dynamic_problems_menu(self):
        # remove existing entries
        self._dynamic_problems_menu.delete(0, tk.END)

        # add the static entries
        menu_name = TutorialMenu.DYNAMIC_PROBLEMS_MENU

        try:
            static_entries = next(
                sub for name, sub in self._structure if name == menu_name
            )
        except StopIteration:
            raise AssertionError('Could not find dynamic menu')

        for name, hotkey, cb_name in static_entries:
            self._add_static_entry(
                self._dynamic_problems_menu,
                TutorialMenu.DYNAMIC_PROBLEMS_MENU,
                name,
                hotkey,
                cb_name,
            )

        # add the dynamic entries
        if self._tutorial_package is None:
            return

        for problem_set in self._tutorial_package.problem_sets:
            submenu = tk.Menu(self._dynamic_problems_menu, tearoff=tk.FALSE)
            self._dynamic_problems_menu.add_cascade(
                label='{}: {}'.format(problem_set.date, problem_set.name),
                menu=submenu,
            )

            for tutorial in problem_set:
                # again, close over cb var
                cb = (lambda t=tutorial: lambda: self.problem_callback(t))()
                submenu.add_command(label=tutorial.name, command=cb)

    ## TutorialMenuDelegate callbacks
    def generic_menu_callback(self, name):
        raise AssertionError('No matching menu callback for {}'.format(name))

    def menu_problems_next(self):
        self.delegate.change_problem(increment=1)

    def menu_problems_previous(self):
        self.delegate.change_problem(increment=-1)

    def menu_online_login(self):
        self.delegate.login()

    def menu_online_logout(self):
        self.delegate.logout()

    def menu_online_submit(self):
        self.delegate.submit()

    def menu_online_submissions(self):
        self.delegate.show_submissions()

    def menu_preferences_fonts(self):
        self.delegate.configure_fonts()

    def menu_preferences_tutorial_directory(self):
        self.delegate.change_tutorial_directory()

    def menu_preferences_answers_directory(self):
        self.delegate.change_answers_directory()

    def menu_preferences_set_default(self):
        self.delegate.set_as_default_tutorial()

    def menu_preferences_add_tutorial(self):
        self.delegate.add_tutorial()

    def menu_preferences_remove_current_tutorial(self):
        self.delegate.remove_current_tutorial()

    def menu_feedback_problem(self):
        self.delegate.feedback(problem_feedback=True)

    def menu_feedback_general(self):
        self.delegate.feedback(problem_feedback=False)

    def menu_help_about(self):
        self.delegate.show_about_dialog()

    def menu_help_help(self):
        self.delegate.show_help_dialog()
