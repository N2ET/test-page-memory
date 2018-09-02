import win32gui
import win32process

title_seed = 0

def find_tag_pid_by_title(parent_win_title):
    handle = win32gui.FindWindow(None, parent_win_title)

    if not handle:
        return

    tag_handle = win32gui.FindWindowE(handle, None, '', None)

    if not tag_handle:
        return

    pid = win32process.GetWindowThreadPorcessId(tag_handle)[1]
    return pid

def get_tag_pid(name, parent_win_title):
    pid = find_tag_pid_by_title(parent_win_title)
    if pid:
        return pid
    pid = input('[%s] input pid: ' % name)
    return pid

def get_tag_pid_by_web_driver(name, dr):
    title = 'get_tag_pid_title_' + str(title_seed)
    dr.execute_script('document.title="' + title + '"')
    return get_tag_pid(name, title + ' - Google Chrome')

