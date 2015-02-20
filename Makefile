# Usage:
# To create the MyPyTutor zip file:
#   $ make
#
# To push all relevant files to the EAIT zone:
#   $ make push


.PHONY: all clean cleantutorials tutorials build push

BUILD = CSSE1001Tutorials/CSSE1001Tutorials.zip \
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
	python3 code/create_tutorial.py problem_db/CSSE1001.txt \
	CSSE1001Tutorials --ignore-invalid-tutorials --verbose

build: tutorials $(BUILD)
	mkdir -p build
	cp $(BUILD) build

push:
	./sync
