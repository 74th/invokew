from invoke import task


@task
def install(c):
    c.run("python3 setup.py install")

