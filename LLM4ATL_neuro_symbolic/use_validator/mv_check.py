#!/usr/bin/env python3
"""mv_check.py -- thin, standalone wrapper around the USE Model Validator.

INPUT  : a `.use` model (any UML/OCL class model -- it does NOT have to be a
         transformation model) + a `.properties` search configuration.
OUTPUT : written to an output directory (default: ./output/), named after the
         two input files:
           <use>__<config>.result.json   full result: status / stats / instance
           <use>__<config>.soil          the found object model, as a USE
                                         !new / !set / !insert script
                                         (only on SATISFIABLE)
         and a human-readable summary on stdout.

    python3 mv_check.py input/model.use input/config.properties
    python3 mv_check.py input/model.use input/config.properties --out-dir /tmp/run1
    python3 mv_check.py input/model.use input/config.properties --json      # print JSON, still saves
    python3 mv_check.py input/model.use input/config.properties --no-save   # stdout only

Requires only Java 17+.  Nothing is installed: a throw-away USE_HOME with
`lib/plugins/<plugin>.jar` is built and `use` is pointed at it with `-H=`.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEF_USE_JAR = HERE.parent / "use_core" / "use-gui.jar"
DEF_PLUGIN_JAR = HERE.parent / "use_core" / "validator-7.1.1.jar"
DEF_OUT_DIR = HERE / "output"

_OUTCOME = re.compile(r"INFO:\s+(TRIVIALLY_)?(SATISFIABLE|UNSATISFIABLE)\b")
_SOIL_NEW = re.compile(r"!\s*new\s+(\w+)\s*\(\s*'([^']+)'\s*\)")
_SOIL_SET = re.compile(r"!\s*(\w+)\s*\.\s*(\w+)\s*:=\s*(.+)")
_SOIL_INS = re.compile(r"!\s*insert\s*\(([^)]*)\)\s*into\s+(\w+)")


def make_use_home(plugin_jar: Path) -> Path:
    home = Path(tempfile.mkdtemp(prefix="mvcheck_home_"))
    (home / "lib" / "plugins").mkdir(parents=True)
    shutil.copy2(plugin_jar, home / "lib" / "plugins" / plugin_jar.name)
    return home


def parse_soil(soil: str) -> dict:
    objs: dict = {}
    for cls, oid in _SOIL_NEW.findall(soil):
        objs[oid] = {"id": oid, "class": cls, "attrs": {}}
    for oid, attr, val in _SOIL_SET.findall(soil):
        if oid in objs:
            objs[oid]["attrs"][attr] = val.strip().rstrip(";").strip()
    links = [{"assoc": a, "ends": [e.strip() for e in ends.split(",")]}
             for ends, a in _SOIL_INS.findall(soil)]
    return {"objects": list(objs.values()), "links": links}


def run(use_file: Path, config: Path, *, use_jar: Path, plugin_jar: Path,
        timeout: int = 300, out_dir: Path | None = None) -> dict:
    """Run the validator.  If `out_dir` is given, the raw instance dump is kept
    there as `<use>__<config>.soil` on SATISFIABLE and referenced from the
    result as `counterexample_file`."""
    stem = f"{use_file.stem}__{config.stem}"
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        soil = out_dir / f"{stem}.soil"
    else:
        soil = Path(tempfile.mkstemp(suffix=".soil", prefix="mvcheck_")[1])

    home = make_use_home(plugin_jar)
    script = f"modelvalidator -validate {config.resolve()}\nwrite {soil.resolve()}\nquit\n"
    argv = ["java", "-Djava.awt.headless=true", "-jar", str(use_jar),
            "-nogui", "-nr", "-vt", f"-H={home}", str(use_file.resolve())]
    result: dict = {"use": str(use_file), "config": str(config)}
    try:
        pr = subprocess.run(argv, input=script, capture_output=True, text=True, timeout=timeout)
        out = pr.stdout + "\n" + pr.stderr
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["seconds"] = timeout
        return result
    except FileNotFoundError as e:
        result["status"] = "no-java"
        result["error"] = str(e)
        return result
    finally:
        shutil.rmtree(home, ignore_errors=True)

    hits = _OUTCOME.findall(out)
    stats = re.search(r"Translation time.*?Solving time:\s*[\d.]+\s*m?s", out)
    if stats:
        result["stats"] = stats.group(0)

    if not hits:
        result["status"] = "error"
        result["detail"] = (re.findall(r"^.*?:\d+:\d+:.*$|^Error:.*$", out, re.M)[:5]
                            or out.strip().splitlines()[-8:])
        _rm(soil)
        return result

    trivial, kind = hits[-1]
    if kind == "SATISFIABLE":
        result["status"] = "SATISFIABLE" + (" (trivial)" if trivial else "")
        text = soil.read_text(encoding="utf-8") if soil.exists() else ""
        result["instance"] = parse_soil(text)
        if out_dir is not None and soil.exists():
            result["counterexample_file"] = str(soil)
        elif out_dir is None:
            _rm(soil)
    else:
        result["status"] = "UNSATISFIABLE" + (" (trivial)" if trivial else "")
        _rm(soil)
    return result


def _rm(p: Path):
    try:
        p.unlink()
    except OSError:
        pass


def render(res: dict) -> str:
    lines = [f"{Path(res['use']).name}  +  {Path(res['config']).name}",
             f"  status : {res['status']}"]
    if res.get("stats"):
        lines.append(f"  {res['stats']}")
    inst = res.get("instance")
    if inst:
        lines.append("  instance (= counterexample if the .use asserts not P):")
        for o in inst["objects"]:
            extra = f"  {o['attrs']}" if o["attrs"] else ""
            lines.append(f"    obj  {o['class']:<16} {o['id']}{extra}")
        for l in inst["links"]:
            lines.append(f"    link {l['assoc']:<18} ({', '.join(l['ends'])})")
    if res.get("counterexample_file"):
        lines.append(f"  instance file : {res['counterexample_file']}")
    for d in res.get("detail", []):
        lines.append(f"  ! {d}")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("use", type=Path, help="INPUT .use model")
    ap.add_argument("config", type=Path, help="INPUT .properties search configuration")
    ap.add_argument("--out-dir", type=Path, default=DEF_OUT_DIR,
                    help=f"OUTPUT directory (default: {DEF_OUT_DIR})")
    ap.add_argument("--no-save", action="store_true", help="do not write output files")
    ap.add_argument("--use-jar", type=Path, default=DEF_USE_JAR)
    ap.add_argument("--plugin-jar", type=Path, default=DEF_PLUGIN_JAR)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--json", action="store_true", help="print the result JSON to stdout")
    a = ap.parse_args(argv)

    for p in (a.use, a.config, a.use_jar, a.plugin_jar):
        if not p.exists():
            sys.exit(f"not found: {p}")

    out_dir = None if a.no_save else a.out_dir
    res = run(a.use, a.config, use_jar=a.use_jar, plugin_jar=a.plugin_jar,
              timeout=a.timeout, out_dir=out_dir)

    if out_dir is not None:
        stem = f"{a.use.stem}__{a.config.stem}"
        rjson = out_dir / f"{stem}.result.json"
        rjson.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
        res.setdefault("_result_file", str(rjson))

    print(json.dumps(res, indent=2, ensure_ascii=False) if a.json else render(res))
    if out_dir is not None and not a.json:
        print(f"  result file   : {out_dir / (f'{a.use.stem}__{a.config.stem}.result.json')}")
    return 0 if res["status"].split()[0] in ("SATISFIABLE", "UNSATISFIABLE") else 1


if __name__ == "__main__":
    raise SystemExit(main())
