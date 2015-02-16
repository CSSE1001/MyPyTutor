from abc import ABCMeta, abstractmethod
import string
import tkinter as tk

from tutorlib.gui.utils.root import get_root_widget
from tutorlib.interface.web_api import WebAPI


MENU_STRUCTURE = [
    ('Problems', [
        ('Next Tutorial', ['N', 'n'], 'next'),
        ('Previous Tutorial', ['P', 'p'], 'previous'),
    ]),
    ('Online', [
        ('Login', None, None),
        ('Logout', None, None),
        (None, None, None),
        ('Submit Answer', ['<F6>'], 'submit'),
        ('Show Submissions', None, 'submissions'),
        (None, None, None),
        ('Synchronise Solutions', None, 'sync'),
    ]),
    ('Tools', [
        ('Visualise Code', None, 'visualise'),
        ('Open Interpreter', None, 'interpreter'),
    ]),
    ('Preferences', [
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
        ('Help', ['<F1>'], 'help'),
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

    @abstractmethod
    def synchronise(self):
        pass

    # tools
    @abstractmethod
    def show_visualiser(self):
        pass

    @abstractmethod
    def reload_interpreter(self):
        pass

    # preferences
    @abstractmethod
    def change_tutorial_directory(self):
        pass

    @abstractmethod
    def change_answers_directory(self):
        pass

    @abstractmethod
    def set_as_default_package(self):
        pass

    @abstractmethod
    def add_tutorial_package(self):
        pass

    @abstractmethod
    def remove_current_tutorial_package(self):
        pass

    @abstractmethod
    def change_tutorial_package(self, package_name):
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
    DYNAMIC_TUTORIAL_PACKAGES_MENU = 'Preferences'

    def __init__(self, master, delegate=None, structure=MENU_STRUCTURE):
        super().__init__(master)

        assert delegate is None or isinstance(delegate, TutorialMenuDelegate)
        self.delegate = delegate

        self._structure = structure
        self._selected_tutorial_package = None
        self._tutorial_package_names = None
        self._selected_tutorial_package_name_var = tk.StringVar()
        self._submissions = {}

        for submenu_name, submenu_entries in self._structure:
            submenu = tk.Menu(self, tearoff=tk.FALSE)
            self.add_cascade(label=submenu_name, menu=submenu)

            if submenu_name == TutorialMenu.DYNAMIC_PROBLEMS_MENU:
                submenu.config(postcommand=self.build_dynamic_problems_menu)
                self._dynamic_problems_menu = submenu
                continue
            elif submenu_name == TutorialMenu.DYNAMIC_TUTORIAL_PACKAGES_MENU:
                submenu.config(
                    postcommand=self.build_dynamic_tutorial_packages_menu
                )
                self._dynamic_tutorial_packages_menu = submenu
                continue

            for entry_name, entry_bindings, entry_cb_name in submenu_entries:
                self._add_static_entry(
                    submenu,
                    submenu_name,
                    entry_name,
                    entry_bindings,
                    entry_cb_name
                )

    def _add_static_entry(self, submenu, submenu_name, entry_name,
                entry_bindings, entry_cb_name):
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
        callback = (lambda n=cb_name: lambda evt=None: self.callback(n))()

        # add the callback to the menu
        kwargs = {'accelerator': entry_bindings[0]} if entry_bindings else {}
        submenu.add_command(label=entry_name, command=callback, **kwargs)

        # if there are any bindings, set them on the root window
        if entry_bindings:  # get_root_widget could take non-trivial time
            root = get_root_widget(submenu)

            for binding in entry_bindings:
                root.bind(binding, callback)  # NOT bind_all - idlelib hates it

    def set_selected_tutorial_package(self, tutorial_package):
        self._selected_tutorial_package = tutorial_package
        self._selected_tutorial_package_name_var.set(tutorial_package.name)

    def set_tutorial_packages(self, package_names):
        self._tutorial_package_names = package_names

    def set_submissions(self, submissions):
        self._submissions = submissions

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

    def tutorial_package_callback(self, package_name):
        self.delegate.change_tutorial_package(package_name)

    def _prepare_dynamic_menu(self, menu, menu_name):
        # remove existing entries
        menu.delete(0, tk.END)

        # get the static entries
        try:
            static_entries = next(
                sub for name, sub in self._structure if name == menu_name
            )
        except StopIteration:
            raise AssertionError('Could not find dynamic menu')

        # add the stataic entries
        for name, hotkey, cb_name in static_entries:
            self._add_static_entry(menu, menu_name, name, hotkey, cb_name)

    def build_dynamic_problems_menu(self):
        self._prepare_dynamic_menu(
            self._dynamic_problems_menu, TutorialMenu.DYNAMIC_PROBLEMS_MENU
        )

        # add the dynamic entries
        if self._selected_tutorial_package is None:
            return

        for problem_set in self._selected_tutorial_package.problem_sets:
            submenu = tk.Menu(self._dynamic_problems_menu, tearoff=tk.FALSE)
            self._dynamic_problems_menu.add_cascade(
                label='{}: {}'.format(problem_set.date, problem_set.name),
                menu=submenu,
            )

            for i, tutorial in enumerate(problem_set):
                # work out whether this tutorial has been submitted
                status = self._submissions.get(tutorial, WebAPI.MISSING)
                color = {
                    WebAPI.OK: 'blue',
                    WebAPI.LATE: 'orange',
                    # WebAPI.MISSING is *intentionally* absent - see below
                }.get(status)

                # again, close over cb var
                cb = (lambda t=tutorial: lambda: self.problem_callback(t))()
                submenu.add_command(label=tutorial.name, command=cb)

                # we can't use 'black' as the default on OS X, as the correct
                # default color depends on the user's color scheme
                # a similar problem exists on windows and linux
                # our solution is to only config the color for other statuses
                if color is not None:
                    submenu.entryconfig(i, foreground=color)

    def build_dynamic_tutorial_packages_menu(self):
        self._prepare_dynamic_menu(
            self._dynamic_tutorial_packages_menu,
            TutorialMenu.DYNAMIC_TUTORIAL_PACKAGES_MENU,
        )

        # add the dynamic entries
        if self._tutorial_package_names is None:
            return

        submenu = tk.Menu(
            self._dynamic_tutorial_packages_menu,
            tearoff=tk.FALSE,
        )
        self._dynamic_tutorial_packages_menu.add_cascade(
            label='Select Tutorial Package',
            menu=submenu,
        )

        for package_name in self._tutorial_package_names:
            # again, close over cb var
            cb = (lambda n=package_name: \
                      lambda: self.tutorial_package_callback(n))()

            submenu.add_radiobutton(
                label=package_name,
                variable=self._selected_tutorial_package_name_var,
                command=cb,
            )

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

    def menu_online_sync(self):
        self.delegate.synchronise()

    def menu_tools_visualise(self):
        self.delegate.show_visualiser()

    def menu_tools_interpreter(self):
        self.delegate.reload_interpreter()

    def menu_preferences_tutorial_directory(self):
        self.delegate.change_tutorial_directory()

    def menu_preferences_answers_directory(self):
        self.delegate.change_answers_directory()

    def menu_preferences_set_default(self):
        self.delegate.set_as_default_package()

    def menu_preferences_add_tutorial(self):
        self.delegate.add_tutorial_package()

    def menu_preferences_remove_current_tutorial(self):
        self.delegate.remove_current_tutorial_package()

    def menu_feedback_problem(self):
        self.delegate.feedback(problem_feedback=True)

    def menu_feedback_general(self):
        self.delegate.feedback(problem_feedback=False)

    def menu_help_about(self):
        self.delegate.show_about_dialog()

    def menu_help_help(self):
        self.delegate.show_help_dialog()
