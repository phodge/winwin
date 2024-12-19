import re
import subprocess

import click
import libtmux

from winwin.ui import ui_new_session
from winwin.config import Config


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

    cfg = Config()

    _present_jerjerrod_state()

    _present_upstream_branches(cfg)

    _present_tmux_state()

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


def _present_jerjerrod_state():
    try:
        import jerjerrod.projects
        import jerjerrod.caching
    except ImportError:
        click.secho('Jerjerrod: NOT INSTALLED', fg="magenta", dim=True)
        return

    click.secho('Jerjerrod:', fg="magenta", dim=True)
    jkwargs = {
        'JERJERROD:CLEAN': dict(fg="magenta", dim=True),
        'JERJERROD:CHANGED': dict(fg="red", bold=True),
        'JERJERROD:UNPUSHED': dict(fg="yellow", dim=True),
        'JERJERROD:UNTRACKED': dict(fg="red", dim=True),
        'JERJERROD:GARBAGE': dict(fg="yellow", dim=True),
    }
    all_projects = sorted(
        jerjerrod.projects.get_all_projects(jerjerrod.caching.DiskCache(), {}),
        key=lambda p: p.getname(),
    )
    for p in all_projects:
        status = p.getstatus(True)
        label = status[10:]
        if p.isignored:
            label += '/IGNORED'
            kwargs = jkwargs['JERJERROD:CLEAN']
        else:
            kwargs = jkwargs[status]

        if p.isworkspace:
            not_interesting = {'master', 'main'}
            branches = [branch or '<no-branch>' for branch in p.get_branches(False) if branch not in not_interesting]
            branchstr = "|".join(branches)
            more = 0
            while branches and len(branchstr) >= 60:
                more += 1
                branches = branches[:-1]
                branchstr = "{}|+{} more".format("|".join(branches), more)
            if branches:
                label += '|' + branchstr
            elif more:
                # if every branch name was too long to fit
                label += '|{} branches'.format(more)
        else:
            # don't show simple repos if they are clean
            if status != 'JERJERROD:CLEAN':
                branch = p.getbranch(False)
                if branch:
                    label += '|' + branch
            elif not p.spotlight:
                continue

        click.secho('> {} [{}]'.format(p.getname(), label), **kwargs)


def _present_upstream_branches(cfg: Config) -> None:
    upstream_repositories = cfg.get_upstream_repositories()

    if not len(upstream_repositories):
        return

    for upstream in upstream_repositories:
        click.secho('Upstream: ', fg="blue", nl=False)
        click.secho(upstream.label, fg="blue", nl=False, bold=True)

        # what are the remote branches?
        branches = upstream.get_upstream_branches()
        if len(branches):
            click.secho(f' [{len(branches)}]', fg="blue", bold=True)
            for commitsha, refname, subject in branches:
                click.secho('* ' + refname + ' ', fg="blue", nl=False)
                click.secho(subject[:40], fg="blue", dim=True)
        else:
            click.secho(' [no personal branches]', fg="blue", dim=True)


def _present_tmux_state():
    # print list of existing tmux sessions
    tmux = libtmux.Server()
    try:
        sessions = tmux.sessions
    except libtmux.exc.LibTmuxException:
        # probably the server isn't running
        click.secho('No tmux sessions', fg="cyan", dim=True)
        return
    click.secho('Existing tmux sessions: {}'.format(len(sessions)), fg="cyan", dim=True)
    for s in sessions:
        name = s.name
        click.secho('  {}'.format(name), fg="cyan", dim=True)


# the main() hook here allows us to re-spawn winwin.cli.main() in a subprocess
# using 'python -m winwin.cli' instead of needing to know where the executable
# was installed to.
if __name__ == '__main__':
    main()
