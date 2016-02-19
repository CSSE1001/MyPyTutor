from functools import partial
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as tkfiledialog
import os

import tkinter.messagebox as tkmessagebox
import datetime, time, shutil

from tutorlib.config.attempts import TutorialAttempts
from tutorlib.config.configuration \
        import add_tutorial, load_config, save_config
from tutorlib.gui.app.menu import TutorialMenuDelegate, TutorialMenu
from tutorlib.gui.app.output \
        import AnalysisOutput, TestOutput, TestOutputDelegate
from tutorlib.gui.app.tutorial import TutorialFrame
from tutorlib.gui.dialogs.about import TutAboutDialog
from tutorlib.gui.dialogs.feedback import FeedbackDialog
from tutorlib.gui.dialogs.progress import ProgressPopup
from tutorlib.gui.dialogs.submissions import SubmissionsDialog, SubmissionsSelectDialog
from tutorlib.gui.editor.delegate import TutorEditorDelegate
from tutorlib.gui.editor.editor_window import TutorEditor
from tutorlib.utils.decorators import skip_if_attr_none
import tutorlib.utils.messagebox as tkmessagebox
from tutorlib.utils.threading import exec_sync
from tutorlib.interface.interpreter import Interpreter
from tutorlib.interface.problems import TutorialPackage, TutorialPackageError
from tutorlib.interface.tests import run_tests
from tutorlib.interface.web_api import WebAPI, WebAPIError
from tutorlib.online.sync import SyncClient


VERSION = '3.0.10'


