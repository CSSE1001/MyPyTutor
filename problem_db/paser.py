from HTMLParser import HTMLParser

class MyHTMLParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        print "Encountered the beginning of a %s tag %s" %(tag,attrs)

    def handle_endtag(self, tag):
        print "Encountered the end of a %s tag" % tag

    def handle_data(self,data):
        print "Data:%s:" %data

f = open("assignments.txt", "U")
parser = MyHTMLParser()

parser.feed(f.read())
f.close()

