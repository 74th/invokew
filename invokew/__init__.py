from typing import TextIO
import invoke


def task(name=None,
         aliases=(),
         positional=None,
         optional=(),
         iterable=None,
         incrementable=None,
         default=False,
         auto_shortflags=True,
         help={},
         pre=[],
         post=[],
         autoprint=False,
         klass=invoke.Task,
         *args,
         **kwargs):
    wrap = invoke.task(
        name=name,
        aliases=aliases,
        positional=positional,
        optional=optional,
        iterable=iterable,
        incrementable=incrementable,
        default=default,
        auto_shortflags=auto_shortflags,
        help=help,
        pre=pre,
        post=post,
        autoprint=autoprint,
        *args,
        **kwargs)
    def inner(obj):
        if hasattr(obj, "__annotations__"):
            del(obj.__annotations__)
        return wrap(obj)
    return inner


class Context(invoke.Context):
    def run(self,
            command:str,
            shell:str="/bin/bash",
            warn:bool=False,
            hide:str=None,
            pty:bool=True,
            fallback:bool=True,
            echo:bool=False,
            env:dict={},
            replace_env:bool=True,
            encoding:str=None,
            out_stream:TextIO=None,
            err_stream:TextIO=None,
            in_stream:TextIO=None,
            wachers=[],
            echo_stdin:bool=None)->invoke.Result:
        """
        Execute ``command``, returning an instance of `Result`.

        .. note::
            All kwargs will default to the values found in this instance's
            `~.Runner.context` attribute, specifically in its configuration's
            ``run`` subtree (e.g. ``run.echo`` provides the default value for
            the ``echo`` keyword, etc). The base default values are described
            in the parameter list below.

        :param str command: The shell command to execute.

        :param str shell:
            Which shell binary to use. Default: ``/bin/bash`` (on Unix;
            ``COMSPEC`` or ``cmd.exe`` on Windows.)

        :param bool warn:
            Whether to warn and continue, instead of raising
            `.UnexpectedExit`, when the executed command exits with a
            nonzero status. Default: ``False``.

            .. note::
                This setting has no effect on exceptions, which will still be
                raised, typically bundled in `.ThreadException` objects if they
                were raised by the IO worker threads.

                Similarly, `.WatcherError` exceptions raised by
                `.StreamWatcher` instances will also ignore this setting, and
                will usually be bundled inside `.Failure` objects (in order to
                preserve the execution context).

        :param hide:
            Allows the caller to disable ``run``'s default behavior of copying
            the subprocess' stdout and stderr to the controlling terminal.
            Specify ``hide='out'`` (or ``'stdout'``) to hide only the stdout
            stream, ``hide='err'`` (or ``'stderr'``) to hide only stderr, or
            ``hide='both'`` (or ``True``) to hide both streams.

            The default value is ``None``, meaning to print everything;
            ``False`` will also disable hiding.

            .. note::
                Stdout and stderr are always captured and stored in the
                ``Result`` object, regardless of ``hide``'s value.

            .. note::
                ``hide=True`` will also override ``echo=True`` if both are
                given (either as kwargs or via config/CLI).

        :param bool pty:
            By default, ``run`` connects directly to the invoked process and
            reads its stdout/stderr streams. Some programs will buffer (or even
            behave) differently in this situation compared to using an actual
            terminal or pseudoterminal (pty). To use a pty instead of the
            default behavior, specify ``pty=True``.

            .. warning::
                Due to their nature, ptys have a single output stream, so the
                ability to tell stdout apart from stderr is **not possible**
                when ``pty=True``. As such, all output will appear on
                ``out_stream`` (see below) and be captured into the ``stdout``
                result attribute. ``err_stream`` and ``stderr`` will always be
                empty when ``pty=True``.

        :param bool fallback:
            Controls auto-fallback behavior re: problems offering a pty when
            ``pty=True``. Whether this has any effect depends on the specific
            `Runner` subclass being invoked. Default: ``True``.

        :param bool echo:
            Controls whether `.run` prints the command string to local stdout
            prior to executing it. Default: ``False``.

            .. note::
                ``hide=True`` will override ``echo=True`` if both are given.

        :param dict env:
            By default, subprocesses receive a copy of Invoke's own environment
            (i.e. ``os.environ``). Supply a dict here to update that child
            environment.

            For example, ``run('command', env={'PYTHONPATH':
            '/some/virtual/env/maybe'})`` would modify the ``PYTHONPATH`` env
            var, with the rest of the child's env looking identical to the
            parent.

            .. seealso:: ``replace_env`` for changing 'update' to 'replace'.

        :param bool replace_env:
            When ``True``, causes the subprocess to receive the dictionary
            given to ``env`` as its entire shell environment, instead of
            updating a copy of ``os.environ`` (which is the default behavior).
            Default: ``False``.

        :param str encoding:
            Override auto-detection of which encoding the subprocess is using
            for its stdout/stderr streams (which defaults to the return value
            of `default_encoding`).

        :param out_stream:
            A file-like stream object to which the subprocess' standard output
            should be written. If ``None`` (the default), ``sys.stdout`` will
            be used.

        :param err_stream:
            Same as ``out_stream``, except for standard error, and defaulting
            to ``sys.stderr``.

        :param in_stream:
            A file-like stream object to used as the subprocess' standard
            input. If ``None`` (the default), ``sys.stdin`` will be used.

            If ``False``, will disable stdin mirroring entirely (though other
            functionality which writes to the subprocess' stdin, such as
            autoresponding, will still function.) Disabling stdin mirroring can
            help when ``sys.stdin`` is a misbehaving non-stream object, such as
            under test harnesses or headless command runners.

        :param watchers:
            A list of `.StreamWatcher` instances which will be used to scan the
            program's ``stdout`` or ``stderr`` and may write into its ``stdin``
            (typically ``str`` or ``bytes`` objects depending on Python
            version) in response to patterns or other heuristics.

            See :doc:`/concepts/watchers` for details on this functionality.

            Default: ``[]``.

        :param bool echo_stdin:
            Whether to write data from ``in_stream`` back to ``out_stream``.

            In other words, in normal interactive usage, this parameter
            controls whether Invoke mirrors what you type back to your
            terminal.

            By default (when ``None``), this behavior is triggered by the
            following:

                * Not using a pty to run the subcommand (i.e. ``pty=False``),
                  as ptys natively echo stdin to stdout on their own;
                * And when the controlling terminal of Invoke itself (as per
                  ``in_stream``) appears to be a valid terminal device or TTY.
                  (Specifically, when `~invoke.util.isatty` yields a ``True``
                  result when given ``in_stream``.)

                  .. note::
                      This property tends to be ``False`` when piping another
                      program's output into an Invoke session, or when running
                      Invoke within another program (e.g. running Invoke from
                      itself).

            If both of those properties are true, echoing will occur; if either
            is false, no echoing will be performed.

            When not ``None``, this parameter will override that auto-detection
            and force, or disable, echoing.

        :returns:
            `Result`, or a subclass thereof.

        :raises:
            `.UnexpectedExit`, if the command exited nonzero and
            ``warn`` was ``False``.

        :raises:
            `.Failure`, if the command didn't even exit cleanly, e.g. if a
            `.StreamWatcher` raised `.WatcherError`.

        :raises:
            `.ThreadException` (if the background I/O threads encountered
            exceptions other than `.WatcherError`).

        .. versionadded:: 1.0
        """
        return super(Context, self).run(
            command,
            shell=shell,
            warn=warn,
            hide=hide,
            pty=pty,
            fallback=fallback,
            echo=echo,
            env=env,
            replace_env=replace_env,
            encoding=encoding,
            out_stream=out_stream,
            err_stream=err_stream,
            in_stream=in_stream,
            wachers=wachers,
            echo_stdin=echo_stdin)

    def cd(self, path:str):
        """
        Context manager that keeps directory state when executing commands.

        Any calls to `run`, `sudo`, within the wrapped block will implicitly
        have a string similar to ``"cd <path> && "`` prefixed in order to give
        the sense that there is actually statefulness involved.

        Because use of `cd` affects all such invocations, any code making use
        of the `cwd` property will also be affected by use of `cd`.

        Like the actual 'cd' shell builtin, `cd` may be called with relative
        paths (keep in mind that your default starting directory is your user's
        ``$HOME``) and may be nested as well.

        Below is a "normal" attempt at using the shell 'cd', which doesn't work
        since all commands are executed in individual subprocesses -- state is
        **not** kept between invocations of `run` or `sudo`::

            c.run('cd /var/www')
            c.run('ls')

        The above snippet will list the contents of the user's ``$HOME``
        instead of ``/var/www``. With `cd`, however, it will work as expected::

            with c.cd('/var/www'):
                c.run('ls')  # Turns into "cd /var/www && ls"

        Finally, a demonstration (see inline comments) of nesting::

            with c.cd('/var/www'):
                c.run('ls') # cd /var/www && ls
                with c.cd('website1'):
                    c.run('ls')  # cd /var/www/website1 && ls

        .. note::
            Space characters will be escaped automatically to make dealing with
            such directory names easier.

        .. versionadded:: 1.0
        """
        return super(Context, self).cd(path)

    def prefix(self, command:str):
        """
        Prefix all nested `run`/`sudo` commands with given command plus ``&&``.

        Most of the time, you'll want to be using this alongside a shell script
        which alters shell state, such as ones which export or alter shell
        environment variables.

        For example, one of the most common uses of this tool is with the
        ``workon`` command from `virtualenvwrapper
        <https://virtualenvwrapper.readthedocs.io/en/latest/>`_::

            with c.prefix('workon myvenv'):
                c.run('./manage.py migrate')

        In the above snippet, the actual shell command run would be this::

            $ workon myvenv && ./manage.py migrate

        This context manager is compatible with `cd`, so if your virtualenv
        doesn't ``cd`` in its ``postactivate`` script, you could do the
        following::

            with c.cd('/path/to/app'):
                with c.prefix('workon myvenv'):
                    c.run('./manage.py migrate')
                    c.run('./manage.py loaddata fixture')

        Which would result in executions like so::

            $ cd /path/to/app && workon myvenv && ./manage.py migrate
            $ cd /path/to/app && workon myvenv && ./manage.py loaddata fixture

        Finally, as alluded to above, `prefix` may be nested if desired, e.g.::

            with c.prefix('workon myenv'):
                c.run('ls')
                with c.prefix('source /some/script'):
                    c.run('touch a_file')

        The result::

            $ workon myenv && ls
            $ workon myenv && source /some/script && touch a_file

        Contrived, but hopefully illustrative.

        .. versionadded:: 1.0
        """
        return super(Context, self).prefix(command)
