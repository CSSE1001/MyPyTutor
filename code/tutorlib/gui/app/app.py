import os
import tkinter as tk
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox

from tutorlib.config.configuration \
        import add_tutorial, load_config, save_config
from tutorlib.gui.app.menu import TutorialMenuDelegate, TutorialMenu
from tutorlib.gui.app.output import AnalysisOutput, TestOutput
from tutorlib.gui.app.tutorial import TutorialFrame
from tutorlib.gui.editor.editor_window import TutorEditor
from tutorlib.gui.dialogs.about import TutAboutDialog
from tutorlib.gui.dialogs.feedback import FeedbackDialog
from tutorlib.gui.dialogs.font_chooser import FontChooser
from tutorlib.gui.dialogs.help import HelpDialog
from tutorlib.interface.problems import TutorialPackage
from tutorlib.interface.tests import StudentCodeError, run_tests
from tutorlib.interface.web_api import WebAPI


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
        self.web_api = WebAPI()

        ## Optionals / property bases
        self.current_tutorial = None
        self._editor = None

        #### Create GUI Widgets
        ## Top Frame
        top_frame = tk.Frame(master)
        top_frame.pack(fill=tk.BOTH, expand=tk.TRUE)

        ## Tutorial (html display of tutorial problem)
        self.tutorial_frame = TutorialFrame(
            top_frame,
            (self.cfg.font.name, self.cfg.font.size),
            self.cfg.window_sizes.problem
        )
        self.tutorial_frame.pack(fill=tk.BOTH, expand=tk.TRUE)

        ## Short Problem Description
        self.short_description = tk.Label(top_frame, fg='blue')
        self.short_description.pack(fill=tk.X)

        ## Toolbar (hints, login status etc)
        toolbar = tk.Frame(top_frame, bg='grey80')
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.hint_button = tk.Button(
            toolbar, text='Next Hint', command=self._next_hint
        )

        self.online_status = tk.Label(
            toolbar, relief=tk.SUNKEN
        )
        self.online_status.pack(
            side=tk.RIGHT, pady=3, ipady=2, padx=2, ipadx=2
        )
        self._set_online_status(logged_in_user=None)

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

    @property
    def answer_path(self):
        return os.path.join(
            self.tutorial_package.options.ans_dir,
            '_'.join(self.current_tutorial.name.split()) + '.py'
        )

    ## Private methods
    def _select_tutorial_package(self, package_name):
        if package_name is None:
            # we can't change to a non-existent package, so we will need to
            # add a new one
            self.add_tutorial()
            return

        options = getattr(self.cfg, package_name)
        self.tutorial_package = TutorialPackage(options)

        # update menu
        self.menu.set_tutorial_package(self.tutorial_package)

    def _next_hint(self):
        hint = self.current_tutorial.next_hint

        if hint is not None:
            html = '<p>\n<b>Hint: </b>{}'.format(hint)
            self.tutorial_frame.show_hint(html)

            # TODO: show/hide hints button

    def _set_online_status(self, logged_in_user=None):
        if logged_in_user is None:
            self.online_status.config(text='Status: Not Logged In')
        else:
            self.online_status.config(
                text='Status: Logged in as {}'.format(logged_in_user)
            )

    def _ask_for_directory(self, initial_dir=None, prompt='Choose Directory'):
        if initial_dir is None or not os.path.exists(initial_dir):
            initial_dir = os.path.expanduser('~')

        return tkfiledialog.askdirectory(title=prompt, initialdir=initial_dir)

    ## General callbacks
    def close(self, evt=None):
        # only close if the editor indicates that it's safe to do so
        # (this will prompt the student to save their code)
        if self.editor.close() == 'yes':  # TODO: magic strings
            self.logout()
            save_config(self.cfg)

            self.master.destroy()

    ## Public-ish methods
    def run_tests(self):
        code_text = self.editor.get_text()

        # run the tests
        # if the student code cannot be parsed, highlight the problem line
        try:
            tester, analyser = run_tests(self.current_tutorial, code_text)
        except StudentCodeError as e:
            self.editor.error_line(e.linenum)
            return False

        # show the results on the UI
        self.test_output.set_test_results(tester.results)
        self.analysis_output.set_analyser(analyser)

        # return whether the code passed
        return tester.passed and not analyser.errors

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

        if self.editor.maybesave() == 'cancel':  # TODO: magic string
            return

        # set the current tutorial
        self.current_tutorial = problem

        # show the problem text and description
        self.tutorial_frame.add_text(self.current_tutorial.description)
        self.short_description.config(
            text=self.current_tutorial.short_description
        )

        # set up the editor
        self.editor.reset(
            self.answer_path, self.current_tutorial.preload_code_text
        )
        self.editor.undo.reset_undo()

        # set up the hints toolbar
        if self.current_tutorial.hints:
            self.hint_button.pack(side=tk.LEFT)
        else:
            self.hint_button.pack_forget()

        # run the tests
        # this will fill out the results and static analysis sections
        self.run_tests()

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
            return False

        self._set_online_status(logged_in_user=self.web_api.user)
        return True

    def logout(self):
        self.web_api.logout()

        self._set_online_status(logged_in_user=None)

    def submit(self):
        if not self.web_api.is_logged_in() or not self.login():
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

    def change_tutorial_directory(self):
        directory = self._ask_for_directory(
            prompt='Choose Tutorial Folder: {}'.format(
                    self.current_tutorial.name
                ),
            initial_dir=self.current_tutorial.options.tut_dir,
        )

        if directory:
            # .current_tutorial.options is bound to cfg, so will change it
            self.current_tutorial.options.tut_dir = directory
            self._select_tutorial_package(self.current_tutorial.name)

    def change_answers_directory(self):
        directory = self._ask_for_directory(
            prompt='Choose Answers Folder: {}'.format(
                    self.current_tutorial.name
                ),
            initial_dir=self.current_tutorial.options.ans_dir,
        )

        if directory:
            # .current_tutorial.options is bound to cfg, so will change it
            self.current_tutorial.options.ans_dir = directory
            self.editor.set_filename(self.answer_path)
            # TODO: relocate answers?

    def set_as_default_tutorial(self):
        pass

    def add_tutorial(self):
        # if we don't have a default tutorial, we should add this one as the
        # default and then switch to it
        as_default = self.cfg.tutorials.default is None
        add_tutorial(self.cfg, as_default=as_default)

        if as_default:
            self._select_tutorial_package(self.cfg.tutorials.default)

    def remove_current_tutorial(self):
        pass

    # feedback
    def feedback(self, problem_feedback=False):
        if problem_feedback:
            FeedbackDialog(
                self.master,
                'Problem Feedback: {}'.format(self.current_tutorial.name),
                self.current_tutorial.name,
                self.editor.get_text()
            )
        else:
            FeedbackDialog(self.master, 'General Feedback')

    # help
    def show_help_dialog(self):
        HelpDialog(self.master, 'Help')

    def show_about_dialog(self):
        TutAboutDialog(self.master, 'About MyPyTutor')
