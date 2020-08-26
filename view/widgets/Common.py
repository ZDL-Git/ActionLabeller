class TableDecorators:
    @classmethod
    def dissort(cls, func):
        def func_wrapper(*args, **kwargs):
            table = args[0]
            table.setSortingEnabled(False)
            result = func(*args, **kwargs)
            table.setSortingEnabled(True)
            return result

        return func_wrapper

    @classmethod
    def block_signals(cls, func):
        def func_wrapper(*args, **kwargs):
            table = args[0]
            table.blockSignals(True)
            result = func(*args, **kwargs)
            table.blockSignals(False)
            return result

        return func_wrapper


def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().setParent(None)
        elif child.layout() is not None:
            clear_layout(child.layout())
