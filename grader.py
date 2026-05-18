#!/usr/bin/env python3
"""Mini Student Shell 채점 스크립트 (Python 3.9+, cross-platform)

사용법:
    python grader.py [admin_path] [client_path] [students_csv]
    기본값: ./admin_shell(.exe)  ./client_shell(.exe)  ./students.csv

채점 구조:
    [기본]        CSV 비교 (35pt) + 화면 출력 (65pt) = 100pt 기준
    [보너스]      CSV+출력 (15pt)
    [어드밴스드]  CSV (15pt) + 출력 (15pt) = 30pt
"""

import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple


# ─── color support ────────────────────────────────────────────────────────────

def _supports_color() -> bool:
    if platform.system() == "Windows":
        return "ANSICON" in os.environ or "WT_SESSION" in os.environ
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


class C:
    _on = _supports_color()
    GREEN  = "\033[0;32m"  if _on else ""
    RED    = "\033[0;31m"  if _on else ""
    YELLOW = "\033[1;33m"  if _on else ""
    CYAN   = "\033[0;36m"  if _on else ""
    BOLD   = "\033[1m"     if _on else ""
    RESET  = "\033[0m"     if _on else ""


# ─── grader ───────────────────────────────────────────────────────────────────

class Grader:
    def __init__(self, admin: str, client: str, students_csv: str) -> None:
        self.admin = str(Path(admin).resolve())
        self.client = str(Path(client).resolve())
        self.students_csv = students_csv
        self.exp_dir = Path(__file__).parent / "expected"
        self.score = 0
        self.bonus = 0
        self.advanced = 0
        self.MAX = 100
        self.MAX_BONUS = 15
        self.MAX_ADV = 30
        self.tmpdir = tempfile.mkdtemp(prefix="grader_")

    # ── file helpers ──────────────────────────────────────────────────────────

    def mk3(self, path: str) -> None:
        """Write the standard 3-student base CSV (Alice/Bob/Charlie)."""
        with open(path, "w", encoding="ascii", newline="\n") as f:
            f.write("id,name,score\n1,Alice,90\n2,Bob,85\n3,Charlie,95\n")

    def write_csv(self, path: str, lines: List[str]) -> None:
        with open(path, "w", encoding="ascii", newline="\n") as f:
            f.write("\n".join(lines) + "\n")

    def write_cmd(self, path: str, commands: List[str]) -> None:
        with open(path, "w", encoding="ascii", newline="\n") as f:
            f.write("\n".join(commands) + "\n")

    def tmp(self, name: str) -> str:
        return os.path.join(self.tmpdir, name)

    # ── process helpers ───────────────────────────────────────────────────────

    def run(self, exe: str, csv_path: str,
            commands: Optional[List[str]] = None,
            timeout: int = 10) -> str:
        """Run exe csv_path with commands piped via stdin, return combined output."""
        stdin_text = ""
        if commands:
            stdin_text = "\n".join(commands) + "\nexit\n"
        try:
            r = subprocess.run(
                [exe, csv_path],
                input=stdin_text,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return (r.stdout or "") + (r.stderr or "")
        except subprocess.TimeoutExpired:
            return "[TIMEOUT]"
        except Exception as e:
            return f"[ERROR: {e}]"

    def run_no_arg(self, exe: str, timeout: int = 5) -> str:
        """Run exe with no arguments (Usage test)."""
        try:
            r = subprocess.run(
                [exe], capture_output=True, text=True, timeout=timeout
            )
            return (r.stdout or "") + (r.stderr or "")
        except subprocess.TimeoutExpired:
            return "[TIMEOUT]"
        except Exception as e:
            return f"[ERROR: {e}]"

    def run_bad_csv(self, exe: str, csv_path: str, timeout: int = 5) -> str:
        """Run exe with a bad CSV file (no stdin interaction)."""
        try:
            r = subprocess.run(
                [exe, csv_path],
                input="exit\n",
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return (r.stdout or "") + (r.stderr or "")
        except subprocess.TimeoutExpired:
            return "[TIMEOUT]"
        except Exception as e:
            return f"[ERROR: {e}]"

    def run_with_file(self, exe: str, csv_path: str, cmd_file: str,
                      timeout: int = 10) -> str:
        """Run exe csv_path -f cmd_file."""
        try:
            r = subprocess.run(
                [exe, csv_path, "-f", cmd_file],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return (r.stdout or "") + (r.stderr or "")
        except subprocess.TimeoutExpired:
            return "[TIMEOUT]"
        except Exception as e:
            return f"[ERROR: {e}]"

    def run_f_no_file(self, exe: str, csv_path: str,
                      timeout: int = 5) -> Tuple[str, int]:
        """Run exe csv_path -f (no filename) → (output, returncode)."""
        try:
            r = subprocess.run(
                [exe, csv_path, "-f"],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return (r.stdout or "") + (r.stderr or ""), r.returncode
        except subprocess.TimeoutExpired:
            return "[TIMEOUT]", 1
        except Exception as e:
            return f"[ERROR: {e}]", 1

    # ── CSV comparison ────────────────────────────────────────────────────────

    @staticmethod
    def normalize_csv(path: str) -> List[str]:
        if not os.path.exists(path):
            return []
        lines = []
        with open(path, "r", encoding="ascii", errors="replace") as f:
            for line in f:
                line = line.replace("\r", "").rstrip()
                if line:
                    lines.append(line)
        return lines

    def compare_csv(self, actual: str, expected_path: str) -> Tuple[bool, List[str]]:
        a = self.normalize_csv(actual)
        e = self.normalize_csv(expected_path)
        if a == e:
            return True, []
        diffs: List[str] = []
        for i in range(max(len(a), len(e))):
            al = a[i] if i < len(a) else "(없음)"
            el = e[i] if i < len(e) else "(없음)"
            if al != el:
                diffs.append(f"  줄 {i + 1}:")
                diffs.append(f"    실제 : {al}")
                diffs.append(f"    정답 : {el}")
        return False, diffs

    # ── scoring helpers ───────────────────────────────────────────────────────

    def section(self, title: str) -> None:
        print(f"\n{C.CYAN}{C.BOLD}=== {title} ==={C.RESET}")

    def _pass(self, label: str, pts: int, mode: str = "basic") -> None:
        if mode == "bonus":
            tag = "BONUS PASS"
        elif mode == "advanced":
            tag = "ADV PASS"
        else:
            tag = "PASS"
        print(f"  {C.GREEN}[{tag}]{C.RESET} {label} (+{pts}pt)")
        if mode == "basic":
            self.score += pts
        elif mode == "bonus":
            self.bonus += pts
        else:
            self.advanced += pts

    def _fail(self, label: str, pts: int, mode: str = "basic") -> None:
        if mode == "bonus":
            tag, color = "BONUS FAIL", C.YELLOW
        elif mode == "advanced":
            tag, color = "ADV FAIL", C.RED
        else:
            tag, color = "FAIL", C.RED
        print(f"  {color}[{tag}]{C.RESET} {label} (0/{pts}pt)")

    def _skip(self, label: str) -> None:
        print(f"  {C.YELLOW}[SKIP]{C.RESET} {label}")

    def check_csv(self, actual: str, expected_path: str, pts: int,
                  label: str, mode: str = "basic") -> None:
        if not os.path.exists(actual):
            self._fail(label, pts, mode)
            print(f"  {C.RED}  [오류] 실제 파일 없음: {actual}{C.RESET}")
            return
        ok, diffs = self.compare_csv(actual, expected_path)
        if ok:
            self._pass(label, pts, mode)
        else:
            self._fail(label, pts, mode)
            print(f"  {'─' * 40}")
            for d in diffs:
                print(d)
            print(f"  {'─' * 40}")

    def out_test(self, label: str, pts: int, cond: bool,
                 mode: str = "basic", detail: str = "") -> None:
        if cond:
            self._pass(label, pts, mode)
        else:
            self._fail(label, pts, mode)
            if detail:
                preview = detail.replace("\n", " ")[:200]
                print(f"    출력: {preview}")

    # ── build check ───────────────────────────────────────────────────────────

    def check_build(self) -> bool:
        self.section("BUILD CHECK")
        ok = True
        for name, exe in [("admin_shell", self.admin), ("client_shell", self.client)]:
            if os.path.isfile(exe) and os.access(exe, os.X_OK):
                print(f"  {name}: OK ({exe})")
            else:
                print(f"  {C.RED}[ERROR]{C.RESET} {name} 없거나 실행 불가: {exe}")
                ok = False
        return ok

    # ── basic CSV tests (35pt + CSV-07 8pt) ──────────────────────────────────

    def test_basic_csv(self) -> None:
        self.section("CSV-01: add + save [PRD §8.3, §8.1] (9pt)")
        # 3명 기본 CSV → add David 88 → save → 정답과 비교
        csv = self.tmp("csv01.csv")
        self.mk3(csv)
        cmd = self.tmp("cmd01.txt")
        self.write_cmd(cmd, ["add 4 David 88", "save"])
        self.run_with_file(self.admin, csv, cmd)
        self.check_csv(
            csv,
            str(self.exp_dir / "CSV01_add_save" / "expected.csv"),
            9,
            "CSV-01: add 4 David 88 → save → CSV 정답 일치",
        )

        self.section("CSV-02: delete + save [PRD §8.4, §8.1] (9pt)")
        csv = self.tmp("csv02.csv")
        self.mk3(csv)
        cmd = self.tmp("cmd02.txt")
        self.write_cmd(cmd, ["delete 2", "save"])
        self.run_with_file(self.admin, csv, cmd)
        self.check_csv(
            csv,
            str(self.exp_dir / "CSV02_delete_save" / "expected.csv"),
            9,
            "CSV-02: delete 2(Bob) → save → CSV 정답 일치",
        )

        self.section("CSV-03: update + save [PRD §8.5, §8.1] (9pt)")
        csv = self.tmp("csv03.csv")
        self.mk3(csv)
        cmd = self.tmp("cmd03.txt")
        self.write_cmd(cmd, ["update 1 100", "save"])
        self.run_with_file(self.admin, csv, cmd)
        self.check_csv(
            csv,
            str(self.exp_dir / "CSV03_update_save" / "expected.csv"),
            9,
            "CSV-03: update 1→100(Alice) → save → CSV 정답 일치",
        )

        self.section("CSV-04: save → 재시작 → 데이터 유지 [PRD §8.1] (8pt)")
        # 연속성 주의: 두 번의 별도 프로세스 실행으로 영속성 검증
        csv = self.tmp("csv04.csv")
        self.mk3(csv)
        cmd_a = self.tmp("cmd04a.txt")
        self.write_cmd(cmd_a, ["add 4 Eve 77", "save"])
        cmd_b = self.tmp("cmd04b.txt")
        self.write_cmd(cmd_b, ["save"])
        self.run_with_file(self.admin, csv, cmd_a)   # 세션 1: 추가 후 저장
        self.run_with_file(self.admin, csv, cmd_b)   # 세션 2: 재시작 후 재저장
        self.check_csv(
            csv,
            str(self.exp_dir / "CSV04_persist" / "expected.csv"),
            8,
            "CSV-04: add Eve→save→재시작→save → CSV 정답 일치 (영속성)",
        )

        self.section("CSV-07: 100명 학생 load+save (데이터 보존) [PRD §7] (8pt)")
        if not os.path.isfile(self.students_csv):
            self._skip("CSV-07: students.csv 없음")
        else:
            csv = self.tmp("csv07.csv")
            shutil.copy(self.students_csv, csv)
            cmd = self.tmp("cmd07.txt")
            self.write_cmd(cmd, ["save"])
            self.run_with_file(self.admin, csv, cmd)
            self.check_csv(
                csv,
                self.students_csv,
                8,
                "CSV-07: students.csv(100명) load→save → 원본과 동일 (데이터 손실 없음)",
            )

    # ── basic output tests (65pt) ─────────────────────────────────────────────

    def test_basic_output(self) -> None:
        # ── TC01-TC05: 프로그램 시작 / 인자 처리 ─────────────────────────────
        self.section("TC01-TC05: 프로그램 시작 / 인자 처리 [PRD §3] (5pt)")
        csv = self.tmp("s_startup.csv")
        self.mk3(csv)

        out = self.run(self.admin, csv)
        self.out_test("TC01: Admin 시작 배너 '[Admin Program]'", 1,
                      "[Admin Program]" in out, detail=out)

        out = self.run(self.client, csv)
        self.out_test("TC02: Client 시작 배너 '[Client Program]'", 1,
                      "[Client Program]" in out, detail=out)

        out = self.run_no_arg(self.admin)
        self.out_test("TC03: 인자 없을 때 'Usage' 출력", 1,
                      "Usage" in out, detail=out)

        out = self.run(self.admin, csv)
        self.out_test("TC04: 'Loaded 3 students from' 로드 메시지", 1,
                      "Loaded 3 students from" in out, detail=out)

        bad = self.tmp("bad_header.csv")
        self.write_csv(bad, ["BADHEADER", "1,Alice,90"])
        out = self.run_bad_csv(self.admin, bad)
        self.out_test("TC05: 잘못된 CSV 헤더 → Error 출력", 1,
                      any(k in out for k in ["Error", "error", "invalid", "Invalid", "header"]),
                      detail=out)

        # ── TC07: list 빈 목록 ────────────────────────────────────────────────
        self.section("TC07: list 빈 목록 [PRD §8.7] (2pt)")
        empty = self.tmp("empty.csv")
        self.write_csv(empty, ["id,name,score"])
        out = self.run(self.admin, empty, ["list"])
        self.out_test("TC07: list 빈 목록 → 'No students found'", 2,
                      "No students found" in out, detail=out)

        # ── TC08-TC19: add 유효성 검사 ───────────────────────────────────────
        self.section("TC08-TC19: add 명령어 유효성 검사 [PRD §8.3] (10pt)")
        csv = self.tmp("s_add.csv")

        self.mk3(csv)
        out = self.run(self.admin, csv, ["add 4 David 88"])
        self.out_test("TC08: add 정상 추가 → 'Student added'", 1,
                      "Student added" in out, detail=out)

        self.mk3(csv)
        out = self.run(self.admin, csv, ["add 1 Dup 70"])
        self.out_test("TC09: add 중복 ID → duplicate 에러", 1,
                      any(k in out for k in ["duplicate", "Duplicate"]), detail=out)

        self.mk3(csv)
        out = self.run(self.admin, csv, ["add abc Name 80"])
        self.out_test("TC10: add 비숫자 ID → Error", 1, "Error" in out, detail=out)

        self.mk3(csv)
        out = self.run(self.admin, csv, ["add 0 Zero 80"])
        self.out_test("TC11: add ID=0 (양수 필수) → Error", 1, "Error" in out, detail=out)

        self.mk3(csv)
        out = self.run(self.admin, csv, ["add -5 Neg 80"])
        self.out_test("TC12: add 음수 ID → Error", 1, "Error" in out, detail=out)

        self.mk3(csv)
        out = self.run(self.admin, csv, ["add 4 David 101"])
        self.out_test("TC13: add 점수 101 초과 → Error", 1, "Error" in out, detail=out)

        self.mk3(csv)
        out = self.run(self.admin, csv, ["add 4 David -1"])
        self.out_test("TC14: add 점수 -1 미만 → Error", 1, "Error" in out, detail=out)

        self.mk3(csv)
        out = self.run(self.admin, csv, ["add 4 David abc"])
        self.out_test("TC15: add 비숫자 점수 → Error", 1, "Error" in out, detail=out)

        self.mk3(csv)
        out = self.run(self.admin, csv, ["add 4"])
        self.out_test("TC16-17: add 인자 부족/없음 → Error/missing", 1,
                      any(k in out for k in ["Error", "missing"]), detail=out)

        self.mk3(csv)
        out18 = self.run(self.admin, csv, ["add 4 Edge 0"])
        self.mk3(csv)
        out19 = self.run(self.admin, csv, ["add 5 Edge 100"])
        self.out_test("TC18-19: add 점수 경계값 0/100 정상 추가", 1,
                      "Student added" in out18 and "Student added" in out19)

        # ── TC20-TC22: delete ────────────────────────────────────────────────
        self.section("TC20-TC22: delete 명령어 [PRD §8.4] (5pt)")

        self.mk3(csv)
        out = self.run(self.admin, csv, ["delete 2"])
        self.out_test("TC20: delete 정상 삭제 → 'Student deleted'", 2,
                      "Student deleted" in out, detail=out)

        self.mk3(csv)
        out = self.run(self.admin, csv, ["delete 99"])
        self.out_test("TC21: delete 미존재 학생 → 'student not found'", 2,
                      "student not found" in out, detail=out)

        self.mk3(csv)
        out = self.run(self.admin, csv, ["delete xyz"])
        self.out_test("TC22: delete 잘못된 ID → Error", 1, "Error" in out, detail=out)

        # ── TC23-TC26: update ────────────────────────────────────────────────
        self.section("TC23-TC26: update 명령어 [PRD §8.5] (5pt)")

        self.mk3(csv)
        out = self.run(self.admin, csv, ["update 1 100"])
        self.out_test("TC23: update 정상 수정 → 'Student updated'", 2,
                      "Student updated" in out, detail=out)

        self.mk3(csv)
        out = self.run(self.admin, csv, ["update 99 80"])
        self.out_test("TC24: update 미존재 학생 → 'student not found'", 2,
                      "student not found" in out, detail=out)

        self.mk3(csv)
        out = self.run(self.admin, csv, ["update 1 abc"])
        self.out_test("TC25-26: update 점수 오류(abc) → Error", 1, "Error" in out, detail=out)

        # ── TC27-TC30: find ──────────────────────────────────────────────────
        self.section("TC27-TC30: find 명령어 [PRD §8.6] (7pt)")
        csv_f = self.tmp("s_find.csv")
        self.mk3(csv_f)

        out = self.run(self.admin, csv_f, ["find 1"])
        self.out_test("TC27: find 1 (Admin) → ID:1, Name:Alice, Score:90", 2,
                      all(k in out for k in ["ID: 1", "Name: Alice", "Score: 90"]), detail=out)

        out = self.run(self.client, csv_f, ["find 2"])
        self.out_test("TC28: find 2 (Client) → ID:2, Name:Bob, Score:85", 2,
                      all(k in out for k in ["ID: 2", "Name: Bob", "Score: 85"]), detail=out)

        out = self.run(self.admin, csv_f, ["find 99"])
        self.out_test("TC29: find 미존재 학생 → 'student not found'", 2,
                      "student not found" in out, detail=out)

        out = self.run(self.admin, csv_f, ["find abc"])
        self.out_test("TC30: find 잘못된 ID → Error", 1, "Error" in out, detail=out)

        # ── TC32 + TC34-TC35: save/reload ────────────────────────────────────
        self.section("TC32 + TC34-TC35: save/reload 메시지 [PRD §8.1, §8.2] (5pt)")
        csv_sr = self.tmp("s_savereload.csv")
        self.mk3(csv_sr)

        out = self.run(self.admin, csv_sr, ["save"])
        self.out_test("TC32: save → 'Saved N students to <file>' 메시지", 2,
                      "Saved" in out and "students to" in out, detail=out)

        reload_csv = self.tmp("reload.csv")
        self.write_csv(reload_csv, ["id,name,score", "1,Alice,100", "5,New,77"])
        out = self.run(self.admin, reload_csv, ["reload"])
        self.out_test("TC34: reload (Admin) → 'Reloaded N students from <file>'", 2,
                      "Reloaded" in out and "from" in out, detail=out)

        self.mk3(csv_sr)
        out = self.run(self.client, csv_sr, ["reload"])
        self.out_test("TC35: reload (Client) → 'Reloaded' 메시지", 1,
                      "Reloaded" in out, detail=out)

        # ── TC36-TC39: stats ─────────────────────────────────────────────────
        self.section("TC36-TC38 + TC39: stats 명령어 [PRD §8.8] (9pt)")
        csv_st = self.tmp("s_stats.csv")
        self.mk3(csv_st)

        out = self.run(self.admin, csv_st, ["stats"])
        self.out_test("TC36: stats (3명) → Count:3, Average:90.0, Max:95, Min:85", 3,
                      all(k in out for k in
                          ["Count: 3", "Average: 90.0", "Max: 95", "Min: 85"]), detail=out)

        empty2 = self.tmp("empty2.csv")
        self.write_csv(empty2, ["id,name,score"])
        out = self.run(self.admin, empty2, ["stats"])
        self.out_test("TC37: stats 빈 목록 → 'No student data available'", 1,
                      "No student data available" in out, detail=out)

        one = self.tmp("one.csv")
        self.write_csv(one, ["id,name,score", "42,Solo,73"])
        out = self.run(self.admin, one, ["stats"])
        self.out_test("TC38: stats (1명) → Count:1, Average:73.0, Max=Min=73", 2,
                      all(k in out for k in
                          ["Count: 1", "Average: 73.0", "Max: 73", "Min: 73"]), detail=out)

        if os.path.isfile(self.students_csv):
            out = self.run(self.admin, self.students_csv, ["stats"])
            self.out_test("TC39: stats (100명) → Count:100, Max:100, Min:54", 3,
                          all(k in out for k in ["Count: 100", "Max: 100", "Min: 54"]),
                          detail=out)
        else:
            self._skip("TC39: students.csv 없음")

        # ── TC44-TC45: help ───────────────────────────────────────────────────
        self.section("TC44-TC45: help 명령어 [PRD §8.9] (4pt)")
        csv_h = self.tmp("s_help.csv")
        self.mk3(csv_h)

        out = self.run(self.admin, csv_h, ["help"])
        self.out_test("TC44: help (Admin) → save/add/delete/update 모두 표시", 2,
                      all(k in out for k in ["save", "add", "delete", "update"]), detail=out)

        out = self.run(self.client, csv_h, ["help"])
        self.out_test("TC45: help (Client) → find/list 표시, save 미표시", 2,
                      "find" in out and "list" in out and "save" not in out, detail=out)

        # ── TC33 + TC49: 권한 구분 ────────────────────────────────────────────
        self.section("TC33 + TC49: Admin/Client 권한 구분 [PRD §6] (4pt)")
        csv_p = self.tmp("s_perm.csv")
        self.mk3(csv_p)

        out = self.run(self.client, csv_p, ["save"])
        self.out_test("TC33: Client save → 'Unknown command or permission denied'", 1,
                      any(k in out for k in ["Unknown command", "permission denied"]), detail=out)

        for cmd_str, cmd_name in [
            ("add 4 David 88", "add"),
            ("delete 1",       "delete"),
            ("update 1 100",   "update"),
        ]:
            self.mk3(csv_p)
            out = self.run(self.client, csv_p, [cmd_str])
            self.out_test(f"TC49: Client '{cmd_name}' → 거부", 1,
                          any(k in out for k in ["Unknown command", "permission denied"]),
                          detail=out)

        # ── TC54-TC58: -f 옵션 ───────────────────────────────────────────────
        self.section("TC54-TC58: -f 명령어 파일 옵션 [PRD §3.1] (6pt)")
        csv_fx = self.tmp("s_fopt.csv")
        self.mk3(csv_fx)

        cmd54 = self.tmp("cmd54.txt")
        self.write_cmd(cmd54, ["list", "add 4 David 88", "find 4", "exit"])
        out = self.run_with_file(self.admin, csv_fx, cmd54)
        self.out_test("TC54-55: -f 줄 번호 형식 '[command file:N] <cmd>'", 2,
                      "[command file:1] list" in out and
                      "[command file:2] add 4 David 88" in out, detail=out)

        self.mk3(csv_fx)
        cmd56 = self.tmp("cmd56.txt")
        self.write_cmd(cmd56, ["list", "update 99 70", "find 1", "exit"])
        out = self.run_with_file(self.admin, csv_fx, cmd56)
        self.out_test("TC56: -f 에러 → 'Skipped line 2' 후 계속 실행", 2,
                      "student not found" in out and "Skipped line 2" in out and
                      "[command file:3] find 1" in out, detail=out)

        self.mk3(csv_fx)
        cmd57 = self.tmp("cmd57.txt")
        self.write_cmd(cmd57, ["list", "exit", "add 4 ShouldNotRun 99"])
        out = self.run_with_file(self.admin, csv_fx, cmd57)
        self.out_test("TC57: -f exit 이후 명령 처리 안 됨", 1,
                      "Goodbye" in out and "ShouldNotRun" not in out, detail=out)

        self.mk3(csv_fx)
        out, ec = self.run_f_no_file(self.admin, csv_fx)
        self.out_test("TC58: -f 파일명 미지정 → 에러 또는 비정상 종료", 1,
                      any(k in out for k in ["Error", "Usage", "requires"]) or ec != 0,
                      detail=out)

        # ── TC68 + TC70: 에러 처리 ────────────────────────────────────────────
        self.section("TC68 + TC70: 에러 처리 [PRD §10] (3pt)")
        csv_e = self.tmp("s_err.csv")
        self.mk3(csv_e)

        out = self.run(self.admin, csv_e, ["unknowncmd"])
        self.out_test("TC68: 알 수 없는 명령어 → 'Unknown command or permission denied.'", 2,
                      any(k in out for k in ["Unknown command", "permission denied"]), detail=out)

        try:
            r = subprocess.run(
                [self.admin, csv_e],
                input="\n\nlist\nexit\n",
                capture_output=True,
                text=True,
                timeout=10,
            )
            out = (r.stdout or "") + (r.stderr or "")
        except Exception as ex:
            out = str(ex)
        self.out_test("TC70: 빈 입력 줄 무시 → list 정상 처리 (Alice 포함)", 1,
                      "Alice" in out, detail=out)

    # ── bonus tests (15pt) ────────────────────────────────────────────────────

    def test_bonus(self) -> None:
        self.section("BONUS CSV-05: sort name + save [PRD §16] (+4pt)")
        inp05 = str(self.exp_dir / "CSV05_sort_name" / "input.csv")
        exp05 = str(self.exp_dir / "CSV05_sort_name" / "expected.csv")
        csv = self.tmp("csv05.csv")
        shutil.copy(inp05, csv)
        cmd = self.tmp("cmd05.txt")
        self.write_cmd(cmd, ["sort name", "save"])
        self.run_with_file(self.admin, csv, cmd)
        self.check_csv(csv, exp05, 4,
                       "CSV-05: sort name → save → 알파벳 순서 CSV 정답 일치", mode="bonus")

        self.section("BONUS CSV-06: sort score + save [PRD §16] (+4pt)")
        inp06 = str(self.exp_dir / "CSV06_sort_score" / "input.csv")
        exp06 = str(self.exp_dir / "CSV06_sort_score" / "expected.csv")
        csv = self.tmp("csv06.csv")
        shutil.copy(inp06, csv)
        cmd = self.tmp("cmd06.txt")
        self.write_cmd(cmd, ["sort score", "save"])
        self.run_with_file(self.admin, csv, cmd)
        self.check_csv(csv, exp06, 4,
                       "CSV-06: sort score → save → 점수 오름차순 CSV 정답 일치", mode="bonus")

        self.section("BONUS TC40 + TC43: sort 메시지 / 에러 [PRD §16] (+2pt)")
        csv_s = self.tmp("s_sort.csv")
        self.mk3(csv_s)
        out = self.run(self.admin, csv_s, ["sort name"])
        self.out_test("TC40: sort name → 'sorted by name' 메시지", 1,
                      "sorted by name" in out, mode="bonus", detail=out)
        self.mk3(csv_s)
        out = self.run(self.admin, csv_s, ["sort badkey"])
        self.out_test("TC43: sort badkey → Error", 1,
                      "Error" in out, mode="bonus", detail=out)

        self.section("BONUS TC60-TC62: 주석/빈줄 처리 [PRD §16] (+5pt)")
        csv_c = self.tmp("s_comment.csv")
        self.mk3(csv_c)
        cmd_c = self.tmp("cmd_comment.txt")
        self.write_cmd(cmd_c, [
            "# This is a comment",
            "list",
            "# Another comment",
            "find 1",
            "exit",
        ])
        out = self.run_with_file(self.admin, csv_c, cmd_c)
        self.out_test("TC60: # 주석 내용 출력 안 됨", 2,
                      "This is a comment" not in out and "Another comment" not in out,
                      mode="bonus", detail=out)
        self.out_test("TC61: # 주석 줄 번호 카운트 제외 (list=1, find=2)", 2,
                      "[command file:1] list" in out and "[command file:2] find 1" in out,
                      mode="bonus", detail=out)

        self.mk3(csv_c)
        cmd_b = self.tmp("cmd_blank.txt")
        self.write_cmd(cmd_b, ["", "list", "", "find 1", "exit"])
        out = self.run_with_file(self.admin, csv_c, cmd_b)
        self.out_test("TC62: 빈 줄 번호 카운트 제외 (list=1, find=2)", 1,
                      "[command file:1] list" in out and "[command file:2] find 1" in out,
                      mode="bonus", detail=out)

    # ── advanced CSV tests (15pt) ─────────────────────────────────────────────

    def test_advanced_csv(self) -> None:
        self.section("ADV-CSV-01: 다중 add + save (3→6명) [복합] (4pt)")
        # 기본 3명에 3명 추가 → save → 6명 CSV
        csv = self.tmp("adv_csv01.csv")
        self.mk3(csv)
        cmd = self.tmp("adv_cmd01.txt")
        self.write_cmd(cmd, [
            "add 4 David 88",
            "add 5 Emma 72",
            "add 6 Frank 95",
            "save",
        ])
        self.run_with_file(self.admin, csv, cmd)
        self.check_csv(
            csv,
            str(self.exp_dir / "ADV_CSV01_multi_add" / "expected.csv"),
            4,
            "ADV-CSV-01: 기본3명 + add3명 → save → 6명 CSV 정답 일치",
            mode="advanced",
        )

        self.section("ADV-CSV-02: 혼합 CRUD + save [복합] (4pt)")
        # add David 88, delete Bob(2), update Alice(1)→95, save
        # 결과: Alice(95), Charlie(95), David(88) — Bob 제외
        csv = self.tmp("adv_csv02.csv")
        self.mk3(csv)
        cmd = self.tmp("adv_cmd02.txt")
        self.write_cmd(cmd, [
            "add 4 David 88",
            "delete 2",
            "update 1 95",
            "save",
        ])
        self.run_with_file(self.admin, csv, cmd)
        self.check_csv(
            csv,
            str(self.exp_dir / "ADV_CSV02_mixed_crud" / "expected.csv"),
            4,
            "ADV-CSV-02: add+delete+update→save → CSV 정답 일치",
            mode="advanced",
        )

        self.section("ADV-CSV-03: delete 후 동일 ID 재추가 + save [복합] (3pt)")
        # delete Charlie(3), add 3 NewGuy 77, save → ID 3이 재사용됨
        csv = self.tmp("adv_csv03.csv")
        self.mk3(csv)
        cmd = self.tmp("adv_cmd03.txt")
        self.write_cmd(cmd, [
            "delete 3",
            "add 3 NewGuy 77",
            "save",
        ])
        self.run_with_file(self.admin, csv, cmd)
        self.check_csv(
            csv,
            str(self.exp_dir / "ADV_CSV03_delete_readd" / "expected.csv"),
            3,
            "ADV-CSV-03: delete 3→add 3 NewGuy 77→save → CSV 정답 일치",
            mode="advanced",
        )

        self.section("ADV-CSV-04: 다중 update + save [복합] (2pt)")
        # 3명 모두 점수 변경: 1→50, 2→60, 3→70
        csv = self.tmp("adv_csv04.csv")
        self.mk3(csv)
        cmd = self.tmp("adv_cmd04.txt")
        self.write_cmd(cmd, [
            "update 1 50",
            "update 2 60",
            "update 3 70",
            "save",
        ])
        self.run_with_file(self.admin, csv, cmd)
        self.check_csv(
            csv,
            str(self.exp_dir / "ADV_CSV04_multi_update" / "expected.csv"),
            2,
            "ADV-CSV-04: 3×update→save → CSV 정답 일치",
            mode="advanced",
        )

        self.section("ADV-CSV-05: reload이 미저장 데이터 폐기 [복합] (2pt)")
        # add David(미저장) → reload → save → 원본 3명만 남아야 함
        # 연속성 없음: 단일 세션 내 reload로 검증
        csv = self.tmp("adv_csv05.csv")
        self.mk3(csv)
        cmd = self.tmp("adv_cmd05.txt")
        self.write_cmd(cmd, [
            "add 4 David 88",   # 메모리에만 추가, 저장 안 함
            "reload",            # 파일에서 다시 읽기 → David 사라짐
            "save",              # 원본 3명만 저장
        ])
        self.run_with_file(self.admin, csv, cmd)
        self.check_csv(
            csv,
            str(self.exp_dir / "ADV_CSV05_reload_discard" / "expected.csv"),
            2,
            "ADV-CSV-05: add(미저장)→reload→save → 원본 3명 유지",
            mode="advanced",
        )

    # ── advanced output tests (15pt) ──────────────────────────────────────────

    def test_advanced_output(self) -> None:
        self.section("ADV-OUT-01: 수정 후 stats [복합] (3pt)")
        # add David(50), update Alice(1)→50, delete Charlie(3)
        # 남은 학생: Alice(50), Bob(85), David(50) → Count:3, Min:50, Max:85
        csv = self.tmp("adv_out01.csv")
        self.mk3(csv)
        out = self.run(self.admin, csv, [
            "add 4 David 50",
            "update 1 50",
            "delete 3",
            "stats",
        ])
        self.out_test(
            "ADV-OUT-01: add/update/delete 후 stats → Count:3, Min:50, Max:85",
            3,
            "Count: 3" in out and "Min: 50" in out and "Max: 85" in out,
            mode="advanced",
            detail=out,
        )

        self.section("ADV-OUT-02: delete 후 find [복합] (2pt)")
        csv = self.tmp("adv_out02.csv")
        self.mk3(csv)
        out = self.run(self.admin, csv, ["delete 2", "find 2"])
        self.out_test(
            "ADV-OUT-02: delete 2(Bob) 후 find 2 → 'student not found'",
            2,
            "student not found" in out,
            mode="advanced",
            detail=out,
        )

        self.section("ADV-OUT-03: update 후 find [복합] (2pt)")
        csv = self.tmp("adv_out03.csv")
        self.mk3(csv)
        out = self.run(self.admin, csv, ["update 1 99", "find 1"])
        self.out_test(
            "ADV-OUT-03: update 1→99 후 find 1 → Score: 99",
            2,
            "Score: 99" in out,
            mode="advanced",
            detail=out,
        )

        self.section("ADV-OUT-04: -f 다중 에러 처리 [복합] (3pt)")
        # cmd: list(ok) / update 999 50(error) / add abc x 200(error) / find 1(ok)
        # 기대: Skipped line 2, Skipped line 3, [command file:4] find 1
        csv = self.tmp("adv_out04.csv")
        self.mk3(csv)
        cmd = self.tmp("adv_cmd_out04.txt")
        self.write_cmd(cmd, [
            "list",
            "update 999 50",
            "add abc x 200",
            "find 1",
            "exit",
        ])
        out = self.run_with_file(self.admin, csv, cmd)
        self.out_test(
            "ADV-OUT-04: -f 에러 줄 skip 후 계속 → Skipped line 2/3, [command file:4] find 1",
            3,
            "Skipped line 2" in out and "Skipped line 3" in out and
            "[command file:4] find 1" in out,
            mode="advanced",
            detail=out,
        )

        self.section("ADV-OUT-05: 경계값 stats [복합] (2pt)")
        # 기본 3명(90,85,95) + Low(0) + High(100) = 5명, 합계 370, 평균 74.0
        csv = self.tmp("adv_out05.csv")
        self.mk3(csv)
        out = self.run(self.admin, csv, [
            "add 4 Low 0",
            "add 5 High 100",
            "stats",
        ])
        self.out_test(
            "ADV-OUT-05: 경계값 stats → Count:5, Min:0, Max:100, Average:74.0",
            2,
            all(k in out for k in
                ["Count: 5", "Min: 0", "Max: 100", "Average: 74.0"]),
            mode="advanced",
            detail=out,
        )

        self.section("ADV-OUT-06: delete 후 동일 ID 재사용 [복합] (1pt)")
        csv = self.tmp("adv_out06.csv")
        self.mk3(csv)
        out = self.run(self.admin, csv, [
            "delete 2",
            "add 2 NewBob 77",
            "find 2",
        ])
        self.out_test(
            "ADV-OUT-06: delete 2→add 2 NewBob→find 2 → 'Name: NewBob'",
            1,
            "Name: NewBob" in out,
            mode="advanced",
            detail=out,
        )

        self.section("ADV-OUT-07: 전체 삭제 후 list / stats [복합] (2pt)")
        csv = self.tmp("adv_out07.csv")
        self.mk3(csv)
        out = self.run(self.admin, csv, [
            "delete 1",
            "delete 2",
            "delete 3",
            "list",
            "stats",
        ])
        self.out_test(
            "ADV-OUT-07: 전체 삭제 후 list → 'No students found'",
            1,
            "No students found" in out,
            mode="advanced",
            detail=out,
        )
        self.out_test(
            "ADV-OUT-07: 전체 삭제 후 stats → 'No student data available'",
            1,
            "No student data available" in out,
            mode="advanced",
            detail=out,
        )

    # ── summary & cleanup ─────────────────────────────────────────────────────

    def print_summary(self) -> None:
        total = self.score + self.bonus + self.advanced
        max_total = self.MAX + self.MAX_BONUS + self.MAX_ADV
        bar = "═" * 44
        dash = "─" * 44
        print(f"\n{C.BOLD}{bar}{C.RESET}")
        print(f"{C.BOLD} 필수 점수:      {self.score:4d} / {self.MAX:4d} pt{C.RESET}")
        print(f"{C.BOLD} 보너스 점수:    {self.bonus:4d} / {self.MAX_BONUS:4d} pt{C.RESET}")
        print(f"{C.BOLD} 어드밴스드:     {self.advanced:4d} / {self.MAX_ADV:4d} pt{C.RESET}")
        print(f"{C.BOLD}{dash}{C.RESET}")
        print(f"{C.BOLD} 총 점수:        {total:4d} / {max_total:4d} pt{C.RESET}")
        print(f"{C.BOLD}{bar}{C.RESET}")

    def cleanup(self) -> None:
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def run_all(self) -> None:
        try:
            if not self.check_build():
                print(f"\n{C.RED}빌드 실패. 채점을 중단합니다.{C.RESET}")
                return
            self.test_basic_csv()
            self.test_basic_output()
            self.test_bonus()
            self.test_advanced_csv()
            self.test_advanced_output()
            self.print_summary()
        finally:
            self.cleanup()


# ─── entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    is_win = platform.system() == "Windows"
    ext = ".exe" if is_win else ""
    admin    = sys.argv[1] if len(sys.argv) > 1 else f"./admin_shell{ext}"
    client   = sys.argv[2] if len(sys.argv) > 2 else f"./client_shell{ext}"
    students = sys.argv[3] if len(sys.argv) > 3 else "./students.csv"
    Grader(admin, client, students).run_all()


if __name__ == "__main__":
    main()
