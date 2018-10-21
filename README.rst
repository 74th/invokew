type hint wrapper for Invoke
============================

This is wrapper for using `Invoke <https://github.com/pyinvoke/invoke>`_ with type hints.

https://github.com/pyinvoke/invoke

https://www.pyinvoke.org/

::

    from invokew import task, Context

    @task()
    def test(c: Context):

        c.run("ls")

`Invoke License <https://github.com/pyinvoke/invoke/blob/master/LICENSE>`_
