# xjson
一个 json 解析和生成器

## 环境
Python：3.x

## 例子
```python
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
    # 对象转换成 json 字符串
    string = xjson.dumps(data)


if __name__ == '__main__':
    main()
```
或者
```
python3 demo.py
```

## 测试
```
python3 test.py
```
