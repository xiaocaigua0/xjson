import unittest
from xjson import (
    Type,
    Token,
    XJson,
    Vars,
)
from utils import log


class TestXJson(unittest.TestCase):
    def test_parsed_string(self):
        string = '"abc"'
        vars = Vars(i=0)
        s = XJson.parsed_string(string, vars)
        assert s == 'abc'
        string = '"\\"\\t\\n"'
        vars = Vars(i=0)
        s = XJson.parsed_string(string, vars)
        assert s == '"\t\n'
        string = '"\\u263A"'
        vars = Vars(i=0)
        s = XJson.parsed_string(string, vars)
        assert s == '\u263A'

    def test_parsed_number(self):
        string = '1'
        vars = Vars(i=0)
        s = XJson.parsed_number(string, vars)
        assert s == '1'
        string = '1.1'
        vars = Vars(i=0)
        s = XJson.parsed_number(string, vars)
        assert s == '1.1'
        string = '-1'
        vars = Vars(i=0)
        s = XJson.parsed_number(string, vars)
        assert s == '-1'
        string = '1.1e-9'
        vars = Vars(i=0)
        s = XJson.parsed_number(string, vars)
        assert s == '1.1e-9'

    def test_parsed_keyword(self):
        string = 'true'
        vars = Vars(i=0)
        s = XJson.parsed_keyword(string, vars)
        assert s == 'true'
        string = 'false,'
        vars = Vars(i=0)
        s = XJson.parsed_keyword(string, vars)
        assert s == 'false'
        string = 'null}'
        vars = Vars(i=0)
        s = XJson.parsed_keyword(string, vars)
        assert s == 'null'

    def test_parsed_tokens(self):
        string = """
        {
            "string": "abcd",
            "number": 1,
            "keyword": null
        }
        """
        tokens = XJson.parsed_tokens(string)
        expected_types = [
            Type.braceLeft,
            Type.string,
            Type.colon,
            Type.string,
            Type.comma,
            Type.string,
            Type.colon,
            Type.number,
            Type.comma,
            Type.string,
            Type.colon,
            Type.keyword,
            Type.braceRight,
        ]
        expected_values = [
            '{',
            'string',
            ':',
            'abcd',
            ',',
            'number',
            ':',
            1,
            ',',
            'keyword',
            ':',
            None,
            '}',
        ]
        assert [t.type for t in tokens] == expected_types
        assert [t.value for t in tokens] == expected_values

    def test_parse(self):
        string = """
        {
            "string": "abcd",
            "number": 1,
            "keyword": null
        }
        """
        data = XJson.parse(string)
        expected_data = {
            'string': 'abcd',
            'number': 1,
            'keyword': None,
        }
        assert data == expected_data
        #
        string = """
        [
            {
                "string": "abcd",
                "number": 1,
                "keyword": null
            }
        ]
        """
        data = XJson.parse(string)
        expected_data = [
            {
                'string': 'abcd',
                'number': 1,
                'keyword': None,
            }
        ]
        assert data == expected_data
        #
        string = '1'
        try:
            data = XJson.parse(string)
            assert 0
        except Exception as e:
            assert isinstance(e, ValueError)
        #
        string = """
        {
            "string": "abcd",
        }
        """
        try:
            data = XJson.parse(string)
            assert 0
        except Exception as e:
            assert isinstance(e, ValueError)

    def test_stringify(self):
        data = {
            "string": "abcd",
            "int": 1,
            "float": 1.1,
            "bool": True,
            "null": None,
            "unicode": "\u263A",
        }
        string = XJson.stringify(data)
        expected_string = '{"string":"abcd","int":1,"float":1.1,"bool":true,"null":null,"unicode":"\\u263a"}'
        assert string == expected_string
        #
        data = [
            {
                "string": "abcd",
                "int": 1,
                "float": 1.1,
                "bool": True,
                "null": None,
            }
        ]
        string = XJson.stringify(data)
        expected_string = '[{"string":"abcd","int":1,"float":1.1,"bool":true,"null":null}]'
        assert string == expected_string


if __name__ == '__main__':
    unittest.main()
