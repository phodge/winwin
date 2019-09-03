import re
import subprocess

import click
import libtmux

from winwin.ui import ui_new_session


@click.group()
def main():
    pass


@main.command('open-terminal')
def open_terminal():
    from winwin.config import get_self_cmd_str
    from winwin.ubuntu import open_terminal_gui

    inner_cmd = (get_self_cmd_str(['present-ui'])
                 + ' || read -n 1 -p "Press any key to exit"')

    # FIXME: what to do if running on OS X?
    open_terminal_gui(
        'Start a new session',
        ['bash', '-c', inner_cmd],
        zoom=1.3,
        w=80, h=24,
    )


@main.command('enter-main-session')
@click.argument('session_name')
def enter_main_session(session_name):
    # commands to run inside the session
    tmux = libtmux.Server()

    session = tmux.new_session(
        session_name,
        attach=False,
        window_name='Window 1',
    )

    # set option on the session
    session.set_option('detach-on-destroy', 'on')

    # now attach to the new session
    session.attach_session()


@main.command('enter-second-session')
@click.argument('session_name')
def enter_second_session(session_name):
    tmux = libtmux.Server()

    # create a new detached session which shares the same windows as the
    # original session
    subprocess.check_call(['tmux', 'new-session', '-d', '-t', session_name])

    name_re = re.compile(r'^%s-\d+$' % re.escape(session_name))

    # find our new session
    session: libtmux.Session = None
    for sess in tmux.list_sessions():
        if name_re.match(sess.get('session_name')):
            session = sess

    if not session:
        raise Exception("Couldn't find session %r" % name_re)  # noqa

    # create a new window for the new session
    session.new_window('Window 5', window_index='5')

    # attach to the session
    session.attach_session()


@main.command('present-ui')
def present_ui():
    #if not CONFIG_DIR.exists():
        #CONFIG_DIR.mkdir(parents=True)

    # TODO: get list of existing sessions
    #existing = []

    # TODO: get a list of historic session names
    #historic = []

    # TODO: change prompt text if there are existing/historic session names we
    # could use
    p = 'Please enter a name for this session'
    answer = click.prompt(p)

    # FIXME: work out if it is an existing session or new session
    if True:
        ui_new_session(answer)
    else:
        raise Exception("TODO: resume the selected session")  # noqa


# the main() hook here allows us to re-spawn winwin.cli.main() in a subprocess
# using 'python -m winwin.cli' instead of needing to know where the executable
# was installed to.
if __name__ == '__main__':
    main()
