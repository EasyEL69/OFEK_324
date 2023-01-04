# TODO: import doesn't work, need to be fix!


# def test():
#   with open(writer.c.OUTPUT_FILE_PATH, "rb") as f:
#      for record in writer.stream.items(f, "item"):
#         print(writer.Writer.content_bytes(record))


def foo(**args: object) -> dict:
    return args


def main():
    print(foo(x=5, y=6, k=7))


if __name__ == '__main__':
    main()
