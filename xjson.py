from enum import Enum


class Type(Enum):
    auto = 0            # auto 就是 6 个单字符符号, 用来方便写代码的
    colon = 1           # :
    comma = 2           # ,
    braceLeft = 3       # {
    braceRight = 4      # }
    bracketLeft = 5     # [
    bracketRight = 6    # ]
    number = 7          # 169
    string = 8          # "name"
    keyword = 9         # true, false, null


class Token(object):
    def __init__(self, token_type, token_value):
        super(Token, self).__init__()
        # 用表驱动法处理 if
        d = {
            ':': Type.colon,
            ',': Type.comma,
            '{': Type.braceLeft,
            '}': Type.braceRight,
            '[': Type.bracketLeft,
            ']': Type.bracketRight,
        }
        keywords = {
            'true': True,
            'false': False,
            'null': None,
        }
        if token_type == Type.auto:
            self.type = d[token_value]
        else:
            self.type = token_type
        #
        if token_type == Type.number:
            if '.' in token_value or 'e' in token_value:
                self.value = float(token_value)
            else:
                self.value = int(token_value)
        elif token_type == Type.keyword:
            self.value = keywords[token_value]
        else:
            self.value = token_value

    def __repr__(self):
        return '({})'.format(self.value)


class Args:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v

    def __repr__(self):
        l = ['{}={}'.format(k, v) for k, v in self.__dict__.items()]
        s = ','.join(l)
        return s


