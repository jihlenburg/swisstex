import subprocess, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PY = ROOT / "fonts/.venv/bin/python"

class BuildResult:
    def __init__(self, pdf, log, returncode, sidecar):
        self.pdf, self.log, self.returncode, self.sidecar = pdf, log, returncode, sidecar

def build_doc(tex_path, tmp_path, runs=1):
    tex = Path(tex_path)
    r = None
    for _ in range(runs):
        r = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", f"-output-directory={tmp_path}", str(tex)],
            cwd=ROOT, capture_output=True, text=True, timeout=300)
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
