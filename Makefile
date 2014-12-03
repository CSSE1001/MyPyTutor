# Usage:
# To create the MyPyTutor zip file:
#   $ make
#
# To push all relevant files to the EAIT zone:
#   $ make push


.PHONY: all clean tutorials build push

BUILD = MyPyTutor34.zip \
        tut_admin.txt \
        CSSE1001Tutorials/CSSE1001Tutorials.zip \
        CSSE1001Tutorials/config.txt \
        doc/MyPyTutor.html \
        code/mpt_installer.py \
        www/index.html

all: MyPyTutor34.zip tutorials

clean:
	-rm MyPyTutor34.zip
	-rm code/tutorlib/*.pyc
	-rm -r tut_admin.txt CSSE1001Tutorials
	-rm -r build

tutorials: problem_db/*
	-python3 code/create_tutorial.py problem_db/CSSE1001.txt CSSE1001Tutorials

build: tutorials $(BUILD)
	mkdir -p build
	cp $(BUILD) build

push: build
	scp build/* uqprobin@csse1001.zones.eait.uq.edu.au:

MyPyTutor34.zip: code/*.py code/*/*.py
	cp code/MyPyTutor.py{,w}
	python3.4 -m compileall -b code/tutorlib
	cd code && zip ../MyPyTutor34.zip MyPyTutor.py{,w} tutorlib/*.pyc