class XJson:
    @staticmethod
    def parsed_error():
        raise ValueError('No JSON object could be decoded')

    @staticmethod
    def stringified_error():
        raise TypeError('TypeError: data is not JSON serializable')

    @classmethod
    def _parsed_unicode(cls, string):
        try:
            s = '\\u{}'.format(string).encode('utf-8').decode('unicode_escape')
        except Exception as e:
            return cls.parsed_error()
        return s

    def _parsed_escape(self, string, args):
        args.i += 1
        c = string[args.i]
        t = {
            '\\': '\\',
            '"': '"',
            '/': '/',
            'b': '\b',
            'f': '\f',
            't': '\t',
            'n': '\n',
            'r': '\r',
            'u': 'u',
        }
        s = t.get(c)
        if s is None:
            return self.parsed_error()
        args.i += 1
        if s == 'u':
            s = self._parsed_unicode(string[args.i:args.i+4])
            args.i += 4
        return s

    def _parsed_string(self, string, args):
        length = len(string)
        s = ''
        args.i += 1
        while args.i < length:
            c = string[args.i]
            if c == '"':
                args.i += 1
                return s
            elif c == '\\':
                s += self._parsed_escape(string, args)
            else:
                s += c
                args.i += 1
        # 没有找到引号，程序出错
        return self.parsed_error()

    def _parsed_number(self, string, args):
        length = len(string)
        digits = '1234567890'
        valid_chars = digits + '-' + '.' + 'e'
        exist_dot = False
        s = ''
        while args.i < length:
            c = string[args.i]
            if c not in valid_chars:
                return s
            elif c == '.':
                if exist_dot:
                    return self.parsed_error()
                else:
                    exist_dot = True
                    s += c
                    args.i += 1
            else:
                s += c
                args.i += 1
        return s

    def _parsed_keyword(self, string, args):
        length = len(string)
        valid_keywords = {'true', 'false', 'null'}
        spaces = ' \n\t\r'
        s = ''
        while args.i < length:
            c = string[args.i]
            if c in spaces:
                args.i += 1
            elif c in ',}':
                break
            else:
                s += c
                args.i += 1
        if s not in valid_keywords:
            return self.parsed_error()
        return s

    def parsed_tokens(self, string):
        length = len(string)
        tokens = []
        spaces = ' \n\t\r'
        digits = '1234567890-'
        symbols = ':,{}[]'
        args = Args(i=0)
        while args.i < length:
            c = string[args.i]
            if c in spaces:
                args.i += 1
            elif c in symbols:
                t = Token(Type.auto, c)
                tokens.append(t)
                args.i += 1
            elif c == '"':
                s = self._parsed_string(string, args)
                t = Token(Type.string, s)
                tokens.append(t)
            elif c in digits:
                s = self._parsed_number(string, args)
                t = Token(Type.number, s)
                tokens.append(t)
            else:
                s = self._parsed_keyword(string, args)
                t = Token(Type.keyword, s)
                tokens.append(t)
        return tokens

    def _valid_comma(self, tokens, args):
        length = len(tokens)
        i = args.i - 1
        if tokens[i].type == Type.comma:
            return False
        i = args.i + 1
        if i < length:
            if tokens[i].type == Type.braceRight:
                return False
        return True

    def _parsed_dict(self, tokens, args):
        length = len(tokens)
        key = None
        data = {}
        args.i += 1
        while args.i < length:
            t = tokens[args.i]
            if t.type in [Type.braceLeft, Type.bracketLeft]:
                if key is None:
                    return self.parsed_error()
                if t.type == Type.braceLeft:
                    sub = self._parsed_dict(tokens, args)
                else:
                    sub = self._parsed_list(tokens, args)
                data[key] = sub
                key = None
            elif t.type == Type.colon:
                if key is None:
                    return self.parsed_error()
                args.i += 1
            elif t.type == Type.string:
                if key is None:
                    key = t.value
                else:
                    data[key] = t.value
                    key = None
                args.i += 1
            elif t.type in [Type.number, Type.keyword]:
                if key is None:
                    return self.parsed_error()
                data[key] = t.value
                key = None
                args.i += 1
            elif t.type == Type.comma:
                if not self._valid_comma(tokens, args):
                    return self.parsed_error()
                args.i += 1
            elif t.type == Type.braceRight:
                args.i += 1
                return data
            else:
                return self.parsed_error()

    def _parsed_list(self, tokens, args):
        length = len(tokens)
        data = []
        args.i += 1
        while args.i < length:
            t = tokens[args.i]
            if t.type == Type.braceLeft:
                sub = self._parsed_dict(tokens, args)
                data.append(sub)
            elif t.type == Type.bracketLeft:
                sub = self._parsed_list(tokens, args)
                data.append(sub)
            elif t.type in [Type.number, Type.string, Type.keyword]:
                data.append(t.value)
                args.i += 1
            elif t.type == Type.comma:
                if not self._valid_comma(tokens, args):
                    return self.parsed_error()
                args.i += 1
            elif t.type == Type.bracketRight:
                args.i += 1
                return data
            else:
                return self.parsed_error()

    def parsed_json(self, tokens):
        if len(tokens) == 0:
            return self.parsed_error()
        t = tokens[0]
        if t.type == Type.braceLeft:
            args = Args(i=0)
            data = self._parsed_dict(tokens, args)
            return data
        elif t.type == Type.bracketLeft:
            args = Args(i=0)
            data = self._parsed_list(tokens, args)
            return data
        else:
            return self.parsed_error()

    def _stringified_string(self, string):
        t = {
            '\\': '\\\\',
            '"': '\\"',
            '/': '\\/',
            '\b': '\\b',
            '\f': '\\f',
            '\t': '\\t',
            '\n': '\\n',
            '\r': '\\r',
            'u': 'u',
        }
        l = []
        for char in string:
            if char in t:
                c = t[char]
            else:
                c = char.encode('unicode_escape').decode('utf-8')
            l.append(c)
        s = '"{}"'.format(''.join(l))
        return s

    def _stringified_value(self, value):
        if isinstance(value, dict):
            s = self._stringified_dict(value)
        elif isinstance(value, list):
            s = self._stringified_list(value)
        elif isinstance(value, str):
            s = self._stringified_string(value)
        elif isinstance(value, bool):
            # 这个条件要放在 isinstance(value, int) 前面，bool 继承于 int
            s = 'true' if value else 'false'
        elif isinstance(value, (int, float)):
            s = '{}'.format(value)
        elif value is None:
            s = 'null'
        else:
            return self.stringified_error()
        return s

    def _stringified_dict(self, data):
        l = []
        for key, value in data.items():
            if not isinstance(key, str):
                return self.stringified_error()
            k = self._stringified_value(key)
            v = self._stringified_value(value)
            kv = '{}:{}'.format(k, v)
            l.append(kv)
        s = '{{{}}}'.format(','.join(l))
        return s

    def _stringified_list(self, data):
        l = [self._stringified_value(d) for d in data]
        s = '[{}]'.format(','.join(l))
        return s

    @classmethod
    def parse(cls, string):
        o = cls()
        tokens = o.parsed_tokens(string)
        data = o.parsed_json(tokens)
        return data

    @classmethod
    def stringify(cls, data):
        o = cls()
        if isinstance(data, dict):
            string = o._stringified_dict(data)
        elif isinstance(data, list):
            string = o._stringified_list(data)
        else:
            string = o._stringified_value(data)
        return string


def loads(string):
    data = XJson.parse(string)
    return data


def dumps(data):
    string = XJson.stringify(data)
    return string
