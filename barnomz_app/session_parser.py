import re


class SessionParser:
    terminals = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه-شنبه', 'چهارشنبه', 'پنجشنبه']

    def __init__(self):
        self.objects = []
        self.tokens = []
        self.token_index = 0

    def setup(self, string):
        self.tokens = string.split(' ')
        self.tokens.append('$')
        self.token_index = 0

    def get_token(self):
        return self.tokens[self.token_index]

    def next_token(self):
        self.token_index += 1
        return self.tokens[self.token_index]

    def parse(self, string):
        self.objects = []
        string = SessionParser.fix(string)
        self.setup(string)

        self.step_S()

    def step_S(self):
        token = self.get_token()
        if token == '$':
            return

        if not token in SessionParser.terminals:
            print(f"concern in step_S: not in first set ({token})")
            return

        self.step_P()
        self.step_N()

    def step_P(self):
        token = self.get_token()
        if not token in SessionParser.terminals:
            print(f"concern in step_P: not in first set ({token})")
            return

        d = token
        token = self.next_token()
        if token != 'از':
            print("concern: no از")
            return

        token = self.next_token()
        if token != 'ساعت':
            print("concern: no ساعت")
            return

        token = self.next_token()
        if not SessionParser.assert_time(token):
            print(f"concern in step_P: not a time ({token})")
            return
        s = SessionParser.fix_time(token)

        token = self.next_token()
        if token != 'تا':
            print("concern: no تا")
            return

        token = self.next_token()
        if not SessionParser.assert_time(token):
            print(f"concern in step_P: not a time ({token})")
            return
        e = SessionParser.fix_time(token)

        self.next_token()  # move forward since we captured the token

        self.objects.append((d, s, e))

    def step_N(self):
        token = self.get_token()
        if token != 'و' and token != '$':
            print(f"concern in step_N: not in first or follow ({token})")
            return
        if token == 'و':
            self.next_token()  # capture the و
            self.step_P()
            self.step_N()
        else:  # if token == '$':
            return

    def fix(string):
        new_arr = []
        arr = string.split(' ')
        i = 0
        while i < len(arr):
            token = arr[i]
            matches = re.match("(([0-9]{1,2}:)?[0-9]{1,2})و(.*)$", token)
            if matches is None:
                if (token == 'صه'):
                    new_arr.append('سه-شنبه')
                    i += 2
                else:
                    new_arr.append(token)
                    i += 1
                continue
            mtime = matches.group(1)
            other = matches.group(3)
            new_arr.append(mtime)
            new_arr.append('و')
            if other == 'سه':
                new_arr.append('سه-شنبه')
                i += 2
            else:
                new_arr.append(other)
                i = i + 1
        joined = ' '.join(new_arr)
        return joined

    def fix_time(string):
        if ":" not in string:
            return string + ":00"
        return string

    def assert_time(token):
        matches = re.match("^([0-9]{1,2})(:([0-9]{1,2}))?$", token)
        if matches == None:
            return False
        return True

# string = 'یکشنبه از ساعت 15 تا 16:30وسه شنبه از ساعت 15 تا 16:30وپنجشنبه از ساعت 10:30 تا 12وپنجشنبه از ساعت 15 تا ' \
#         '16:30 '
# parser = SessionParser()
# parser.parse(string)
# print(parser.objects)