class TutorialApp(TutorialMenuDelegate, TutorEditorDelegate,
        TestOutputDelegate):
    """
    The main MyPyTutor application.

    Attributes:
      cfg (Namespace): The MyPyTutor configuration options.
      current_tutorial (Tutorial): The currently selected tutorial problem.
      interpreter (Interpreter): The interpreter used by MyPyTutor.
      tutorial_package (TutorialPackage): The selected tutorial package.
      web_api (WebAPI): The web API for the app.

    GUI Attributes:
      analysis_output (AnalysisOutput): The frame displaying the current static
          analysis results.
      editor (TutorEditor): The edit window (where students write their code).
      hint_button (Button): The button which, when clicked, causes the next
          hint to be displayed.
      master (tk.Wm): The base tk window that the app is displayed in.
      menu (TutorialMenu): The menubar.
      online_status (Label): The label showing whether the student is currently
          logged in (ie, authenticated).
      short_description (Label): The label containing the short description
          of the current tutorial problem.
      sync_client (SyncClient): The tutorial synchronisation client.
      test_output (TestOutput): The frame displaying the current test results.
      tutorial_attempts (TutorialAttempts): The number of attempts that the
        student has made at a tutorial problem.
      tutorial_frame (TutorialFrame): The frame which displays the tutorial
          problem and associated data, such as hints.

    """
    def __init__(self, master, web_api=None):
        assert web_api is None or web_api.is_logged_in, \
                'If a WebAPI instance is provided, it must be logged in'

        #### Set up the window
        master.title('MyPyTutor')
        master.protocol("WM_DELETE_WINDOW", self.close)

        #### Set up our menu
        self.menu = TutorialMenu(master, delegate=self)
        master.config(menu=self.menu)

        #### Set up local variables
        ## Optionals / property bases
        self.current_tutorial = None
        self._editor = None
        self._tutorial_package = None
        self._submissions = {}

        ## Important top-level vars
        self.master = master
        self.cfg = load_config()

        ## Vars with side effects
        self.tutorial_package = self.cfg.tutorials.default
        self.menu.set_tutorial_packages(self.cfg.tutorials.names)

        ## Objects
        self.attempts = TutorialAttempts()
        self.interpreter = Interpreter()

        if web_api is None:
            self.web_api = WebAPI(self._login_status_change)
            self.master.after(0, self.login)
        else:
            self.web_api = web_api
            self.web_api.listener = self._login_status_change

            # immediately perform the callback, assuming we've synced already
            self._login_status_change(logged_in=True, do_sync=False)

        self.sync_client = SyncClient(self.web_api)

        ## Purely private vars
        self._is_closing = False

        ## Finalise GUI Setup

        width = min(master.winfo_screenwidth(), self.cfg.resolution.width)
        height = min(master.winfo_screenheight(), self.cfg.resolution.height)
        master.geometry('{}x{}'.format(width, height))

        #### Create GUI Widgets
        ## Top Frame
        top_frame = ttk.Frame(master)
        top_frame.pack(fill=tk.BOTH, expand=tk.TRUE)

        ## Tutorial (html display of tutorial problem)
        self.tutorial_frame = TutorialFrame(
            top_frame,
        )
        self.tutorial_frame.pack(fill=tk.BOTH, expand=tk.TRUE)
        self.tutorial_frame.splash(version=VERSION)

        ## Short Problem Description
        self.short_description = ttk.Label(top_frame)  # TODO: sort out style
        self.short_description.pack()

        ## Toolbar (hints, login status etc)
        toolbar = ttk.Frame(top_frame)  # TODO: sort out style
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.hint_button = ttk.Button(
            toolbar, text='Next Hint', command=self._next_hint
        )

        self.online_status = ttk.Label(
            toolbar, relief=tk.SUNKEN
        )
        self.online_status.pack(
            side=tk.RIGHT, pady=3, ipady=2, padx=2, ipadx=2
        )
        self._set_online_status(logged_in_user=None)

        self.problem_status = ttk.Label(
            toolbar, relief=tk.SUNKEN
        )
        self.problem_status.pack(
            side=tk.RIGHT, pady=3, ipady=2, padx=2, ipadx=2
        )

        ## Test Output
        self.test_output = TestOutput(
            top_frame,
            self,
        )
        self.test_output.pack(fill=tk.X, expand=tk.FALSE)

        ## Analysis Output
        self.analysis_output = AnalysisOutput(
            top_frame,
        )
        self.analysis_output.pack(fill=tk.X, expand=tk.FALSE)

    ## Properties
    @property
    def editor(self):
        """
        Return a reference to the editor window.

        If the editor is not currently visible, accessing it via this property
        will create it and set it to visible.

        This behaviour is intended to permit lazy construction of the editor.

        Returns:
          The editor window (an instance of TutorEditor).
        """
        if self._editor is None:
            self._editor = TutorEditor(
                menu_delegate=self,
                editor_delegate=self,
                root=self.master,
            )
        return self._editor

    ## Private methods
    @property
    def tutorial_package(self):
        return self._tutorial_package

    @tutorial_package.setter
    def tutorial_package(self, package_name):
        """
        Select the tutorial package with the given name.

        If no name is provided, prompt the user to add a new tutorial.

        If a name is provided but the package cannot be loaded, display an
        error to the user but otherwise do nothing.
        This may leave the application in an inconsistent state.

        Warning: if no name is provided, prompting the user to add a new
        tutorial is performed *asynchronously*.  Because of this, if a value
        given to this setter could be null, the calling code *cannot* rely on
        tutorial_package having a valid value immediately after this function
        returns.  For example, the following code is *not safe*:

            self.tutorial_package = 'CSSE1001Tutorials' if rand() < 0.5 else ''
            print(self.tutorial_package.name)  # UNSAFE

        If the assigned value is '' in the above example, self.tutorial_package
        will not have a value until, at the earliest, *after* the next run of
        the GUI event loop (as that is when the user will be prompted to add
        a tutorial).

        In normal use, this should not pose a problem; the only time the
        assigned value should even potentially be the empty string is the very
        first time that MPT is run.

        Args:
          package_name (str): The name of the package to select.

        """
        if not package_name:
            # if no package is given, we want to try to add a new one
            # this will be the case the very first time MyPyTutor is launched
            # in that case, the Tk object (root) will not yet have entered
            # the main loop
            # attempting to display any tk widget before entering the main
            # loop will cause the application to suffer display errors on OS X
            # once it actually appears (see issue #49)
            # by deferring the add action, we can avoid this issue
            self.master.after(0, self.add_tutorial_package)
            return

        assert hasattr(self.cfg, package_name), \
                'Attempt to select unknown package: {}'.format(package_name)
        options = getattr(self.cfg, package_name)

        try:
            self._tutorial_package = TutorialPackage(package_name, options)
        except TutorialPackageError as e:
            tkmessagebox.showerror(
                'Invalid Tutorial Package',
                'Failed to load {}: {}'.format(package_name, e),
            )
            return

        # update menu
        self.menu.set_selected_tutorial_package(self.tutorial_package)

    def _next_hint(self):
        """
        Display the next hint.

        If there are no more hints to display, do nothing.

        """
        if not self.tutorial_frame.show_next_hint():
            self.hint_button.pack_forget()

    def _set_problem_status(self):
        status = self._submissions.get(
            self.current_tutorial,
        )
        strings = {
            WebAPI.OK: 'Yes',
            WebAPI.LATE: 'Late',
            WebAPI.MISSING: 'No',
            None: 'Unknown',
        }
        text = 'Submitted: {}'.format(strings[status])
        self.problem_status.config(text=text)

    def _set_online_status(self, logged_in_user=None):
        """
        Update the online status label.

        Args:
          logged_in_user (str, optional): The username of the student who is
              logged in.  Defaults to None, which indicates that the student
              has logged out.

        """
        if logged_in_user is None:
            self.online_status.config(text='Status: Not Logged In')
        else:
            self.online_status.config(
                text='Status: Logged in as {}'.format(logged_in_user)
            )

    def _ask_for_directory(self, initial_dir=None, prompt='Choose Directory'):
        """
        Display a tk filedialog which prompts the user to select a directory.

        Args:
          initial_dir (str, optional): The initial directory to display in the
              filedialog.  If initial_dir is not provided or does not exist,
              defaults to the user's home directory.
          prompt (str, optional): The prompt to display in the filedialog.
              Defaults to 'Choose Directory'.

        Returns:
          The result of tkfiledialog.askdirectory

        """
        if initial_dir is None or not os.path.exists(initial_dir):
            initial_dir = os.path.expanduser('~')

        return tkfiledialog.askdirectory(title=prompt, initialdir=initial_dir)

    def _display_web_api_error(self, ex):
        """
        Display the given WebAPIError to the user.

        Args:
          ex (WebAPIError): The error to display.

        """
        message = '{}\n\nDetailed error message:\n{}'.format(
            ex.message, ex.details
        )

        tkmessagebox.showerror(
            'Online Services Error',
            message
        )

    ## General callbacks
    def close(self, evt=None):
        """
        Close event for the TutorialApp.

        The app will only be closed if the .editor indicates that it is safe
        to do so (this will prompt the student to save their code).

        """
        # don't try to close more than once
        # this fixes errors when the user keeps hammering the close button
        if self._is_closing:
            return

        if self.editor.close() == tkmessagebox.YES:
            self._is_closing = True

            self.interpreter.kill()

            self.attempts.save()

            self.cfg.resolution.width = self.master.winfo_width()
            self.cfg.resolution.height = self.master.winfo_height()

            save_config(self.cfg)

            self.master.destroy()

    ## Public-ish methods
    @skip_if_attr_none('current_tutorial')
    def run_tests(self, try_to_submit=True, record_attempt=False):
        """
        Test and analyse the student code.

        If there is a compilation error in the student code, highlight the line
        of that error in the editor and return.

        Otherwise, update `.test_output` and `.analysis_output` with the
        results of the testing and analysis respectively.

        This method will also reload the interpreter with the tested code, so
        that students can play with it themselves.

        Args:
          try_to_submit (bool, optional): If True, attempt to submit the
            tutorial if the student's answer is correct.
        record_attempt (bool, optional): If True, record that the student has
            made an attempt at the icurrent problem.

        Returns:
          Whether the code passes the tests and the analysis.

          The code will pass iff it passes every test case *and* causes no
          analysis errors.
          The second requirement is important, as it helps to avoid 'cheat'
          solutions (such as using the `sum` function when instructed not to).

        """
        code_text = self.editor.get_text()

        # run the tests
        # if the student code cannot be parsed, highlight the problem line
        tester, analyser, error_line = run_tests(
            self.current_tutorial, code_text
        )

        if error_line is not None:
            self.highlight_error(error_line)

        # show the results on the UI
        self.test_output.set_test_results(tester.results)
        self.analysis_output.set_analyser(analyser)

        # return whether the code passed
        success = tester.passed and not analyser.errors

        previous_submission_status = self._submissions.get(
            self.current_tutorial, WebAPI.MISSING
        )

        # record an attempt if the user has not previously been successful
        # if the user is not logged in, assume that they have not been
        # successful; NB that this could cause inflation in some circumstances
        if record_attempt and success and (not self.web_api.is_logged_in \
                or previous_submission_status == WebAPI.MISSING):
            self.attempts.record_attempt(
                self.current_tutorial, self.tutorial_package
            )

        # try to submit if successful
        if success and try_to_submit:
            if self.web_api.is_logged_in:
                try:
                    response = self.web_api.submit_answer(
                        self.current_tutorial,
                        self.editor.get_text(),
                        self.attempts.num_attempts_for(
                            self.current_tutorial, self.tutorial_package
                        )
                    )
                    if response is not None:
                        self.master.after(0, self.update_submissions)
                except WebAPIError:
                    pass  # ignore: silently trying to submit
            else:
                if previous_submission_status == WebAPI.MISSING:
                    def _show_info_box():
                        tkmessagebox.showinfo(
                            'Correct!',
                            'Remember that you must log in and submit your ' \
                            'answer in order to receive any marks.'
                        )
                    self.master.after(0, _show_info_box)

        # reload the interpreter with the tested code
        if self.interpreter.is_alive:
            self.interpreter.reload(self.editor.get_text())

        return success

    ## TutorialMenuDelegate
    # problems
    @skip_if_attr_none('tutorial_package')
    def change_problem(self, increment=None, problem=None):
        """
        Change the tutorial problem.

        If the student currently has a problem open with unsaved changes, they
        will be prompted to save those changes.  If they choose to cancel,
        this function will return.

        Either `increment` or `problem` must be provided.  If `increment` is
        provided, it will be interpreted as an instruction to go to the problem
        `increment` after (or before) the current problem.  If `problem` is
        provided, that problem will be switched to directly.

        After the current problem is selected, the `.tutorial_frame`,
        `.short_description`,  and `.editor` are updated as appropriate.

        Tests are automatically run on the new tutorial.  As a side effect,
        both `.test_output` and `.analysis_output` will be updated.

        Args:
          increment (int, optional): The number of problems to skip, relative
              to the current problem.  An increment of 1 will select the next
              problem; -1 will select the previous problem.  Defaults to None.
          problem (Tutorial, optional): The problem to change to.  Defaults to
              None.  If `increment` is not provided, `problem` must be.

        """
        if self.editor.maybesave() == tkmessagebox.CANCEL:
            return

        if increment is not None:
            if increment < 0:
                f = self.tutorial_package.previous
                increment = -increment
            else:
                f = self.tutorial_package.next

            problem = self.current_tutorial

            for _ in range(increment):
                problem = f(self.current_tutorial)

        # set the current tutorial
        assert problem is not None
        self.current_tutorial = problem

        # show the problem text and description
        self.tutorial_frame.tutorial = self.current_tutorial
        self.short_description.config(
            text=self.current_tutorial.short_description
        )

        # set up the editor
        self.editor.reset(self.current_tutorial)
        self.editor.undo.reset_undo()

        # set up the hints toolbar
        if self.current_tutorial.hints:
            self.hint_button.pack(side=tk.LEFT)
        else:
            self.hint_button.pack_forget()

        # update the ui
        self._set_problem_status()

        # run the tests
        # this will fill out the results and static analysis sections
        self.run_tests()

    def _login_status_change(self, logged_in, do_sync=True):
        if do_sync:  # on login or logout
            callback = partial(self.synchronise, no_login=not logged_in)
            callback.__name__ = 'callback'
            self.master.after(0, callback)

        if logged_in:
            self.master.after(0, self.update_submissions)

    # online
    def login(self):
        """
        Attempt to log the student in to the MyPyTutor system.

        If the login fails, show the student an error message.

        If the login succeeds, set the online status appropriately.

        Returns:
          Whether the login attempt succeeded.

        """
        try:
            logged_in = self.web_api.login()
        except WebAPIError:
            tkmessagebox.showerror(
                'Login failed',
                'Please check your credentials and try again.  ' \
                'If the problem persists, check your internet connection.  ' \
                'Some functionality (such as submitting answers) will be ' \
                'unavailable until you log in successfully.'
            )
            logged_in = False

        self._set_online_status(
            logged_in_user=self.web_api.user if logged_in else None
        )
        return logged_in

    def logout(self):
        """
        Log the student out of the MyPyTutor system, and set the online status
        to reflect this.

        """
        self.web_api.logout()

        self._set_online_status(logged_in_user=None)

    @skip_if_attr_none('current_tutorial')
    def submit(self):
        """
        Submit the current tutorial problem.

        The student may only submit if logged on, and if their answer is
        correct (ie, if it passes all tests and raises no analysis errors).

        Attempting to submit will prompt the student to log on (if they are not
        already logged in), and will re-run the tests.

        """
        if not self.login():
            return

        if self.run_tests(try_to_submit=False):
            try:
                response = self.web_api.submit_answer(
                    self.current_tutorial,
                    self.editor.get_text(),
                    self.attempts.num_attempts_for(
                        self.current_tutorial, self.tutorial_package
                    ),
                )
            except WebAPIError as e:
                self._display_web_api_error(e)
                return

            if response is None:
                tkmessagebox.showinfo(
                    'Code Not Submitted',
                    'This tutorial problem has already been submitted.  ' \
                    'There is no need to submit more than once.'
                )
                return

            messages = {self.web_api.OK: 'Code submitted on time',
                        self.web_api.LATE: 'Code submitted late',
                        self.web_api.LATE_OK: 'Code submitted. You will not ' \
                            'receive a penalty for late submission.'}

            tkmessagebox.showinfo(
                'Submission Successful!',
                messages[response],
            )

            self.master.after(0, self.update_submissions)

    def update_submissions(self):
        """
        Get the latest submissions information for the user.

        The student must be logged on to show their submissions.  This method
        will prompt the student to login if necessary.

        If successful, this will update the menu with the submissions
        information.

        Returns:
          A dictionary mapping tutorials to the submission status if
          successful; None otherwise.

        """
        if not self.login():
            return None

        try:
            submissions = self.web_api.get_submissions(self.tutorial_package)
        except WebAPIError as e:
            self._display_web_api_error(e)
            return None

        # update the menu with the new submissions as well
        self.menu.set_submissions(submissions)

        self._submissions = submissions

        # update the problem status
        self._set_problem_status()

        return submissions

    @skip_if_attr_none('tutorial_package')
    def show_submissions(self):
        """
        Show the student their submission history.

        This will indicate which problems have been completed, and which
        still need to be done.

        """
        submissions = self.update_submissions()
        if submissions is None:
            return

        SubmissionsDialog(self.master, submissions, self.tutorial_package)

    @skip_if_attr_none('tutorial_package')
    def synchronise(self, suppress_popups=False, no_login=None):
        """
        Synchronise the tutorial answers.

        A tutorial will be downloaded from the server iff:
          * there is no local answer, but there is one on the server; or
          * the local and remote answers differ, but the remote one was
            modified after the local one.

        A tutorial will be uploaded to the server iff:
          * there is no answer on the server, but there is a local one; or
          * the local and remote answers differ, but the local one was modified
            at the same time as or before the one on the server.

        Args:
          suppress_popups (bool, optional): If True, do not show any popup
              messages.  This is intended to be used when the synchronisation
              is taking place as part of the close handler.  Defaults to False.
          no_login (bool, optional): If True, do not attempt to login; if the
              user is not logged in, exit immediately and silently.  Defaults
              to the same value as suppress_popups.

        """
        if no_login is None:
            no_login = suppress_popups

        # if we're not logged in, and we are told not to, or can't, then quit
        if not self.web_api.is_logged_in:
            if no_login or not self.login():
                return

        # start showing the progress popup
        popup = ProgressPopup()

        def _show_failure_message():
            tkmessagebox.showerror(
                'Could Not Synchronise Answer Code',
                'Please check that you are correctly logged in, ' \
                'and that your internet connection is active.'
            )

        def _show_success_message():
            tkmessagebox.showinfo(
                'Synchronisation Complete!',
                'Your answers have been successfully synchronised with the ' \
                'server.',
            )

        def _background_task():
            # certain methods used in the synchronisation process might throw
            # WebAPIError, so we want to wrap everything in an exception
            # handler
            # note that as this is on a background thread, we must not make
            # any UI calls
            try:
                success = self.sync_client.synchronise(self.tutorial_package)

                if not suppress_popups:
                    if success:
                        self.master.after(0, _show_success_message)
                    else:
                        self.master.after(0, _show_failure_message)
            except WebAPIError as e:
                if not suppress_popups:
                    self.master.after(0, self._display_web_api_error, e)
            finally:
                self.master.after(0, popup.destroy)

        # do this on a background thread
        exec_sync(_background_task)

    # tools
    @skip_if_attr_none('editor')
    def show_visualiser(self):
        """
        Open a web browser with the student's current code pre-loaded into the
        online visualiser tool.

        No login is necessary; the tool is publicly available.

        """
        self.web_api.visualise(self.editor.get_text())

    @skip_if_attr_none('editor')
    def show_interpreter(self):
        """
        Open the interpreter.

        """
        self.interpreter.reload(self.editor.get_text())

    #@skip_if_attr_none('editor')
    def backup(self):
        """
        Backup the user's data.

        """
        filename = self._backup()

    def _backup(self, filename=None, now=None, showMessage=True):
        """
        Backup the user's data.

        Args:
            filename:       The filename to backup to. If None, prompts users for one.
            now:            The time to use for generation of timestamp to suffix to the filename.
                            Not relevant if filename is not None.
            showMessage:    Determines whether to show a GUI success message or not once backup has been completed.

        """

        if now is None:
            now = time.time()

        if filename is None:
            timestamp = datetime.datetime.fromtimestamp(now).strftime('%Y-%m-%d %H-%M-%S')

            # Request filename from user
            filename = tkfiledialog.asksaveasfilename(
                defaultextension='.zip',
                filetypes=[('Zip Archives', '.zip'), ('All files', '.*')],
                initialfile="mpt-backup {timestamp}".format(timestamp=timestamp)
                )

        if not filename:
            return

        if filename.endswith('.zip'):
            filename = filename[:-4]

        # Create zipfile
        filename = shutil.make_archive(filename, 'zip', self.tutorial_package.options.ans_dir)

        if showMessage:
            tkmessagebox.showinfo("Backup complete!", "Your answers have been backed up successfully to {}".format(filename))

        return filename

    def process_submission_reset(self, problems, now=None):
        """
        Processes a user initiated submission reset.
        1. Clears local files
        2. Clears submissions on server
        3. Synchronizes attempts with server

        Args:
            problems: A list of tutorial problems to reset.
        """

        window = tk.Toplevel(self.master)
        tk.Label(window, text="Working").pack(anchor=tk.CENTER, padx=50, pady=50)
        window.grab_set()

        # 1. Clear local files
        for problem, problem_set in problems:
            if not problem.has_answer:
                # Skip problems that have no attempt recorded
                continue

            problem.clear_local_attempt()

        # 2. Clear submissions on server
        self.web_api.reset_answers([problem for problem, _ in problems])

        # 3. Synchronize attempts with server
        self.synchronise()

        window.grab_release()
        window.destroy()

        tkmessagebox.showinfo("Successfully Reset", "The submissions that you selected have been successfully reset.")

    def reset_submissions(self):
        """
        Allows a user to select some of their submissions to reset.
        """
        if self.current_tutorial and self.editor.maybesave() == tkmessagebox.CANCEL:
            return

        now = datetime.datetime.now()

        def done():
            self.master.after(0, self.update_submissions)

            if self.current_tutorial:
                self.editor.reset(self.current_tutorial)
                self.editor.undo.reset_undo()

        def process(output):
            self.process_submission_reset(output, now)

            done()

        # Check for backup first
        do_backup = tkmessagebox.askyesno(
            "Backup first?",
            "It is HIGHLY recommended to backup your answers before attempting to reset any of your submissions."
            "\n\n"
            "Would you like to backup now?"
        )

        if do_backup:
            self._backup(now=now)

        # Prompt user with list of submissions to reset
        dialog = SubmissionsSelectDialog(self.master, None, self.tutorial_package, text="Reset", command=process)

    # preferences
    @skip_if_attr_none('tutorial_package')
    def change_tutorial_directory(self):
        """
        Prompt to change the current tutorial directory.

        This is the directory that the tutorial problems are read from.

        If the tutorial directory is changed, reload the current tutorial
        package.  This may cause an error popup if the new directory is
        not valid.

        """
        directory = self._ask_for_directory(
            prompt='Choose Tutorial Folder: {}'.format(
                    self.tutorial_package.name
                ),
            initial_dir=self.tutorial_package.options.tut_dir,
        )

        if directory:
            # .current_tutorial.options is bound to cfg, so will change it
            self.tutorial_package.options.tut_dir = directory
            # force a reload of the tutorial package so that all tutorials
            # with a reference to the old directory are replaced
            self.tutorial_package = self.tutorial_package.name

    @skip_if_attr_none('tutorial_package')
    def change_answers_directory(self):
        """
        Prompt to change the current answers directory.

        This is the directory that the tutorial answers are written to.

        If the answers directory is changed, reload the current tutorial
        package.  This will update the `.answer_path` property on each tutorial
        object.  The `.current_tutorial` will then be updated to match this
        (so that it does not contain a reference to the old object).  Finally,
        the save path for the editor must also be updated.

        """
        directory = self._ask_for_directory(
            prompt='Choose Answers Folder: {}'.format(
                    self.tutorial_package.name
                ),
            initial_dir=self.tutorial_package.options.ans_dir,
        )

        if directory:
            # .current_tutorial.options is bound to cfg, so will change it
            self.tutorial_package.options.ans_dir = directory
            # force a reload of the tutorial package so that all tutorials
            # with a reference to the old directory are replaced
            self.tutorial_package = self.tutorial_package.name

            # need to update reference to Tutorial in new (reloaded) package
            # (but only if we actually have a tutorial open)
            if self.current_tutorial is None:
                return

            self.current_tutorial = self.tutorial_package.tutorial_with_name(
                self.current_tutorial.name
            )
            self.editor.set_filename(self.current_tutorial.answer_path)
            # TODO: relocate answers?

    @skip_if_attr_none('tutorial_package')
    def set_as_default_package(self):
        """
        Set the current tutorial package as the default tutorial package.

        """
        self.cfg.tutorials.default = self.tutorial_package.name

    def add_tutorial_package(self):
        """
        Prompt the user to add a tutorial package.

        If there is no default tutorial package, then this tutorial package
        will be added as the default.  Otherwise, it will be added as an
        ordinary package.

        If the package was added as the default package, it will be selected
        automatically.

        """
        # if we don't have a default tutorial, we should add this one as the
        # default and then switch to it
        as_default = not self.cfg.tutorials.default
        msg = add_tutorial(self.cfg, as_default=as_default, window=self.master)

        if msg is not None:
            tkmessagebox.showerror(
                'Failed to Add Tutorial',
                'Could not add tutorial: {}'.format(msg),
            )
            return

        if as_default:
            self.tutorial_package = self.cfg.tutorials.default

        self.menu.set_tutorial_packages(self.cfg.tutorials.names)

    @skip_if_attr_none('tutorial_package')
    def remove_current_tutorial_package(self):
        """
        Remove the current tutorial package.

        It is not possible to remove the default tutorial package, or the only
        tutorial package which is available.

        The user will be prompted to confirm the package's removal.  If they
        choose to proceed, the default tutorial package will be selected.

        This process does not delete any problem or answer files.

        """
        if self.cfg.tutorials.default == self.tutorial_package.name:
            tkmessagebox.showerror(
                'Remove Current Tutorial Error',
                'You cannot remove the default tutorial.  ' \
                'Try setting a new default first.'
            )
            return

        if len(self.cfg.tutorials.names) == 1:
            tkmessagebox.showerror(
                'Remove Current Tutorial Error'
                'You cannot remove the last tutorial.  ' \
                'Try adding a new tutorial first.'
            )
            return

        should_remove = tkmessagebox.askquestion(
            'Remove Tutorial?',
            'Do you really want to remove {}?'.format(
                self.tutorial_package.name
            )
        )

        if str(should_remove) == tkmessagebox.YES:
            del self.cfg[self.tutorial_package.name]
            self.cfg.tutorials.names.remove(self.tutorial_package.name)

            self.tutorial_package = self.cfg.tutorials.default

            self.menu.set_tutorial_packages(self.cfg.tutorials.names)

    def change_tutorial_package(self, package_name):
        """
        Change the selected tutorial package.

        Args:
          package_name (str): The name of the tutorial package to change to.

        """
        self.tutorial_package = package_name

    # feedback
    def feedback(self, problem_feedback=False):
        """
        Display a window which enables the user to provide feedback.

        Args:
          problem_feedback (bool, optional): Whether the feedback is about the
              current problem.  If True, then information about the problem
              will be included along with the feedback message.  Defaults to
              False.

        """
        def callback(subject, feedback):
            self.web_api.provide_feedback(
                subject,
                feedback,
                code=self.editor.get_text() if problem_feedback else ''
            )

        if problem_feedback and self.current_tutorial is not None:
            FeedbackDialog(
                self.master,
                'Problem Feedback: {}'.format(self.current_tutorial.name),
                self.current_tutorial.name,
                callback=callback,
            )
        else:
            FeedbackDialog(
                self.master,
                'General Feedback',
                callback=callback,
            )

    # help
    def show_help_dialog(self):
        """
        Show the help dialog.

        """
        self.web_api.display_help()

    def show_about_dialog(self):
        """
        Show the about dialog.

        """
        TutAboutDialog(self.master, 'About MyPyTutor')

    ## TutorEditorDelegate
    check_solution = lambda self: self.run_tests(record_attempt=True)
    quit_editor = close

    ## TestOutputDelegate
    def highlight_error(self, line_number):
        """
        Highlight an error on the given line.

        Args:
          line_number (int): The line number to highlight.

        """
        self.editor.error_line(line_number)
