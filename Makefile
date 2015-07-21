# Usage:
#   $ make
#
# To push all relevant files to the EAIT zone:
#   $ make push


.PHONY: all clean cleantutorials tutorials build push

BUILD = CSSE1001Tutorials/CSSE1001Tutorials.zip \
        CSSE1001Tutorials/config.txt \
        code/mpt_installer.py \

all: tutorials

clean: cleantutorials
	-rm -f MyPyTutor34.zip
	-rm -f code/tutorlib/*.pyc
	-rm -rf build

cleantutorials:
	-rm -rf CSSE1001Tutorials

tutorials: problem_db/* cleantutorials
	cp code/MyPyTutor.py code/MyPyTutor.pyw
	python3 code/create_tutorial.py problem_db/CSSE1001.txt \
	CSSE1001Tutorials --ignore-invalid-tutorials --verbose

build: tutorials $(BUILD)
	mkdir -p build
	cp $(BUILD) build

push:
	./sync CSSE1001Tutorials
