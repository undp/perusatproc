from perusatproc.util import run_command


def pansharpen(inp, inxs, out):
    base_cmd = 'otbcli_BundleToPerfectSensor -inp {inp} ' \
        '-inxs {inxs} ' \
        '-out "{out}?&gdal:co:COMPRESS=DEFLATE&gdal:co:TILED=YES" uint16'
    run_command(base_cmd.format(inp=inp, inxs=inxs, out=out))
