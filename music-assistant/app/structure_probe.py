import inspect
from types import SimpleNamespace

import app.ingest as ingest
import app.library_scan as library_scan


def to_obj(x):
    if isinstance(x, dict):
        return SimpleNamespace(**x)
    return x


def looks_like_track(obj):
    attrs = set(dir(obj))
    interesting = {"artist", "title", "album", "path", "extension"}
    return len(attrs & interesting) >= 2


def try_call(module, func_name):
    fn = getattr(module, func_name)
    if not callable(fn):
        return None, "not callable"

    try:
        sig = inspect.signature(fn)
    except Exception:
        return None, "no signature"

    required = []
    for p in sig.parameters.values():
        if p.default is inspect._empty and p.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ):
            required.append(p.name)

    if required:
        return None, f"needs args: {required}"

    try:
        result = fn()
    except Exception as e:
        return None, f"call failed: {e}"

    return result, "ok"


def inspect_module(module, label):
    print(f"\n===== {label} =====")
    print("file:", module.__file__)

    found_any = False

    for name in dir(module):
        if name.startswith("_"):
            continue

        obj = getattr(module, name)
        if not callable(obj):
            continue

        found_any = True
        try:
            sig = inspect.signature(obj)
        except Exception:
            sig = "(signature unavailable)"

        print(f"\n-- {name}{sig}")
        result, status = try_call(module, name)
        print("status:", status)

        if status != "ok":
            continue

        print("result type:", type(result))

        if isinstance(result, (list, tuple)):
            print("len:", len(result))
            if result:
                sample = to_obj(result[0])
                print("sample type:", type(sample))
                for attr in ("artist", "title", "album", "path", "extension"):
                    print(f"  {attr} =", getattr(sample, attr, "<missing>"))

                if looks_like_track(sample):
                    print("TRACK-LIKE RESULT: YES")
        else:
            sample = to_obj(result)
            for attr in ("artist", "title", "album", "path", "extension"):
                print(f"  {attr} =", getattr(sample, attr, "<missing>"))

    if not found_any:
        print("No public callables found")


inspect_module(ingest, "INGEST")
inspect_module(library_scan, "LIBRARY_SCAN")
