#! /usr/bin/env python

import cgi, sys, crypt, random, time, calendar,os,fcntl,shutil, datetime, hashlib

######## start config #################################

# where student data is to be put/found
data_dir = "/opt/local/share/MyPyTutor/CSSE1001/data"

# the file containing the timestamp for the tutorial problems
timestamp_file = "/opt/local/share/MyPyTutor/CSSE1001/config.txt"

# the file containing the version number of MyPyTutor
mpt_version_file = "/opt/local/share/MyPyTutor/CSSE1001/mpt_version.txt"

# the file containing the tutorial information
tut_info_file = "/opt/local/share/MyPyTutor/CSSE1001/tut_admin.txt"

# the zip file containing the tutorial info
tut_zipfile_url = "http://csse1001.uqcloud.net/mpt/CSSE1001Tutorials.zip"

# the zip file containing MyPyTutor2.5
#mpt25_url = "https://student.eait.uq.edu.au/mypytutor/MyPyTutor/CSSE1001/MyPyTutor25.zip"
# the zip file containing MyPyTutor2.6
#mpt26_url = "http://mypytutor.cloud.itee.uq.edu.au/MyPyTutor/CSSE1001/MyPyTutor26.zip"
# the zip file containing MyPyTutor2.7
mpt27_url = "http://csse1001.uqcloud.net/mpt/MyPyTutor27.zip"

# datetime format used in due dates
date_format = "%d/%m/%y"

# hour of day (24hr clock) for due time
due_hour = 17

######## end config   #################################

random.seed()

#chars = [chr(x) for x in (range(48, 91) + range(97, 123))]

chars = list("abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ")

print 'Content-Type: text/html\n\n'

def encrypt_password(passwd):
    return hashlib.md5(passwd).hexdigest()

def check_password(id, passwd, admin=False):
    users_file = os.path.join(data_dir,'users')
    users = open(users_file, 'U')
    user_lines = users.readlines()
    users.close()
    for user in user_lines:
        if user.startswith('#'):
            continue
        data = user.split(',')
        if len(data) == 6  and id == data[0]:
            if admin and data[2] != 'admin':
                return False
            encrypted_pw = encrypt_password(passwd)
            return encrypted_pw == data[1] 
    return False

def gen_password(passwd):
    if passwd == '-':
        random.shuffle(chars)
        password = ''.join(chars[:8])
    else:
        password = passwd
    encrypted_password  = encrypt_password(password)
    return password, encrypted_password

def create_session(user_name, admin=False):
    t = calendar.timegm(time.localtime())
    r = random.randint(0, 1000000)
    session_key = '%d:%d' % ( t, r)
    if admin:
        session_key += ':admin'
    user_file = os.path.join(data_dir, user_name)
    session_file = open(user_file, 'w')
    session_file.write(session_key)
    session_file.close()
    return session_key

def logout(user_name):
    user_file = os.path.join(data_dir, user_name)
    session_file = open(user_file, 'w')
    session_file.close()

def check_session_key(key, user_name):
    user_file = os.path.join(data_dir, user_name)
    try:
        session_file = open(user_file, 'U')
        data = session_file.read().rstrip()
        session_file.close()
        if data == '':
            return False, 'Error 199'
        if key == data:
            return True, ''
        key_time = int(key.split(':')[0])
        data_time = int(data.split(':')[0])
        if key_time < data_time:
            return False, 'Another login for this user'
        else:
            return False, 'Error 199'
    except:
        return False, 'Error: Change password error'


def set_password(user, password):
    encrypted_pw = encrypt_password(password)
    lock_file = os.path.join(data_dir,'users.lock')
    lockf = open(lock_file, 'a')
    fcntl.flock(lockf,fcntl.LOCK_EX)
    found = False
    try:
        users_file = os.path.join(data_dir,'users')
        users_file_cp = os.path.join(data_dir,'users_tmp')
        users = open(users_file, 'U')
        users_cp = open(users_file_cp, 'w')
        for line in users:
            if line.startswith('#'):
                users_cp.write(line)
                continue
            items = line.split(',')
            if len(items) == 6 and user == items[0]:
                found = True
                items[1] = encrypted_pw
                new_line = ','.join(items)
                users_cp.write(new_line+'\n')
            elif line.rstrip() == []:
                users_cp.write('\n')
            else:
                users_cp.write(line)
        users_cp.close()
        users.close()
        if found:
            shutil.move(users_file_cp, users_file)
    except:
        found = False                
    lockf.close()
    if found:
        return True, ''
    else:
        return False, "Can't find user"


def change_the_password(form):
    p1 = form['password1'].value
    orig = form['password'].value
    user = form['username'].value
    if not check_password(user, orig):
        return False, 'Incorrect Password.'
    return set_password(user, p1)

