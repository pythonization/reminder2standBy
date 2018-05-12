"""Various helper functions."""

try:
    import prctl
    # to install run:
    # sudo apt install build-essential libcap-dev
    # pip3 install --user python-prctl
except ImportError:
    prctl = None


def give_name2thread(name, thread_obj):
    """Give name to current thread.

    if prctl installed, then also set name via this module. (Then you can see
    thread name in htop .)
    Do not delete calls of this function. Thread name useful for searching
    bugs.

    :param name: thread name
    :type name: str
    :param thread_obj: pass thread object to legacy python function
    :type thread_obj: Thread
    """
    thread_obj.name = name
    if prctl:
        prctl.set_name(name)
