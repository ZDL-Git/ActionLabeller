import hashlib
import json
import sys
import time

from common.Log import Log


def python_version_required(v: str, ge=True):
    v_tuple = tuple(map(int, v.split('.')))
    v_len = len(v_tuple)
    if v_len > 3:
        Log.error('required version error!')
        return
    if (not ge and v_tuple != sys.version_info[:v_len]) or (ge and v_tuple > sys.version_info[:v_len]):
        raise Exception(f'python version {sys.version_info[:3]} not meets the requirement!')


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


def hash_of_file(file, fn='md5') -> str:
    # BUF_SIZE is totally arbitrary, change for your app!
    # lets read stuff in 500MB chunks!
    buf_size = 524288000
    if fn == 'md5':
        res = hashlib.md5()
    elif fn == 'sha1':
        res = hashlib.sha1()
    else:
        Log.error('fn should in [md5,sha1]')
        return None
    with open(file, 'rb') as f:
        while True:
            data = f.read(buf_size)
            if not data:
                break
            res.update(data)
    return res.hexdigest()