def upload_code(form):
    user = form['username'].value
    text = form['code'].value
    problem_name = form['problem_name'].value
    if len(text) > 2000:
        return False, 'Error: Code exceeds maximum length'
    code_file = os.path.join(data_dir, user+'.code')
    header = '##$$%s$$##\n' % problem_name
    if os.path.exists(code_file):
        fd = open(code_file, 'U')
        file_text = fd.read()
        fd.close()
        pos = file_text.find(header)
        if pos == -1:
            fd = open(code_file, 'a')
            fd.write(header + text)
            fd.close()
        else:
            front = file_text[:pos]
            end_pos = file_text.find('##$$', pos+4)
            if end_pos == -1:
                new_text = front + header + text
            else:
                new_text = front + header + text + file_text[end_pos:]
            fd = open(code_file, 'w')
            fd.write(new_text)
            fd.close()
        return True, "OK"
    else:
        fd = open(code_file, 'w')
        fd.write(header + text)
        fd.close()
        return True, "OK"

def download_code(form):
    user = form['username'].value
    problem_name = form['problem_name'].value
    code_file = os.path.join(data_dir, user+'.code')
    header = '##$$%s$$##\n' % problem_name
    if os.path.exists(code_file):
        fd = open(code_file, 'U')
        file_text = fd.read()
        fd.close()
        pos = file_text.find(header)
        if pos == -1:
            return False, "No code to download"
        else:
            front = file_text[:pos]
            end_pos = file_text.find('##$$', pos+4)
            text = file_text[pos+len(header):end_pos]
            if text:
                return text, ''
            else:
                return ' ',''
    else:
        return False, "No code to download"

def submit_answer(form):
    user = form['username'].value
    tut_id = form['tut_id'].value
    tut_id_crypt = form['tut_id_crypt'].value
    if tut_id_crypt != str(_sh(tut_id + user)):
        return False, "Error 901 "
    tut_check_num = form['tut_check_num'].value
    code = form['code'].value
    #admin_file = os.path.join(data_dir,'tut_admin.txt')
    admin_fid = open(tut_info_file, 'U')
    admin_lines = admin_fid.readlines()
    admin_fid.close()
    found = False
    section = ''
    tut_name = ''
    for line in admin_lines:
        if line.startswith('['):
            section = line.strip()[:-1]
        elif line.startswith(tut_id):
            found = True
            tut_name = line.split(' ', 1)[1].strip()
            break
    if tut_name == '' or section == '':
        return False, "Tutorial not found"
    first_word = section.split(' ', 1)[0][1:]
    try:
        due_date = datetime.datetime.strptime(first_word, date_format)
        due_time = due_date.replace(hour = due_hour)
    except Exception as e:
        #print e
        due_time = None
    today = datetime.datetime.today()
    sub_file = os.path.join(data_dir, user+'.sub')
    header = '\n##$$%s$$##\n' % tut_name
    if due_time and today > due_time:
        msg = "LATE"
        sub_text = header + 'LATE\n' + tut_check_num + '\n' + code
    else:
        msg = "OK"
        sub_text = header + 'OK\n' + tut_check_num + '\n' + code
    if os.path.exists(sub_file):
        fd = open(sub_file, 'U')
        file_text = fd.read()
        fd.close()
        if header in file_text:
            return False, "Already submitted"
        fd = open(sub_file, 'a')
        fd.write(sub_text)
        fd.close()
        return True, msg 
    else:
        fd = open(sub_file, 'w')
        fd.write(sub_text)
        fd.close()
        return True, msg  
    
def show_submit(form):
    user = form['username'].value
    sub_file = os.path.join(data_dir, user+'.sub')
    if os.path.exists(sub_file):
        fd = open(sub_file, 'U')
        file_text = fd.read()
        fd.close()
        return file_text
    else:
        return ''

def admin_form(form):
    return 'session_key' in form and 'admin' in form['session_key'].value

def match_user(form):
    if not admin_form(form):
        return False, 'Error 666'
    if 'match' not in form:
        return False, 'Error 111'
    match = form['match'].value
    users_file = os.path.join(data_dir,'users')
    users = open(users_file, 'U')
    user_lines = users.readlines()
    users.close()
    result = ''
    for user in user_lines:
        if user.startswith('#'):
            continue
        if match in user:
            result += user
    return True, result

def change_user_password(form):
    if not admin_form(form):
        return False, 'Error 666'
    if not ('the_user' in form and 'password' in form):
        return False, 'Error 111'
    user = form['username'].value
    the_user = form['the_user'].value
    password = form['password'].value
    if user == the_user:
        return False, 'Error 112'
    return set_password(the_user, password)
                
