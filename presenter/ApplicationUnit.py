from zdl.utils.io.log import logger


class ApplicationUnit:

    def __init__(self, mwindow):
        logger.debug('')
        self.mw = mwindow

        self.mw.btn_eval.clicked.connect(self.slot_eval),

    def slot_eval(self):
        eval_content = self.mw.eval_input.toPlainText()
        try:
            resp = eval(eval_content)
            logger.info(f'{eval_content} -> {resp}')
        except Exception as e:
            resp = e.__str__()
            logger.error(f'{eval_content} -> {resp}')
        self.mw.eval_output.setText(str(resp))
