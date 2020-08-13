from perusatproc.util import run_otb_command


def pansharpen(inp, inxs, out, create_options=[]):
    create_opt = ''
    if create_options:
        create_opt = '&'.join('gdal:co:{}'.format(opt) for opt in create_options)
    base_cmd = 'otbcli_BundleToPerfectSensor -inp {inp} ' \
        '-inxs {inxs} ' \
        '-out "{out}?{create_opt}" uint16'
    run_otb_command(base_cmd.format(inp=inp, inxs=inxs, out=out, create_opt=create_opt))
