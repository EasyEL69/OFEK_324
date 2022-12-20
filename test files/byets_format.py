#TODO: import doesnot work, need to be fix!
from source import writer

def test():
    with open(writer.c.OUTPUT_FILE_PATH, "rb") as f:
        for record in writer.stream.items(f, "item"):
            print(writer.Writer.content_bytes(record))


def main():
    test()


if __name__ == '__main__':
    main()