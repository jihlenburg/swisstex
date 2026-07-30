import subprocess, re, os
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PY = ROOT / "fonts/.venv/bin/python"

class BuildResult:
    def __init__(self, pdf, log, returncode, sidecar):
        self.pdf, self.log, self.returncode, self.sidecar = pdf, log, returncode, sidecar

def build_doc(tex_path, tmp_path, runs=1):
    tex = Path(tex_path)
    r = None
    # TEXINPUTS gains tests/fixtures// (recursive) so identity .sty fixtures
    # (e.g. swissidentity-test.sty, loaded via \RequirePackage from inside
    # swisstex.cls) resolve without copying them next to the .tex under
    # test. The trailing ":" is load-bearing: kpathsea appends the compiled-
    # in default search path after it instead of replacing it, so
    # swisstex.cls itself (found today via cwd=ROOT with no TEXINPUTS set at
    # all) keeps resolving exactly as before.
    env = {**os.environ, "TEXINPUTS": f"{ROOT}/tests/fixtures//:"}
    for _ in range(runs):
        r = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", f"-output-directory={tmp_path}", str(tex)],
            cwd=ROOT, capture_output=True, text=True, timeout=300, env=env)
    log = (tmp_path / f"{tex.stem}.log").read_text(errors="replace")
    side = tmp_path / f"{tex.stem}.swisscheck"
    sidecar = {}
    if side.exists():
        for line in side.read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                sidecar[k.strip()] = v.strip()
    return BuildResult(tmp_path / f"{tex.stem}.pdf", log, r.returncode, sidecar)

def swisscheck(pdf, *args):
    r = subprocess.run([str(PY), str(ROOT / "swisscheck.py"), str(pdf), *args],
                       cwd=ROOT, capture_output=True, text=True, timeout=120)
    return r.returncode, r.stdout + r.stderr
