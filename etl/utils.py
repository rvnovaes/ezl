from os.path import join


def ecm_path_advwin2ezl(advwin_path):
    part = advwin_path.split('Agenda\\', 1)[1].replace('\\', '/')
    return join('ECM', part)


def ecm_path_ezl2advwin(ezl_path):
    part = ezl_path.split('ECM/', 1)[1].replace('/', '\\')
    return join('Agenda', part)
