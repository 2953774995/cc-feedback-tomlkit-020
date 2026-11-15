#!/usr/bin/env python3
"""两份 TOML 结构差异验收探针。

契约：
  from tomlkit.diff import diff_toml
  res = diff_toml(old_text, new_text)
  res.added     新增键的 dotted path 列表
  res.removed   删除键的列表
  res.changed   值变化的键列表
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

FAILED = 0
PASSED = 0


def check(code, desc, fn):
    global FAILED, PASSED
    try:
        fn()
        print(f"[PASS] {code} {desc}")
        PASSED += 1
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] {code} {desc}")
        print(f"        {type(exc).__name__}: {exc}")
        FAILED += 1


def main():
    try:
        from tomlkit.diff import diff_toml  # noqa: F401
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] P0 导入 tomlkit.diff 失败：{type(exc).__name__}: {exc}")
        print("-" * 60)
        print("探针汇总：0/5 通过")
        return 1

    A = 'name = "x"\n[db]\nhost = "h1"\n'
    B = 'name = "y"\n[db]\nhost = "h1"\nport = 5432\n'

    def p1():
        res = diff_toml(A, A)
        assert res.added == [] and res.removed == [] and res.changed == [], res

    def p2():
        res = diff_toml(A, B)
        assert res.added == ["db.port"], res.added

    def p3():
        res = diff_toml(A, B)
        assert res.changed == ["name"], res.changed

    def p4():
        res = diff_toml(B, A)
        assert res.removed == ["db.port"], res.removed

    def p5():
        import tomlkit
        assert tomlkit.parse(A)["db"]["host"] == "h1"

    check("P1", "相同文档无差异", p1)
    check("P2", "新增键带 dotted path", p2)
    check("P3", "值变更识别", p3)
    check("P4", "反向删除识别", p4)
    check("P5", "既有 parse 不变", p5)

    print("-" * 60)
    print(f"探针汇总：{PASSED}/{PASSED + FAILED} 通过")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