def unset_late(form):
    if not admin_form(form):
        return False, 'Error 666'
    if not ('the_user' in form and 'problem' in form):
        return False, 'Error 112'
    user = form['username'].value
    the_user = form['the_user'].value
    problem = form['problem'].value
    problem_tag = "##$$%s$$##" % problem
    #if user == the_user:
    #    return False, 'Error 112'
    sub_file = os.path.join(data_dir, the_user+'.sub')
    sub_fd = open(sub_file, 'U')
    sub_text = sub_fd.readlines()
    sub_fd.close()
    found = False
    updated_text = []
    length = len(sub_text)
    i = 0
    while i < length:
        line = sub_text[i]
        i += 1
        updated_text.append(line)
        if line.startswith(problem_tag):
            found = True
            status = sub_text[i]
            if status.strip() == 'LATE':
                updated_text.append('OK\n')
                i += 1
            else:
                return False, 'Error 113'
    if not found:
        return False, 'Error 114'
    sub_file_cp = os.path.join(data_dir,'sub_tmp')
    sub_file_cp_fd = open(sub_file_cp, 'w')
    sub_file_cp_fd.writelines(updated_text)
    sub_file_cp_fd.close()
    sub_fd = open(sub_file, 'U')
    sub_text_new = sub_fd.readlines()
    sub_fd.close()
    if sub_text == sub_text_new:
        shutil.move(sub_file_cp, sub_file)
        return True, 'OK'
    else:
        return unset_late(form)

def get_problem_list():
    #admin_file = os.path.join(data_dir,'tut_admin.txt')
    admin_fid = open(tut_info_file, 'U')
    admin_lines = admin_fid.readlines()
    admin_fid.close()
    problem_list = []
    for line in admin_lines:
        line = line.strip()
        if line.startswith('[') or line == '':
            continue
        problem_name = line.split(' ', 1)[1].strip()
        problem_list.append(problem_name)
    return problem_list

def get_results(form):
    if not admin_form(form):
        return False, 'Error 666'
    problem_list = get_problem_list()
    users_file = os.path.join(data_dir,'users')
    users_fd = open(users_file, 'U')
    user_lines = users_fd.readlines()
    users_fd.close()
    results_list = list(problem_list)
    results_list.append('######')
    for user in user_lines:
        if user.startswith('#'):
            continue
        data = user.split(',')
        if len(data) == 6  and data[2] == 'student':
            student = data[0]
            sub_file = os.path.join(data_dir, student+'.sub')
            try:
                sub_fd = open(sub_file, 'U')
            except:
                continue
            sub_lines = sub_fd.readlines()
            sub_fd.close()
            length = len(sub_lines)
            i = 0
            result_dict = {}
            while i < length:
                line = sub_lines[i].strip()
                i += 1
                if line.startswith('##$$'):
                    problem = line[4:-4]
                    result = sub_lines[i].strip()
                    i += 1
                    tries = sub_lines[i].strip()
                    i += 1
                    result_dict[problem] = "%s/%s" % (result, tries)
            student_result = [student]
            for prob in problem_list:
                student_result.append(result_dict.get(prob, '-'))
            results_list.append(','.join(student_result))
    return True, '\n'.join(results_list)

def get_user_subs(form):
    if not admin_form(form):
        return False, 'Error 666'
    the_user = form['the_user'].value
    problem_list = get_problem_list()
    sub_file = os.path.join(data_dir, the_user+'.sub')
    try:
        sub_fd = open(sub_file, 'U')
    except:
        return False, 'No user info.'
    sub_lines = sub_fd.readlines()
    sub_fd.close()
    length = len(sub_lines)
    i = 0
    result_dict = {}
    while i < length:
        line = sub_lines[i].strip()
        i += 1
        if line.startswith('##$$'):
            problem = line[4:-4]
            result = sub_lines[i].strip()
            i += 1
            result_dict[problem] = "%s" % result
    user_list = []
    for prob in problem_list:
        user_list.append("%s:::%s" % (prob, result_dict.get(prob, '-')))
    return True, '\n'.join(user_list)
   
def add_user(form):
    if not admin_form(form):
        return False, 'Error 666'
    if not ('type' in form and \
            'the_user' in form and \
            'firstname' in form and \
            'lastname' in form and \
            'password' in form and \
            'email' in form):
        return False, 'Error 120'
    username = form['the_user'].value
    type = form['type'].value
    firstname = form['firstname'].value
    lastname = form['lastname'].value
    email = form['email'].value
    passwd = form['password'].value
    users_file = os.path.join(data_dir,'users')
    users_fd = open(users_file, 'U')
    users_text = users_fd.read()
    users_fd.close()
    if username in users_text:
        return False, 'Error: User is already registered.'
    password, crypt_password = gen_password(passwd)
    text = ','.join([username, crypt_password, type, 
                     firstname, lastname, email])+'\n'
    lock_file = os.path.join(data_dir,'users.lock')
    lockf = open(lock_file, 'a')
    fcntl.flock(lockf,fcntl.LOCK_EX)
    if type == 'student':
        users_fd = open(users_file, 'a')
        users_fd.write(text)
        users_fd.close()
    else:
        users_file_cp = os.path.join(data_dir,'users_tmp')
        users = open(users_file, 'U')
        users_cp = open(users_file_cp, 'w')
        for line in users:
            if line.startswith('#') and type in line:
                users_cp.write(line)
                users_cp.write(text)
            else:
                users_cp.write(line)
        users_cp.close()
        users.close()
        shutil.move(users_file_cp, users_file)
    lockf.close()
    return True, password
    
