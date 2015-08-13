from tutorlib.gui.dialogs.text import TextDialog
from tutorlib.interface.web_api import WebAPI
import tkinter as tk
import datetime


class SubmissionsDialog(TextDialog):
    def __init__(self, parent, submissions, tutorial_package):
        # build up the text
        # our desired output is
        #   problem_set_name
        #   tutorial_name : status
        padding = max(
            len(tut.name) for ps in tutorial_package.problem_sets for tut in ps
        )

        status_texts = {
            WebAPI.OK: 'Ok',
            WebAPI.LATE: 'Late',
            WebAPI.LATE_OK: 'Late without penalty',
            WebAPI.MISSING: 'Not Submitted',
        }
        text = ''

        for problem_set in tutorial_package.problem_sets:
            text += '{}\n'.format(problem_set.name)

            for tutorial in problem_set:
                status = submissions.get(tutorial)
                status_text = status_texts.get(status)
                if status_text is None:
                    status_text = 'Unknown'

                text += '    {name: >{padding}} : {status}\n'.format(
                    name=tutorial.name, padding=padding, status=status_text
                )

            text += '\n'

        # pass off the rest of the work to our superclass
        super().__init__(parent, 'Submissions', text)


class SubmissionsSelectDialog(tk.Toplevel):
    def __init__(self, parent, submissions, tutorial_package, text="OK", command=None):

        super().__init__(parent)

        selections = []

        def commandHandler():
            if not command:
                return

            output = []

            for problem_set, var in selections:
                if not var.get():
                    continue

                for problem in problem_set.problems:
                    output.append( (problem, problem_set) )

                self.destroy()

            command(output)


        i = 0

        now = datetime.datetime.now()

        for problem_set in tutorial_package.problem_sets:
            past_due = datetime.datetime.strptime(problem_set.date, "%d/%m/%y") <= now

            var = tk.BooleanVar()
            var.set(not past_due)

            cb = tk.Checkbutton(self, variable=var, text=problem_set.name)

            if past_due:
                cb.configure(state='disabled')

            due_label = tk.Label(self, text=problem_set.date)

            cb.grid(row=i, column=0, sticky=tk.W)
            due_label.grid(row=i, column=1, sticky=tk.W)

            selections.append( (problem_set, var) )

            # for problem in problem_set.problems:
            #
            #     i += 1
            #     cb = tk.Checkbutton(self, text=problem.name, variable=var, command=lambda e=None: print(var.get()) )
            #     cb.grid(row=i, column=1, sticky=tk.W)
            #
            #     status = tk.Label(self, text="Status") #todo: populate with real status
            #     status.grid(row=i, column=2, sticky=tk.W)

            i += 2

        button = tk.Button(self, text=text, command=commandHandler)
        button.grid(row=i, column=1)
