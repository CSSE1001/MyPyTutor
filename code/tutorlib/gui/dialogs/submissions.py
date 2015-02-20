from tutorlib.gui.dialogs.text import TextDialog
from tutorlib.interface.web_api import WebAPI


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
