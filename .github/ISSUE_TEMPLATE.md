# Context

* syno-cert-decoder version:
* Python version:
* Operating System:

## Description

Describe what you were trying to get done.  Tell us what happened, what went
wrong, and what you expected to happen.

### What I Did

```txt
Paste the command(s) you ran and the output.
```

<details>
<summary>Traceback or other long output</summary>

```txt
Traceback (most recent call last):
  File "/Users/jeff/workspace/emanon/env/bin/emanon", line 33, in <module>
    sys.exit(load_entry_point('emanon', 'console_scripts', 'emanon')())
  File "/Users/jeff/workspace/emanon/env/lib/python3.8/site-packages/typer/main.py", line 214, in __call__
    return get_command(self)(*args, **kwargs)
  File "/Users/jeff/workspace/emanon/env/lib/python3.8/site-packages/click/core.py", line 1128, in __call__
    return self.main(*args, **kwargs)
  File "/Users/jeff/workspace/emanon/env/lib/python3.8/site-packages/click/core.py", line 1053, in main
    rv = self.invoke(ctx)
  File "/Users/jeff/workspace/emanon/env/lib/python3.8/site-packages/click/core.py", line 1659, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "/Users/jeff/workspace/emanon/env/lib/python3.8/site-packages/click/core.py", line 1395, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/Users/jeff/workspace/emanon/env/lib/python3.8/site-packages/click/core.py", line 754, in invoke
    return __callback(*args, **kwargs)
  File "/Users/jeff/workspace/emanon/env/lib/python3.8/site-packages/typer/main.py", line 500, in wrapper
    return callback(**use_params)  # type: ignore
  File "/Users/jeff/workspace/emanon/emanon/cli.py", line 31, in version
    foo.bar
AttributeError: 'NoneType' object has no attribute 'bar'
```

</details>
