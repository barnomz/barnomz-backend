import gnupg # pip3 install python-gnupg
import requests
import subprocess as sp
from bs4 import BeautifulSoup
from .models import *
import datetime as dt
from .session_parser import SessionParser
from .location_parser import parse_location parse_exam_time

# the username and password used
# to log into edu.sharif.edu
_username=None
_password=None


# pgp secret key fingerprint and password
# to decrypt the credentials
fp = ''
secret_passphrase=''

def get_credentials():
    if(_username == None or _password == None):
        retrieve_credentials("http://educred.whackamole.top:18434/getCred")
    return (_username, _password)

def retrieve_credentials(url):
    res = requests.get(url=url)
    data = res.text
    gpg = pnupg.GPG()
    dec = str(gpg.decrypt(data, fp, passphrase=secret_passphrase)).split('/')
    return (dec[0], dec[1])
    

def login():
    username, password = get_credentials()
    session = requests.session()
    response = session.post("https://edu.sharif.edu/login.do", data={
        "username": username,
        "password": password,
        "command": "login",
        })
    if session.cookies.get("JSESSIONID"):
        session.post("https://edu.sharif.edu/action.do", data={
            "changeMenu": "OnlineRegistration",
            "isShowMenu": "",
            "id": "",
            "commandMessage": "",
            "defaultCss": "",
            })
        session.post("https://edu.sharif.edu/register.do", data={
            "changeMenu": "OnlineRegistration*OfficalLessonListShow",
            "isShowMenu": "",
            })
        return session
    return None

def shell_clear_tables(script_name):
    sp.call(['bash', script_name])

def navigate_page(session):
    session.post("https://edu.sharif.edu/action.do" data={
        "chagneMenu":"register",
        "isShowMenu":"",
        "id":"",
        "commandMessage":"",
        "defaultCss":""
        })
    session.post("https://edu.sharif.edu/action.do" data={
        "chagneMenu":"register*lpLocations2",
        "isShowMenu":"",
        "id":"",
        "commandMessage":"",
        "defaultCss":""
        })
    res = session.post("https://edu.sharif.edu/action.do", data={
        "command":"showResult",
        "departmentID":"40",
        "lessonType":"",
        "termID":"14021"}, headers={
            "Referer":"https://edu.sharif.edu/action.do",
            "Origin":"https://edu.sharif.edu"} )
    return res

def extract_data(soup):
    courses = []
    top_tabs = soup.body.findChildren('table', recursive=False)
    sparser = SessionParser()
    for top_tab in top_tabs:
        tables = top_tab.select('table')
        table_meta = tables[2]
        table_data = tables[3]
        grade = table_meta.select_one('td:nth-of-type(2) span').text
        dep = table_meta.select_one('td:nth-of-type(5) span').text
        name=""
        number =""
        group=0
        units=0
        prof_name=""
        capaciy=0
        enrolled=0
        location=None
        sessions=None
        exam_time="00:00"
        exam_date=""
        info=""
        warning=""
        for k in [3,4]:
            row_cols = table_data.select(f"tr:nth-of-type({k})>td")
            name = extract_single(row_cols, 1, name)
            number = extract_single(row_cols, 2, number)
            group = extract_single(row_cols, 3, group)
            units = extract_single(row_cols, 4, units)
            prof_name = extract_single(row_cols, 5, prof_name)
            capaciy = extract_single(row_cols, 8, capaciy)
            enrolled = extract_single(row_cols, 9, enrolled)
            location = extract_single(row_cols, 10, location)
            if location != None:
                location = parse_location(location)
            session = extract_single(row_cols, 11, session)
            if session != None:
                sparser.parse(session)
                sessions = sparser.objects
            exam_date = extract_single(row_cols, 12, exam_date)
            if exam_time != "":
                exam_date, exam_time = parse_exam_time(exam_date)
            info = extract_single(row_cols, 13, info)
            warning = extract_single(row_cols, 14, warning)
            courses.append((name,units,group,exam_date,exam_time,capaciy,enrolled,grade,info,warning,
                            prof_name,
                            location,
                            (dep, 0)
                            ))
    return courses
        
def navigate_page_prerequisites(session):
    pass 


def extract_single(row_cols, n, default):
    col_span = row_cols[n].select('span')
    if(col_span == None):
        return default
    return col_span.text.trim()



def reset_edu_data():
    session = login()
    if session == None:
        return False

    # navigate to the page
    result = navigate_page(session)

    soup = BeautifulSoup(result.content, "html.parser")

    # then perform DOM and parsing to extract the data
    courses = extract_data(soup)

    # edu shows prerequisites somewhere else...
    # TODO: write prerequisites parser
    # TODO: extract and parse prereqs by navigating to
    #       each department and iterating the tables
    #       finally, update whatever course that we
    #       already have to include the prerequisites

    # now for the actual updating:
    # fist remove all of the necessary data
    # from the database by running external
    # sql queries TODO: add the script
    shell_clear_tables('script-name.sh') 
    
    # then insert the new data

    classes = dict()
    profs= dict()
    deps = dict()

    for course_number, course_info in courses.items():
        class_info = course_info[11] 
        class_id = class_info[0]+'-'+class_info[1]
        m_class = None
        if class_id in classes:
            m_class = classes[class_id]
        else:
            m_class= Classroom()
            m_class.fill(class_info[0], class_info[1])
            classes[class_id] = m_class
        
        dep_info = course_info[12] 
        dep_name = dep_info[0]
        m_dep = None
        if dep_name in deps:
            m_dep = deps[dep_name]
        else:
            m_dep = Department()
            m_dep.fill(dep_info[0], dep_info[1])
            deps[dep_name] = m_dep

        prof_name = course_info[10]
        m_prof = None
        if(prof_name in profs):
            m_prof = profs[prof_name]
        else:
            m_prof = Professor()
            m_prof.fill(
                    full_name = prof_name,
                    department = m_dep.name
                    )
            profs[prof_name] = m_prof

        
        m_course = Course()
        m_course.fill(
                    course_name= course_info[0],
                    course_code= course_number,
                    unit_count = course_info[1],
                    presented_by = m_prof,
                    group = course_info[2],
                    location = m_class,
                    final_exam_date = course_info[3],
                    final_exam_time = dt.datetime.strptime(course_info[4], '%H:%M').time(),
                    number_of_capacity = course_info[5],
                    number_of_enrolled = course_info[6],
                    department = m_dep,
                    grade = course_info[7]
                    info = course_info[8],
                    warning = course_info[9],
                )

    
