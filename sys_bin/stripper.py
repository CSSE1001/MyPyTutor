#!/usr/bin/python
import sys, re

def strip(infile, outfile):
    fp = open(infile, 'Ur')
    text = fp.read()
    fp.close()
    description = text.split('#{TestCode}#')[0]
    description = description.split('#{Text}#')[1]
    description = description.replace('#{Hint}#', 'Hint')
    stripped_text = re.sub(r'<[^<>]*>', r'', description)
    fp = open(outfile, 'w')
    fp.write(stripped_text)
    fp.close()

if  __name__ == '__main__':
    argc = len(sys.argv)
    if argc != 3:
        print "Usage: stripper.py infile outfile"
    else:
        strip(sys.argv[1], sys.argv[2])



