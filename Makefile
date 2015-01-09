# Usage:
# To create the MyPyTutor zip file:
#   $ make
#
# To push all relevant files to the EAIT zone:
#   $ make push


.PHONY: all clean cleantutorials tutorials build push

BUILD = MyPyTutor34.zip \
        CSSE1001Tutorials/CSSE1001Tutorials.zip \
        CSSE1001Tutorials/config.txt \
        doc/MyPyTutor.html \
        code/mpt_installer.py \
        www/index.html

all: MyPyTutor34.zip tutorials

clean: cleantutorials
	-rm MyPyTutor34.zip
	-rm code/tutorlib/*.pyc
	-rm -r build

cleantutorials:
	-rm -r CSSE1001Tutorials

tutorials: problem_db/* cleantutorials
	-python3 code/create_tutorial.py problem_db/CSSE1001.txt \
	CSSE1001Tutorials --ignore-invalid-tutorials

build: tutorials $(BUILD)
	mkdir -p build
	cp $(BUILD) build

push: build
	scp build/* uqprobin@csse1001.zones.eait.uq.edu.au:

MyPyTutor34.zip: code/*.py code/*/*.py
	cp code/MyPyTutor.py code/MyPyTutor.pyw
	python3.4 -m compileall -b code/tutorlib
	cd code && zip ../MyPyTutor34.zip MyPyTutor.py code/MyPyTutor.pyw tutorlib/*.pyc

