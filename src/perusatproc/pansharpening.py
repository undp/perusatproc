from perusatproc.util import run_command


def pansharpen(inp, inxs, out):
    base_cmd = 'otbcli_BundleToPerfectSensor -inp {inp} ' \
        '-inxs {inxs} ' \
        '-out "{out}" uint16'
    run_command(base_cmd.format(inp=inp, inxs=inxs, out=out))
