#!/opt/csw/bin/python
#next line doesn't work
#!/usr/bin/python

# Import the CGI module
import cgi
import cgitb; cgitb.enable()
import datetime
import fcntl

print "Content-Type: text/html\n\n"

general_feedback_file = "/opt/local/share/MyPyTutor/CSSE1001/general_feedback.html"
problem_feedback_file = "/opt/local/share/MyPyTutor/CSSE1001/problem_feedback.html"
lockfile = "/opt/local/share/MyPyTutor/CSSE1001/feedback.lock"

def stripHTML(string, breaks):
    split_string = string.split('<', 1)
    result = ''
    result += split_string[0]
    while len(split_string) == 2:
        sp_str = split_string[1].split('>', 1)
        if len(sp_str) == 2:
            if breaks and sp_str[0] in ['p', 'br']:
                result += '<%s>' % sp_str[0]
        split_string =  sp_str[1].split('<', 1)
        result += split_string[0]
    return result


def display_error(error):
    print "<HTML>\n"
    print "<HEAD>\n"
    print "\t<TITLE>Result</TITLE>\n"
    print "</HEAD>\n"
    print "<BODY>\n"
    print "<h3>Feedback Result</h3>"
    print '<span style="color:red">'+error
    print "<p>Feedback not accepted</span>"
    print "</BODY>\n"
    print "</HTML>\n"

def display_data(feedback_type, name, code, feedback, now_string):
    print "<HTML>\n"
    print "<HEAD>\n"
    print "\t<TITLE>Result</TITLE>\n"
    print "</HEAD>\n"
    print "<BODY>\n"
    print "<h3>Feedback Result</h3>"
    if feedback_type == 'General':
        print 'General Feedback\n<p>\n'
        print 'Subject: '+name+ '\n<br>Time: '+now_string+'<br>'
        print 'Feedback:\n<br>\n'
        print feedback
    elif feedback_type == 'Problem':
        print "Feedback for problem '%s'  \n<br>Time: %s\n<br>" % (name, now_string)
        print "Code:\n<br>\n<pre>\n"
        print code
        print '\n</pre>\n<br>\nFeedback:\n<br>\n'
        print feedback
    else:
        print "Unknown feedback type\n"
    print "</BODY>\n"
    print "</HTML>\n"


def dump_data(feedback_type, name, code, feedback, now_string):
    lockf = open(feedback_lock, 'a')    
    fcntl.flock(lockf,fcntl.LOCK_EX)
    if feedback_type == 'General':
        fid = open(general_feedback_file, 'U')
        contents = fid.read()
        fid.close()
        split_text = contents.split('<!--End-->')
        fid = open(general_feedback_file, 'w')
        fid.write(' '.join(split_text[:-1]))
        fid.write('\n<p>\n<b>Subject:</b> '+name)
        fid.write('\n<br>\n<b>Time:</b> '+now_string)
        fid.write('\n<br>\n<b>Feedback:</b>\n<br>\n'+feedback+'\n')
        fid.write('<!--End-->')
        fid.write(split_text[-1])
        fid.close()
    else:
        fid = open(problem_feedback_file, 'U')
        contents = fid.read()
        fid.close()
        split_text = contents.split('<!--End-->')
        fid = open(problem_feedback_file, 'w')
        fid.write(' '.join(split_text[:-1]))
        fid.write('\n<p>\n<b>Problem:</b> '+name)
        fid.write('\n<br>\n<b>Time:</b> '+now_string)
        fid.write('\n<br>\n<b>Code:</b>\n<br>\n<pre>\n'+code+'</pre>')
        fid.write('\n<br>\n<b>Feedback:</b>\n<br>\n'+feedback+'\n')
        fid.write('<!--End-->')
        fid.write(split_text[-1])
    lockf.close() 

def main():
    form = cgi.FieldStorage()
    problem_type = form.getvalue('type','xxx')
    problem_name = form.getvalue('problem_name','')
    code = form.getvalue('code_text','')
    feedback = form.getvalue('feedback','')
    if problem_type == 'xxx':
        display_error('No feedback type')
    elif len(problem_name) > 100:
        display_error('Subject/Problem name too long')
    elif len(code) > 1000:
        display_error('Code too long')
    elif len(feedback) > 1000:
        display_error('Feedback too long')
    else:
	try:
		problem_name = stripHTML(problem_name, False)
		feedback = stripHTML(feedback, True)
	except Exception as e:
		problem_name = str(e)
        now = datetime.datetime.now()
        now_string = now.strftime('%H:%M  %d/%m/%y')
        display_data(problem_type, problem_name, code, feedback, now_string)
        dump_data(problem_type, problem_name, code, feedback, now_string)

# Call main function.
main()
