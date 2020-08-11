class TableDecorators:
    @classmethod
    def dissort(cls, func):
        def func_wrapper(*arg):
            arg[0].setSortingEnabled(False)
            func(*arg)
            arg[0].setSortingEnabled(True)

        return func_wrapper

    @classmethod
    def block_signals(cls, func):
        def func_wrapper(*arg):
            arg[0].blockSignals(True)
            func(*arg)
            arg[0].blockSignals(False)

        return func_wrapper


def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().setParent(None)
        elif child.layout() is not None:
            clear_layout(child.layout())
