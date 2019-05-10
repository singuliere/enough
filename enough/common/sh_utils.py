def run_sh(command, *args, **kwargs):
    return run_sh_display(command, True, *args, **kwargs)


def run_sh_display(command, verbose, *args, **kwargs):
    kwargs['_err_to_out'] = True
    kwargs['_iter'] = "out"
    kwargs['_truncate_exc'] = False
    out = []
    for line in command(*args, **kwargs):
        out.append(line)
        if verbose:
            print(line, end='', flush=True)
    return "".join(out)
