MyPyTutor
=========

## Installation

Things you'll need to do:

0. Ensure you have python3.4 installed on your machine.
1. `make`
2. Run `code/MyPyTutor.py` in Python 3.
3. Set your MyPyTutor tutorial folder to `CSSE1001Tutorials` in this repo (this folder will be created when you run `make`).
  * You can do this from "Preferences"/"Configure Tutorial Folder" in the menu.
  * If you already have a MPT installation on your machine, you can also edit `~/mypytutor.cfg`.

## Tutorial Format (.tut)

The .tut format is a simple directory-based format.

A valid .tut directory must contain the following files:

`example.tut/`
  
* `analysis.py`
  * contains static analysis code
  * must define `ANALYSER` to contain a `CodeAnalyser` subclass
    * `CodeAnalyser` will be injected into the namespace when run
* `config.py`
  * defines configuration information for the tutorial
  * `SHORT_DESCRIPTION`: a one-line explanation of the task, shown prominently on the UI
  * `STUDENT_FUNCTION`: the name of the function the student must write; if no function is required, use `None`
  * `HINTS`: a list of hints (as strings)
  * `TIMEOUT`: the maximum time to permit to run all tests and perform static analysis on the tutorial (optional)
* `description.html`
  * the tutorial task description
* `preload.py`
  * the code which should be loaded into the MyPyTutor editor window when the tutorial is first run (or is reset)
* `support.py`
  * any code in this file will be executed before testing the student's submission
  * use to define any required functions/classes
* `tests.py`
  * test cases for the student submission
  * must define `TEST_CLASSES` as a list of test case classes (not instances)
  * each test case must inherit from `StudentTestCase`
    * `StudentTestCase` will be injected into the namespace when run
    * test cases must define two class variables:
      * `DESCRIPTION`: a description of the test case, as a string, eg: `add(1, 2) -> 3` or `Does not modify input`
      * `MAIN_TEST`: the name of the method corresponding to the description
    * test cases must contain at least one test method
      * output from this main test method will be shown to the student
      * additional methods may be added to prevent students simply writing code which retursn the right values to meet the visible tests
    * student code may be executed by calling `self.run_student_code`
      * `input_text` may be used to prove a string as stdin
      * `*args` and `**kwargs` will be passed directly to the student's function
