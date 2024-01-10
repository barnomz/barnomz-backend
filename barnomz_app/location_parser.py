import re


def parse_location(string):
    if string.startswith("http") or string.startswith("vc"):
        return 'vc', string
    token = string.split(';')[0]
    parts = token.split('-')
    return parts[1], parts[0]


def parse_exam_time(e):
    t = e.split(' ')
    if len(t) != 2: print('BAD E:', e)
    return t[1], t[0]

# string = 'دانشکده مهندسی کامپیوتر-۱۰۲ کامپیوتر;دانشکده مهندسی کامپیوتر-۱۰۲ کامپیوتر'
# print(parse_location(string))
