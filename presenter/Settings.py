from common.utils import Log


class Settings:
    pass
    v_interval = None
    # v_speed = None


g_default_action = lambda: (_ for _ in ()).throw(NotImplementedError('Please override g_default_action!'))
g_all_actions = lambda: (_ for _ in ()).throw(NotImplementedError('Please override g_all_actions!'))
g_status_prompt = lambda *args: Log.warn('No status prompt implemented, please override g_status_prompt!')
g_all_labels = lambda: (_ for _ in ()).throw(NotImplementedError('Please override g_all_labels!'))
