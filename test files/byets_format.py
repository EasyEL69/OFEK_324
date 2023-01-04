<<<<<<< Updated upstream
#TODO: import doesn't work, need to be fix!
from source import writer

def test():
    with open(writer.c.OUTPUT_FILE_PATH, "rb") as f:
        for record in writer.stream.items(f, "item"):
            print(writer.Writer.content_bytes(record))
=======
# TODO: import doesn't work, need to be fix!
from source.message_ex import Message_Exalt
# def test():
#   with open(writer.c.OUTPUT_FILE_PATH, "rb") as f:
#      for record in writer.stream.items(f, "item"):
#         print(writer.Writer.content_bytes(record))


def foo(**args: object) -> dict:
    return args
>>>>>>> Stashed changes


def main():
    test()


if __name__ == '__main__':
    main()