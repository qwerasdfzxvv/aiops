from threading import Thread


class AsyncApiMixin:

    def is_need_async(self):
        return False

    def do(self, handler, *args, **kwargs):
        if not self.is_need_async():
            return handler(*args, **kwargs)
        resp = self.do_async(handler, *args, **kwargs)
        self.async_callback(*args, **kwargs)
        return resp

    def get_data(self):
        return []

    def do_async(self, handler, *args, **kwargs):
        data = self.get_data()
        if not data:
            t = Thread(
                target=self.do_in_thread,
                args=(handler, *args),
                kwargs=kwargs
            )
            t.start()
            # 可以做一些格式处理
            resp = f'{self.initial_data}'
            return resp

    @property
    def initial_data(self):
        """
         基础返回数据
        """
        return {
            "status": "pending",
            "error": None,
            "resp": None
        }

    def do_in_thread(self, handler, *args, **kwargs):
        data = self.initial_data
        try:
            response = handler(*args, **kwargs)
            data["status"] = "ok"
            data["resp"] = {"data": response}
        except Exception as e:
            data["error"] = str(e)
            data["status"] = "error"

    def async_callback(self, *args, **kwargs):
        raise NotImplementedError()
