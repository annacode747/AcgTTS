from flask import Flask
from concurrent.futures import ThreadPoolExecutor


class FlaskThreadPool:
    """
    1.在项目合适的地方实例化
        ft_pool = FlaskThreadPool()
    2.在项目合适的地方初始化
        ft_pool.init_app(app)
    3.装饰一个预期异步执行的任务函数
        @ft_pool.submit(callback)
        def func(args1, args2):
            ...
    """

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """ 完成初始化 """
        # 将扩展加入到扩展字典
        self.app = app
        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["async_task"] = self
        size = app.config.setdefault('THREAD_POOL_SIZE', 4)
        self.executor = ThreadPoolExecutor(size)

    def submit(self, callback=None):
        """ 装饰器：将任务异步执行
        1.先将任务加入上下文环境
        2.将任务变成异步任务
        """

        def async_task(func):
            def inner(*args, **kwargs):
                self.executor.submit(func, *args, **kwargs).add_done_callback(callback)

            return inner

        def decorator(func):
            @async_task
            def inner(*args, **kwargs):
                with self.app.app_context():
                    func(*args, **kwargs)

            return inner

        return decorator