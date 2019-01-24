import unittest
from xjson import (
    Type,
    Token,
    XJson,
)
from utils import log


class TestXJson(unittest.TestCase):
    def test_parsed_string(self):
        string = '"abc"'
        s = XJson.parsed_string(string, 0)
        assert s == 'abc'
        string = '"\n\\"a"'
        s = XJson.parsed_string(string, 0)
        assert s == '\n\\"a'

    def test_parsed_number(self):
        string = '1'
        s = XJson.parsed_number(string, 0)
        assert s == '1'
        string = '1.1'
        s = XJson.parsed_number(string, 0)
        assert s == '1.1'
        string = '-1'
        s = XJson.parsed_number(string, 0)
        assert s == '-1'
        string = '1.1e-9'
        s = XJson.parsed_number(string, 0)
        assert s == '1.1e-9'

    def test_parsed_keyword(self):
        string = 'true'
        s = XJson.parsed_keyword(string, 0)
        assert s == 'true'
        string = 'false,'
        s = XJson.parsed_keyword(string, 0)
        assert s == 'false'
        string = 'null}'
        s = XJson.parsed_keyword(string, 0)
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
        }
        string = XJson.stringify(data)
        expected_string = '{"string":"abcd","int":1,"float":1.1,"bool":true,"null":null}'
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
