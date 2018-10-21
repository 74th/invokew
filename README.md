# type hint wrapper for Invoke

This is wrapper for using [Invoke](https://github.com/pyinvoke/invoke) with type hints.

https://github.com/pyinvoke/invoke

https://www.pyinvoke.org/

```python
from invokew import task, Context

@task()
def test(c: Context):

    c.run("ls")
```

[Invoke : Copyright (c) 2018 Jeff Forcier.](https://github.com/pyinvoke/invoke/blob/master/LICENSE)