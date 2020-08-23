from enum import Enum

from common.utils import Log


class Settings:
    pass
    v_interval = None
    # v_speed = None


class Emitter(Enum):
    TIMER = 1
    T_HHEADER = 2
    T_HSCROLL = 3
    T_WHEEL = 4
    T_LABEL = 5
    T_LABELED = 6
    T_TEMP = 7
    V_PLAYER = 8
    INPUT_JUMPTO = 10


g_default_action = lambda: (_ for _ in ()).throw(NotImplementedError('Please override g_default_action!'))
g_all_actions = lambda: (_ for _ in ()).throw(NotImplementedError('Please override g_all_actions!'))
g_status_prompt = lambda *args: Log.warn('No status prompt implemented, please override g_status_prompt!')
g_all_labels = lambda: (_ for _ in ()).throw(NotImplementedError('Please override g_all_labels!'))
