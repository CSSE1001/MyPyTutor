# Usage:
# To create the MyPyTutor zip file:
#   $ make
#
# To push all relevant files to the EAIT zone:
#   $ make push


.PHONY: all clean build push

BUILD = MyPyTutor.zip \
        tut_admin.txt \
        CSSE1001Tutorials/CSSE1001Tutorials.zip \
        CSSE1001Tutorials/config.txt \
        doc/MyPyTutor.html \
        code/mpt_installer.py \
        www/index.html

all: MyPyTutor.zip

clean:
	rm MyPyTutor.zip
	rm -r build

build: $(BUILD)
	mkdir -p build
	cp $(BUILD) build

push: build
	scp build/* uqprobin@csse1001.zones.eait.uq.edu.au:

MyPyTutor.zip: code/*.py code/*/*.py
	cp code/MyPyTutor.py{,w}
	python2.7 -m compileall code/tutorlib
	cd code && zip ../MyPyTutor.zip MyPyTutor.py{,w} tutorlib/*.pyc

