import os
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox

from tutorlib.config.configuration import load_config
from tutorlib.editor.editor_window import TutorEditor
from tutorlib.gui.font_chooser import FontChooser
from tutorlib.gui.menu import TutorialMenuDelegate, TutorialMenu
from tutorlib.gui.output import AnalysisOutput, TestOutput
from tutorlib.interface.problems import TutorialPackage
from tutorlib.interface.tutorial_interface import TutorialInterface
from tutorlib.interface.web_api import WebAPI
import tutorlib.Tutorial as tut_tutorial  # TODO: fix stupid name


class TutorialApp(TutorialMenuDelegate):
    def __init__(self, master):
        #### Set up the window
        master.title('MyPyTutor')
        master.protocol("WM_DELETE_WINDOW", self.close)

        #### Set up our menu
        self.menu = TutorialMenu(master, delegate=self)
        master.config(menu=self.menu)

        #### Set up local variables
        ## Important top-level vars
        self.master = master
        self.cfg = load_config()

        ## Vars with side effects
        self._select_tutorial_package(self.cfg.tutorials.default)

        ## Objects
        self.interface = TutorialInterface()
        self.web_api = WebAPI()

        ## Optionals / property bases
        self.current_tutorial = None
        self._editor = None

        #### Create GUI Widgets
        ## Top Frame
        top_frame = tk.Frame(master)
        top_frame.pack(fill=tk.BOTH, expand=tk.TRUE)

        ## Tutorial (html display of tutorial problem)
        self.tut = tut_tutorial.Tutorial(
            top_frame,
            (self.cfg.font.name, self.cfg.font.size),
            self.cfg.window_sizes.problem
        )
        self.tut.pack(fill=tk.BOTH, expand=tk.TRUE)

        ## Short Problem Description
        self.short_description = tk.Label(top_frame, fg='blue')
        self.short_description.pack(fill=tk.X)

        ## Toolbar (hints, login status etc)
        #self.toolbar = Toolbar(self, top_frame)
        #self.toolbar.pack(fill=tk.X)

        ## Test Output
        self.test_output = TestOutput(
            top_frame,
            self.cfg.font.size,
            self.cfg.window_sizes.output,
        )
        self.test_output.pack(fill=tk.BOTH, expand=0)

        ## Analysis Output
        self.analysis_output = AnalysisOutput(
            top_frame,
            self.cfg.font.size,
            self.cfg.window_sizes.analysis,
        )
        self.analysis_output.pack(fill=tk.BOTH, expand=0)

    ## Properties
    @property
    def editor(self):
        if self._editor is None:
            self._editor = TutorEditor(self, root=self.master, online=False)
            ## TODO: fix online
        return self._editor

    ## Private methods
    def _select_tutorial_package(self, package_name):
        options = getattr(self.cfg, package_name)
        self.tutorial_package = TutorialPackage(options)

        # update menu
        self.menu.set_tutorial_package(self.tutorial_package)

    ## General callbacks
    def close(self, evt=None):
        self.master.destroy()

    ## TutorialMenuDelegate
    # problems
    def change_problem(self, increment=None, problem=None):
        if increment is not None:
            if increment < 0:
                f = self.tutorial_package.previous
                increment = -increment
            else:
                f = self.tutorial_package.next

            problem = self.current_tutorial

            for _ in range(increment):
                problem = f(self.current_tutorial)

        ## TODO: actual selection
        if self.editor.maybesave() == 'cancel':  # TODO: magic string
            return

        self.current_tutorial = problem

        self.tut.add_text(self.current_tutorial.description)

        answer_path = os.path.join(
            self.tutorial_package.options.ans_dir,
            '_'.join(self.current_tutorial.name.split()) + '.py'
        )
        self.editor.reset(answer_path, self.current_tutorial.preload_code_text)

    # online
    def login(self):
        if not self.web_api.login():
            tkmessagebox.showerror(
                'Login failed',
                'Please check your credentials and try again.  ' \
                'If the problem persists, check your internet connection.  ' \
                'Some functionality (such as submitting answers) will be ' \
                'unavailable until you log in successfully.'
            )

    def logout(self):
        self.web_api.logout()

    def submit(self):
        if not self.web_api.is_logged_in() or self.login():
            return

        if self.run_tests():
            self.web_api.submit(self.tutorial)

    def show_submissions(self):
        if not self.web_api.is_logged_in() or self.login():
            return

        submissions = self.web_api.get_submissions()
        # TODO: display submissions

    # preferences
    def configure_fonts(self):
        font_chooser = FontChooser(
            self.master, self, (self.cfg.font.name, self.cfg.font.size)
        )
        self.cfg.font.name, self.cfg.font.size = font_chooser.result

        self.update_fonts()

    def _ask_for_directory(self, initial_dir=None, prompt='Choose Directory'):
        if initial_dir is None or not os.path.exists(initial_dir):
            initial_dir = os.path.expanduser('~')

        return tkfiledialog.askdirectory(title=prompt, initialdir=initial_dir)

    def change_tutorial_directory(self):
        directory = self._ask_for_directory(
            prompt='Choose Tutorial Folder: {}'.format(self.current_tut_name),
            initial_dir=self.current_tut_options.tut_dir,
        )

    def change_answers_directory(self):
        pass

    def set_as_default_tutorial(self):
        pass

    def add_tutorial(self):
        pass

    def remove_current_tutorial(self):
        pass

    # feedback
    def feedback(self, problem_feedback=False):
        pass

    # help
    def show_help_dialog(self):
        pass

    def show_about_dialog(self):
        pass
