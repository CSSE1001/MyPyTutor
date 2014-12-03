# Usage:
# To create the MyPyTutor zip file:
#   $ make
#
# To push all relevant files to the EAIT zone:
#   $ make push


.PHONY: all clean build push

BUILD = MyPyTutor34.zip \
        tut_admin.txt \
        CSSE1001Tutorials/CSSE1001Tutorials.zip \
        CSSE1001Tutorials/config.txt \
        doc/MyPyTutor.html \
        code/mpt_installer.py \
        www/index.html

all: MyPyTutor34.zip

clean:
	rm MyPyTutor34.zip
	rm -r build

build: $(BUILD)
	mkdir -p build
	cp $(BUILD) build

push: build
	scp build/* uqprobin@csse1001.zones.eait.uq.edu.au:

MyPyTutor34.zip: code/*.py code/*/*.py
	cp code/MyPyTutor.py{,w}
	python3.4 -m compileall -b code/tutorlib
	cd code && zip ../MyPyTutor34.zip MyPyTutor.py{,w} tutorlib/*.pyc

