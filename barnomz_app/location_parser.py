import re

def parse_location(string):
    token = string.split(';')[0]
    parts = token.split('-')
    return (parts[1], parts[0])

def parse_exam_time(e):
    t = e.split(' ')
    return (t[1], t[0])
    

string = 'دانشکده مهندسی کامپیوتر-۱۰۲ کامپیوتر;دانشکده مهندسی کامپیوتر-۱۰۲ کامپیوتر'
print(parse_location(string))
