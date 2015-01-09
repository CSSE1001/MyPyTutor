from abc import ABCMeta, abstractmethod


class TutorEditorDelegate(metaclass=ABCMeta):
    @abstractmethod
    def check_solution(self):
        pass

    @abstractmethod
    def quit_editor(self):
        pass