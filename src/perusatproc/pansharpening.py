from perusatproc.util import run_command


def pansharpen(inp, inxs, out):
    base_cmd = "otbcli_BundleToPerfectSensor -inp {inp} -inxs {inxs} -out {out}"

    cmd = base_cmd.format(inp=inp, inxs=inxs, out=out)

    run_command(cmd)