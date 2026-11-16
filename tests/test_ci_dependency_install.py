"""Exercise the actual CI dependency shell; substitute only sudo/APT and /etc path."""
from pathlib import Path
import json,os,subprocess,sys,textwrap

ROOT=Path(__file__).resolve().parents[1]

def dependency_step():
    block=(ROOT/'.github/workflows/validate.yml').read_text().split('      - name: Install ShellCheck\n',1)[1].split('      - name:',1)[0]
    command=block.split('        run:',1)[1]
    first,*rest=command.splitlines()
    return textwrap.dedent('\n'.join(rest)) if first.strip()=='|' else first.strip()


def run_step(tmp_path,acquisition_error=False):
    tools=tmp_path/'bin';tools.mkdir();log=tmp_path/'apt.jsonl';mirror=tmp_path/'apt-mirrors.txt'
    sudo=tools/'sudo'
    sudo.write_text('#!'+sys.executable+'\n'+textwrap.dedent('''\
        import os,subprocess,sys
        args=sys.argv[1:]
        if args[:2]==['/usr/bin/bash','-c']:
            assert len(args)==3 and '/etc/apt/apt-mirrors.txt' in args[2]
            args[2]=args[2].replace('/etc/apt/apt-mirrors.txt',os.environ['MIRROR_FIXTURE'])
        elif args[0]!='apt-get':
            raise AssertionError('Unexpected privileged boundary')
        raise SystemExit(subprocess.run(args,env=os.environ).returncode)
        '''));sudo.chmod(0o755)
    apt=tools/'apt-get'
    apt.write_text('#!'+sys.executable+'\n'+textwrap.dedent('''\
        import json,os,sys
        from pathlib import Path
        args=sys.argv[1:]
        with Path(os.environ['APT_LOG']).open('a') as stream:stream.write(json.dumps(args)+'\\n')
        if args[-1]=='update' and os.environ.get('ACQUISITION_ERROR')=='1':
            # Real APT may warn with exit0 unless any-acquisition-error is fatal.
            raise SystemExit(100 if '--error-on=any' in args else 0)
        '''));apt.chmod(0o755)
    env={'PATH':str(tools)+':/usr/bin:/bin','HOME':str(tmp_path),'LANG':'C','APT_LOG':str(log),'MIRROR_FIXTURE':str(mirror),'ACQUISITION_ERROR':'1' if acquisition_error else '0'}
    result=subprocess.run(['/bin/bash','--noprofile','--norc','-eo','pipefail','-c',dependency_step()],env=env,text=True,capture_output=True,timeout=10)
    calls=[json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
    return result,calls,mirror


def test_actual_ci_step_uses_official_mirrors_then_requires_all_tools(tmp_path):
    result,calls,mirror=run_step(tmp_path)
    assert result.returncode==0,(result.stdout,result.stderr)
    assert mirror.is_file(),'Runner must replace the evidenced unavailable Azure mirror list'
    assert mirror.read_text().splitlines()==['https://archive.ubuntu.com/ubuntu/','https://security.ubuntu.com/ubuntu/']
    assert calls==[['--error-on=any','update'],['install','--yes','shellcheck','qemu-utils','xorriso','squashfs-tools']]
    assert '--allow-unauthenticated' not in dependency_step() and '--allow-insecure-repositories' not in dependency_step()


def test_actual_ci_step_refuses_transient_index_errors_before_install(tmp_path):
    result,calls,mirror=run_step(tmp_path,acquisition_error=True)
    assert result.returncode==100
    assert mirror.is_file()
    assert calls==[['--error-on=any','update']]
