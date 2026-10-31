"""Reuse the existing completed-job fetcher on the current recovery node."""
from pathlib import Path
import importlib.util,subprocess
P=Path(__file__).resolve().parents[2]
s=importlib.util.spec_from_file_location('fetch_existing',P/'harness/fetch_evidence.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def ssh(script,**kwargs):
 return subprocess.run(['/usr/local/bin/h','ssh','fi-gather-pipeline-resume-1030','-c','c2','-n','ziangli','--','bash','-lc',script],cwd='/Users/ziangli/playground/repos/hai',check=True,**kwargs)
m.ssh=ssh
m.main()
