import functools
import unittest

BASE_HEX = 16


def convert_string_to_integer():
    def convert_string_to_integer_inner(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            args_converted = [int(val, BASE_HEX) if isinstance(val, str) else val for val in args]
            kwargs_converted = {key: int(val, BASE_HEX) if isinstance(val, str) else val for key, val in kwargs.items()}
            return func(*args_converted, **kwargs_converted)

        return wrapped

    return convert_string_to_integer_inner


def convert_optional_none_to(default_value=0x0000):
    def convert_optional_none_to_inner(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            args_converted = [default_value if val is None else val for val in args]
            kwargs_converted = {key: default_value if val is None else val for key, val in kwargs.items()}
            return func(*args_converted, **kwargs_converted)

        return wrapped

    return convert_optional_none_to_inner


@convert_string_to_integer()
@convert_optional_none_to(0)
def add(a, b, c=None):
    return a + b + c if c is not None else a + b


class TestConvertStringNoneToIntegerDecorator(unittest.TestCase):

    def test_convert_string_args_to_int(self):
        self.assertEqual(add("0x10", "0x20", "0x30"), 96)
        self.assertEqual(add("0xff", "0x1"), 256)

    def test_retain_none_values(self):
        self.assertEqual(add(None, "0x1"), 1)
        self.assertEqual(add("0x1", None), 1)
        self.assertEqual(add(None, None), 0)

    def test_retain_list_values(self):
        self.assertEqual(add([1, 2], "0x1"), [1, 2, "0x1"])
        self.assertEqual(add("0x1", [1, 2]), ["0x1", 1, 2])
        self.assertEqual(add([1, 2], [3, 4]), [1, 2, 3, 4])

    def test_retain_int_values(self):
        self.assertEqual(add(10, "0x20"), 42)
        self.assertEqual(add("0xff", 1), 256)


if __name__ == '__main__':
    unittest.main()
