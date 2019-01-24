import xjson


def main():
    s = """
    {
        "string": "string",
        "int": 1,
        "float": 1.1,
        "bool": true,
        "null": null,
        "dict": {},
        "list": []
    }
    """
    # json 字符串转换成对象
    data = xjson.loads(s)
    print('data', type(data), data)
    # 对象转换成 json 字符串
    string = xjson.dumps(data)
    print('string', type(string),  string)


if __name__ == '__main__':
    main()
