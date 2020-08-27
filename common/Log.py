import inspect
import json
import os


class Log:
    level = [True] * 4

    @classmethod
    def set_level(cls, level):
        for i in range(len(cls.level)):
            cls.level[i] = False if i < level else True

    @classmethod
    def print_in_color(cls, *txt_msg, back_tupple, fore_tupple=(36, 33, 20)):
        try:
            rf, gf, bf = fore_tupple
            rb, gb, bb = back_tupple
            mat = '\33[38;2;' + str(rf) + ';' + str(gf) + ';' + str(bf) + ';48;2;' + str(rb) + ';' + str(
                gb) + ';' + str(
                bb) + 'm'
            msg = mat + ' '.join(map(str, txt_msg))
            print(msg, '\33[0m')
        except RecursionError as e:
            print(*txt_msg)

    @classmethod
    def _get_file_and_func_and_no(cls):
        cur_frame = inspect.currentframe()
        file_name = os.path.basename(cur_frame.f_back.f_back.f_code.co_filename)
        func_name = cur_frame.f_back.f_back.f_code.co_name
        line_no = cur_frame.f_back.f_back.f_lineno
        return file_name, func_name, line_no

    @classmethod
    def pprint(cls, *args):
        if not cls.level[0]: return
        for c in args:
            try:
                print(json.dumps(c, indent=2))
            except TypeError:
                print(c)

    @classmethod
    def debug(cls, *content):
        if not cls.level[0]: return
        file_name, func_name, line_no = cls._get_file_and_func_and_no()
        cls.print_in_color(f'Debug::【{file_name:<20} {func_name}:{line_no}】', *content, back_tupple=(128, 128, 128))

    @classmethod
    def info(cls, *content):
        if not cls.level[1]: return
        file_name, func_name, line_no = cls._get_file_and_func_and_no()
        cls.print_in_color(f'Info::【{file_name:<20} {func_name}:{line_no}】', *content, back_tupple=(123, 194, 23))

    @classmethod
    def warn(cls, *content):
        if not cls.level[2]: return
        file_name, func_name, line_no = cls._get_file_and_func_and_no()
        cls.print_in_color(f'Warning::【{file_name:<20} {func_name}:{line_no}】', *content, back_tupple=(250, 209, 27))

    @classmethod
    def error(cls, *content):
        if not cls.level[3]: return
        file_name, func_name, line_no = cls._get_file_and_func_and_no()
        cls.print_in_color(f'Error::【{file_name:<20} {func_name}:{line_no}】', *content, back_tupple=(191, 21, 75))
