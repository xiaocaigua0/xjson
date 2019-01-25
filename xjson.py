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


class Vars:
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
    def parsed_unicode(cls, string):
        try:
            s = '\\u{}'.format(string).encode('utf-8').decode('unicode_escape')
        except Exception as e:
            return cls.parsed_error()
        return s

    @classmethod
    def parsed_escape(cls, string, vars):
        vars.i += 1
        c = string[vars.i]
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
            return cls.parsed_error()
        vars.i += 1
        if s == 'u':
            s = cls.parsed_unicode(string[vars.i:vars.i+4])
            vars.i += 4
        return s

    @classmethod
    def parsed_string(cls, string, vars):
        length = len(string)
        s = ''
        vars.i += 1
        while vars.i < length:
            c = string[vars.i]
            if c == '"':
                vars.i += 1
                return s
            elif c == '\\':
                s += cls.parsed_escape(string, vars)
            else:
                s += c
                vars.i += 1
        # 没有找到引号，程序出错
        return cls.parsed_error()

    @classmethod
    def parsed_number(cls, string, vars):
        length = len(string)
        digits = '1234567890'
        valid_chars = digits + '-' + '.' + 'e'
        exist_dot = False
        s = ''
        while vars.i < length:
            c = string[vars.i]
            if c not in valid_chars:
                return s
            elif c == '.':
                if exist_dot:
                    return cls.parsed_error()
                else:
                    exist_dot = True
                    s += c
                    vars.i += 1
            else:
                s += c
                vars.i += 1
        return s

    @classmethod
    def parsed_keyword(cls, string, vars):
        length = len(string)
        valid_keywords = {'true', 'false', 'null'}
        spaces = ' \n\t\r'
        s = ''
        while vars.i < length:
            c = string[vars.i]
            if c in spaces:
                vars.i += 1
            elif c in ',}':
                break
            else:
                s += c
                vars.i += 1
        if s not in valid_keywords:
            return cls.parsed_error()
        return s

    @classmethod
    def parsed_tokens(cls, string):
        length = len(string)
        tokens = []
        spaces = ' \n\t\r'
        digits = '1234567890-'
        symbols = ':,{}[]'
        vars = Vars(i=0)
        while vars.i < length:
            c = string[vars.i]
            if c in spaces:
                vars.i += 1
            elif c in symbols:
                t = Token(Type.auto, c)
                tokens.append(t)
                vars.i += 1
            elif c == '"':
                s = cls.parsed_string(string, vars)
                t = Token(Type.string, s)
                tokens.append(t)
            elif c in digits:
                s = cls.parsed_number(string, vars)
                t = Token(Type.number, s)
                tokens.append(t)
            else:
                s = cls.parsed_keyword(string, vars)
                t = Token(Type.keyword, s)
                tokens.append(t)
        return tokens

    @staticmethod
    def valid_comma(tokens, vars):
        length = len(tokens)
        i = vars.i - 1
        if tokens[i].type == Type.comma:
            return False
        i = vars.i + 1
        if i < length:
            if tokens[i].type == Type.braceRight:
                return False
        return True

    @classmethod
    def parsed_dict(cls, tokens, vars):
        length = len(tokens)
        key = None
        data = {}
        vars.i += 1
        while vars.i < length:
            t = tokens[vars.i]
            if t.type in [Type.braceLeft, Type.bracketLeft]:
                if key is None:
                    return cls.parsed_error()
                if t.type == Type.braceLeft:
                    sub = cls.parsed_dict(tokens, vars)
                else:
                    sub = cls.parsed_list(tokens, vars)
                data[key] = sub
                key = None
            elif t.type == Type.colon:
                if key is None:
                    return cls.parsed_error()
                vars.i += 1
            elif t.type == Type.string:
                if key is None:
                    key = t.value
                else:
                    data[key] = t.value
                    key = None
                vars.i += 1
            elif t.type in [Type.number, Type.keyword]:
                if key is None:
                    return cls.parsed_error()
                data[key] = t.value
                key = None
                vars.i += 1
            elif t.type == Type.comma:
                if not cls.valid_comma(tokens, vars):
                    return cls.parsed_error()
                vars.i += 1
            elif t.type == Type.braceRight:
                vars.i += 1
                return data
            else:
                return cls.parsed_error()

    @classmethod
    def parsed_list(cls, tokens, vars):
        length = len(tokens)
        data = []
        vars.i += 1
        while vars.i < length:
            t = tokens[vars.i]
            if t.type == Type.braceLeft:
                sub = cls.parsed_dict(tokens, vars)
                data.append(sub)
            elif t.type == Type.bracketLeft:
                sub = cls.parsed_list(tokens, vars)
                data.append(sub)
            elif t.type in [Type.number, Type.string, Type.keyword]:
                data.append(t.value)
                vars.i += 1
            elif t.type == Type.comma:
                if not cls.valid_comma(tokens, vars):
                    return cls.parsed_error()
                vars.i += 1
            elif t.type == Type.bracketRight:
                vars.i += 1
                return data
            else:
                return cls.parsed_error()

    @classmethod
    def parsed_json(cls, tokens):
        if len(tokens) == 0:
            return cls.parsed_error()
        t = tokens[0]
        if t.type == Type.braceLeft:
            vars = Vars(i=0)
            data = cls.parsed_dict(tokens, vars)
            return data
        elif t.type == Type.bracketLeft:
            vars = Vars(i=0)
            data = cls.parsed_list(tokens, vars)
            return data
        else:
            return cls.parsed_error()

    @classmethod
    def stringified_string(cls, string):
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

    @classmethod
    def stringified_value(cls, value):
        if isinstance(value, dict):
            s = cls.stringified_dict(value)
        elif isinstance(value, list):
            s = cls.stringified_list(value)
        elif isinstance(value, str):
            s = cls.stringified_string(value)
        elif isinstance(value, bool):
            # 这个条件要放在 isinstance(value, int) 前面，bool 继承于 int
            s = 'true' if value else 'false'
        elif isinstance(value, (int, float)):
            s = '{}'.format(value)
        elif value is None:
            s = 'null'
        else:
            return cls.stringified_error()
        return s

    @classmethod
    def stringified_dict(cls, data):
        l = []
        for key, value in data.items():
            if not isinstance(key, str):
                return cls.stringified_error()
            k = cls.stringified_value(key)
            v = cls.stringified_value(value)
            kv = '{}:{}'.format(k, v)
            l.append(kv)
        s = '{{{}}}'.format(','.join(l))
        return s

    @classmethod
    def stringified_list(cls, data):
        l = [cls.stringified_value(d) for d in data]
        s = '[{}]'.format(','.join(l))
        return s

    @classmethod
    def parse(cls, string):
        tokens = cls.parsed_tokens(string)
        data = cls.parsed_json(tokens)
        return data

    @classmethod
    def stringify(cls, data):
        if isinstance(data, dict):
            string = cls.stringified_dict(data)
        elif isinstance(data, list):
            string = cls.stringified_list(data)
        else:
            string = cls.stringified_value(data)
        return string


def loads(string):
    data = XJson.parse(string)
    return data


def dumps(data):
    string = XJson.stringify(data)
    return string
