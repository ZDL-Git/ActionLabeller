import inspect
import json
import os
import sys
import time


def python_version_required(v: str, ge=True):
    sys_version = sys.version_info
    for i, n in enumerate(v.split('.')):
        n = int(n)
        if (not ge and n != sys_version[i]) or (ge and n > sys_version[i]):
            raise Exception(f'python version not meets the requirement!')


def pprint(*args):
    if len(args) == 1:
        try:
            print(json.dumps(*args, indent=2))
            return
        except TypeError:
            pass
    print(*args)


def print_in_color(txt_msg, back_color: tuple, fore_color: tuple = (255,) * 3):
    rf, gf, bf = fore_color
    rb, gb, bb = back_color
    msg = '{0}' + txt_msg
    mat = '\33[38;2;' + str(rf) + ';' + str(gf) + ';' + str(bf) + ';48;2;' + str(rb) + ';' + str(gb) + ';' + str(
        bb) + 'm'
    print(msg.format(mat), '\33[0m')


class Log:
    level = [True] * 4

    @classmethod
    def set_level(cls, level):
        for i in range(len(cls.level)):
            cls.level[i] = False if i < level else True

    @classmethod
    def print_in_color(cls, *txt_msg, back_tupple, fore_tupple=(36, 33, 20)):
        rf, gf, bf = fore_tupple
        rb, gb, bb = back_tupple
        msg = '{0}' + ' '.join(map(str, txt_msg))
        mat = '\33[38;2;' + str(rf) + ';' + str(gf) + ';' + str(bf) + ';48;2;' + str(rb) + ';' + str(gb) + ';' + str(
            bb) + 'm'
        print(msg.format(mat), '\33[0m')

    @classmethod
    def _get_func_and_no(cls):
        cur_frame = inspect.currentframe()
        func_name = cur_frame.f_back.f_back.f_code.co_name
        line_no = cur_frame.f_back.f_back.f_lineno
        return func_name, line_no

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
        func_name, line_no = cls._get_func_and_no()
        cls.print_in_color(f'Debug::【{func_name}:{line_no}】', *content, back_tupple=(128, 128, 128))

    @classmethod
    def info(cls, *content):
        if not cls.level[1]: return
        func_name, line_no = cls._get_func_and_no()
        cls.print_in_color(f'Info::【{func_name}:{line_no}】', *content, back_tupple=(123, 194, 23))

    @classmethod
    def warn(cls, *content):
        if not cls.level[2]: return
        func_name, line_no = cls._get_func_and_no()
        cls.print_in_color(f'Warning::【{func_name}:{line_no}】', *content, back_tupple=(250, 209, 27))

    @classmethod
    def error(cls, *content):
        if not cls.level[3]: return
        func_name, line_no = cls._get_func_and_no()
        cls.print_in_color(f'Error::【{func_name}:{line_no}】', *content, back_tupple=(191, 21, 75))


def run_cmd(cmd, block=True):
    import subprocess
    (status, output) = subprocess.getstatusoutput(cmd)
    Log.info(f'[{cmd}] result:\n==status: {status}\n==output:\n{output}')
    if status and block:
        raise Exception(f'command [{cmd}] execution failed!')
    return output


def version(package):
    cmd = f'pip show {package}|grep Version'
    run_cmd(cmd)


def export_env(key, value):
    os.environ[key] = str(value)


def warn_log(msg):
    print(f'\x1b[91mwarning: {msg}')


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            Log.debug('Timeit:: %r :: %2.2f s' % (method.__name__, (te - ts)))
        return result

    return timed
