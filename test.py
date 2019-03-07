import unittest
from xjson import (
    Type,
    XJson,
    Args,
)


class TestXJson(unittest.TestCase):
    def test_parsed_string(self):
        string = '"abc"'
        args = Args(i=0)
        o = XJson()
        s = o._parsed_string(string, args)
        assert s == 'abc'
        string = '"\\"\\t\\n"'
        args = Args(i=0)
        s = o._parsed_string(string, args)
        assert s == '"\t\n'
        string = '"\\u263A"'
        args = Args(i=0)
        s = o._parsed_string(string, args)
        assert s == '\u263A'

    def test_parsed_number(self):
        string = '1'
        args = Args(i=0)
        o = XJson()
        s = o._parsed_number(string, args)
        assert s == '1'
        string = '1.1'
        args = Args(i=0)
        s = o._parsed_number(string, args)
        assert s == '1.1'
        string = '-1'
        args = Args(i=0)
        s = o._parsed_number(string, args)
        assert s == '-1'
        string = '1.1e-9'
        args = Args(i=0)
        s = o._parsed_number(string, args)
        assert s == '1.1e-9'

    def test_parsed_keyword(self):
        string = 'true'
        args = Args(i=0)
        o = XJson()
        s = o._parsed_keyword(string, args)
        assert s == 'true'
        string = 'false,'
        args = Args(i=0)
        s = o._parsed_keyword(string, args)
        assert s == 'false'
        string = 'null}'
        args = Args(i=0)
        s = o._parsed_keyword(string, args)
        assert s == 'null'

    def test_parsed_tokens(self):
        string = """
        {
            "string": "abcd",
            "number": 1,
            "keyword": null
        }
        """
        o = XJson()
        tokens = o.parsed_tokens(string)
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