def _sh(text):
    hash_value = 5381
    num = 0
    for c in text:
        if num > 40:
            break
        num += 1
        hash_value = 0x00ffffff & ((hash_value << 5) + hash_value + ord(c))
    return hash_value

def logged_in(form):
    return 'session_key' in form and 'username' in form

def mpt_print(msg):
    print 'mypytutor>>>'+msg

# Call main function.

def main():
    form = cgi.FieldStorage()
    if 'action' in form:
        action = form['action'].value
        is_admin = 'type' in form and form['type'].value == 'admin'
        if action == 'get_tut_zip_file':
            mpt_print(tut_zipfile_url) 
        elif action == 'get_mpt27':
            mpt_print(mpt27_url) 
        elif action == 'get_mpt26':
            mpt_print(mpt26_url) 
	elif action == 'get_version':
	    fp = open(mpt_version_file, 'U')
	    version_text = fp.read().strip()
	    fp.close()
	    mpt_print(version_text)
        elif action == 'login':
            if 'username' in form and 'password' in form:
                result = check_password(form['username'].value, 
                                        form['password'].value, is_admin)
                if result:
                    session_key = create_session(form['username'].value,
                                                 is_admin)
                    try:
                        fd = open(timestamp_file, 'U')
                        text = fd.read()
                        lines = text.split('\n')                        
                        mpt_print(lines[0] + ' ' + session_key)
                    except:
                        mpt_print('Error: 133')

                else:
                    mpt_print('Error:Incorrect User or Password')
            else:
                mpt_print('Error:Invalid entry')
        elif logged_in(form):
            result, msg = check_session_key(form['session_key'].value, form['username'].value)
            if not result:
                mpt_print('Error: %s' % msg)
                return
            if action == 'logout':
                logout(form['username'].value)
                mpt_print('OK')
            elif action == 'change_password':
                if 'password' in form and 'password1' in form:
                    result, msg = change_the_password(form)
                    if result:
                        mpt_print('OK')
                    else:
                        mpt_print('Error: %s' % msg)
            elif action == 'upload':
                if 'code' in form and 'problem_name' in form:
                    result, msg = upload_code(form)
                    if result:
                        mpt_print('OK')
                    else:
                        mpt_print('Error: %s' % msg)
            elif action == 'download':
                if 'problem_name' in form:
                    result, msg = download_code(form)
                    if result:
                        mpt_print(result)
                    else:
                        mpt_print('Error: %s' % msg)
            elif action == 'submit':
                if 'tut_id' in form and \
                        'tut_id_crypt' in form and \
                        'tut_check_num' in form and \
                        'code' in form:
                    result, msg = submit_answer(form)
                    if result:
                        mpt_print(msg)
                    else:
                        mpt_print('Error: %s' % msg)                       
            elif action == 'show':
                result = show_submit(form)
                mpt_print(result)
            # admin queries
            elif action == 'match':
                result, msg = match_user(form)
                if result:
                    mpt_print(msg)
                else:
                    mpt_print('Error: %s' % msg) 
            elif action == 'change_user_password':
                result, msg = change_user_password(form)
                if result:
                    mpt_print(msg)
                else:
                    mpt_print('Error: %s' % msg)
            elif action == 'unset_late':
                result, msg = unset_late(form)
                if result:
                    mpt_print(msg)
                else:
                    mpt_print('Error: %s' % msg) 
            elif action == 'results':
                result, msg = get_results(form)
                if result:
                    mpt_print(msg)
                else:
                    mpt_print('Error: %s' % msg) 
            elif action == 'get_user_subs':
                result, msg = get_user_subs(form)
                if result:
                    mpt_print(msg)
                else:
                    mpt_print('Error: %s' % msg) 
            elif action == 'add_user':
                result, msg = add_user(form)
                if result:
                    mpt_print(msg)
                else:
                    mpt_print('Error: %s' % msg)
            else:
                mpt_print('Error:Unknown 1')

        else:
            mpt_print('Error:Unknown 2')
    else:
        print '<HTML>\n'
        print '<HEAD>\n'
        print '\t<TITLE>MyPyTutor</TITLE>\n'
        print '</HEAD>\n'
        print 'You must use MyPyTutor directly to interact with the online data.'
        print '</BODY>\n'
        print '</HTML>\n'


main()
