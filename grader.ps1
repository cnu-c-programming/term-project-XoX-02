# grader.ps1  –  Mini Student Shell 채점 스크립트 (Windows PowerShell)
#
# 사용법:
#   .\grader.bat [admin_path] [client_path] [students_csv]
#   또는: powershell -ExecutionPolicy Bypass -File grader.ps1 [args]
#   기본값: .\admin_shell.exe  .\client_shell.exe  .\students.csv
param(
    [string]$AdminPath   = ".\admin_shell.exe",
    [string]$ClientPath  = ".\client_shell.exe",
    [string]$StudentsCsv = ".\students.csv"
)

$SCRIPT_DIR   = Split-Path -Parent $MyInvocation.MyCommand.Path
$EXPECTED_DIR = Join-Path $SCRIPT_DIR "expected"
$COMPARE_PS1  = Join-Path $SCRIPT_DIR "compare_csv.ps1"

$script:SCORE = 0; $script:BONUS = 0; $MAX = 100; $MAX_BONUS = 15

function Write-Section([string]$t) { Write-Host ""; Write-Host "=== $t ===" -ForegroundColor Cyan }
function Pass([string]$m,[int]$p) { Write-Host "  [PASS] $m (+${p}pt)" -ForegroundColor Green; $script:SCORE+=$p }
function Fail([string]$m,[int]$p) { Write-Host "  [FAIL] $m (0/${p}pt)" -ForegroundColor Red }
function BPass([string]$m,[int]$p){ Write-Host "  [BONUS PASS] $m (+${p}pt)" -ForegroundColor Green; $script:BONUS+=$p }
function BFail([string]$m)        { Write-Host "  [BONUS FAIL] $m" -ForegroundColor Yellow }

function mk3([string]$path) {
    Set-Content -Path $path -Encoding Ascii -Value @("id,name,score","1,Alice,90","2,Bob,85","3,Charlie,95")
}

function Invoke-WithStdin([string]$exe,[string[]]$exeArgs,[string[]]$inputLines) {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName        = (Resolve-Path $exe).Path
    $psi.Arguments       = ($exeArgs | ForEach-Object { "`"$_`"" }) -join " "
    $psi.RedirectStandardInput=$true; $psi.RedirectStandardOutput=$true
    $psi.RedirectStandardError=$true; $psi.UseShellExecute=$false; $psi.CreateNoWindow=$true
    $proc = [System.Diagnostics.Process]::Start($psi)
    foreach ($l in $inputLines) { $proc.StandardInput.WriteLine($l) }
    $proc.StandardInput.Close()
    $out = $proc.StandardOutput.ReadToEnd(); $proc.WaitForExit()
    return $out -split "`r?`n"
}

function RunAdm([string]$csv,[string[]]$cmds) { Invoke-WithStdin $AdminPath  @($csv) ($cmds+@("exit")) }
function RunCli([string]$csv,[string[]]$cmds) { Invoke-WithStdin $ClientPath @($csv) ($cmds+@("exit")) }
function RunAdmF([string]$csv,[string]$f)     { Invoke-WithStdin $AdminPath  @($csv,"-f",$f) @() }

function Txt([object[]]$o)               { ($o|ForEach-Object{"$_"})-join"`n" }
function Has([object[]]$o,[string]$s)    { (Txt $o).Contains($s) }
function HasNot([object[]]$o,[string]$s) { -not (Has $o $s) }

# CSV 비교 헬퍼 호출
function Check-Csv([string]$actual,[string]$expected,[int]$pts,[string]$label) {
    $result = & powershell -ExecutionPolicy Bypass -File $COMPARE_PS1 -Actual $actual -Expected $expected 2>&1
    if ($LASTEXITCODE -eq 0) { Pass $label $pts }
    else {
        Fail $label $pts
        & powershell -ExecutionPolicy Bypass -File $COMPARE_PS1 -Actual $actual -Expected $expected
    }
}

$T = Join-Path $env:TEMP ([System.Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $T | Out-Null

try {

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "BUILD CHECK"
# ══════════════════════════════════════════════════════════════════════════════
if (-not (Test-Path $AdminPath))  { Write-Host "admin_shell.exe 없음. make admin 필요" -ForegroundColor Red; exit 1 }
if (-not (Test-Path $ClientPath)) { Write-Host "client_shell.exe 없음. make client 필요" -ForegroundColor Red; exit 1 }
if (-not (Test-Path $COMPARE_PS1)){ Write-Host "compare_csv.ps1 없음" -ForegroundColor Red; exit 1 }
Write-Host "  admin_shell, client_shell, compare_csv.ps1 : OK"

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "CSV-01: add + save [PRD §8.3, §8.1] (9pt)"
# ══════════════════════════════════════════════════════════════════════════════
mk3 "$T\csv01.csv"
Set-Content "$T\cmd_csv01.txt" -Encoding Ascii -Value @("add 4 David 88","save","exit")
RunAdmF "$T\csv01.csv" "$T\cmd_csv01.txt" | Out-Null
Check-Csv "$T\csv01.csv" "$EXPECTED_DIR\CSV01_add_save\expected.csv" 9 `
    "CSV-01: add 4 David 88 → save → CSV 정답 일치"

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "CSV-02: delete + save [PRD §8.4, §8.1] (9pt)"
# ══════════════════════════════════════════════════════════════════════════════
mk3 "$T\csv02.csv"
Set-Content "$T\cmd_csv02.txt" -Encoding Ascii -Value @("delete 2","save","exit")
RunAdmF "$T\csv02.csv" "$T\cmd_csv02.txt" | Out-Null
Check-Csv "$T\csv02.csv" "$EXPECTED_DIR\CSV02_delete_save\expected.csv" 9 `
    "CSV-02: delete 2(Bob) → save → CSV 정답 일치"

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "CSV-03: update + save [PRD §8.5, §8.1] (9pt)"
# ══════════════════════════════════════════════════════════════════════════════
mk3 "$T\csv03.csv"
Set-Content "$T\cmd_csv03.txt" -Encoding Ascii -Value @("update 1 100","save","exit")
RunAdmF "$T\csv03.csv" "$T\cmd_csv03.txt" | Out-Null
Check-Csv "$T\csv03.csv" "$EXPECTED_DIR\CSV03_update_save\expected.csv" 9 `
    "CSV-03: update 1 100(Alice) → save → CSV 정답 일치"

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "CSV-04: save → 재시작 → 데이터 유지 [PRD §8.1] (8pt)"
# ══════════════════════════════════════════════════════════════════════════════
# ※ 연속성 주의: 두 번의 별도 프로그램 실행
mk3 "$T\csv04.csv"
Set-Content "$T\cmd_csv04a.txt" -Encoding Ascii -Value @("add 4 Eve 77","save","exit")
RunAdmF "$T\csv04.csv" "$T\cmd_csv04a.txt" | Out-Null   # 세션1
Set-Content "$T\cmd_csv04b.txt" -Encoding Ascii -Value @("save","exit")
RunAdmF "$T\csv04.csv" "$T\cmd_csv04b.txt" | Out-Null   # 세션2: 재시작 후 재저장
Check-Csv "$T\csv04.csv" "$EXPECTED_DIR\CSV04_persist\expected.csv" 8 `
    "CSV-04: add Eve→save→재시작→save → CSV 정답 일치 (영속성 검증)"

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "TC01-TC05: 프로그램 시작 / 인자 처리 [PRD §3] (5pt)"
# ══════════════════════════════════════════════════════════════════════════════
mk3 "$T\s.csv"
$out = RunAdm "$T\s.csv" @()
if (Has $out "[Admin Program]") { Pass "TC01: Admin 시작 배너 '[Admin Program]'" 1 } else { Fail "TC01: Admin 시작 배너 '[Admin Program]'" 1 }

$out = RunCli "$T\s.csv" @()
if (Has $out "[Client Program]") { Pass "TC02: Client 시작 배너 '[Client Program]'" 1 } else { Fail "TC02: Client 시작 배너 '[Client Program]'" 1 }

$psi0 = New-Object System.Diagnostics.ProcessStartInfo
$psi0.FileName=(Resolve-Path $AdminPath).Path; $psi0.RedirectStandardOutput=$true
$psi0.RedirectStandardError=$true; $psi0.UseShellExecute=$false; $psi0.CreateNoWindow=$true
$p0=[System.Diagnostics.Process]::Start($psi0)
$o0=($p0.StandardOutput.ReadToEnd()+$p0.StandardError.ReadToEnd()) -split "`r?`n"; $p0.WaitForExit()
if (Has $o0 "Usage") { Pass "TC03: 인자 없을 때 'Usage' 출력" 1 } else { Fail "TC03: 인자 없을 때 'Usage' 출력" 1 }

$out = RunAdm "$T\s.csv" @()
if (Has $out "Loaded 3 students from") { Pass "TC04: 'Loaded 3 students from' 로드 메시지" 1 } else { Fail "TC04: 'Loaded 3 students from' 로드 메시지" 1 }

Set-Content "$T\bad.csv" -Value "BADHEADER" -Encoding Ascii
$out = Invoke-WithStdin $AdminPath @("$T\bad.csv") @()
if ((Has $out "Error") -or (Has $out "invalid") -or (Has $out "header")) { Pass "TC05: 잘못된 CSV 헤더 → Error 출력" 1 } else { Fail "TC05: 잘못된 CSV 헤더 → Error 출력" 1 }

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "TC07: list 빈 목록 [PRD §8.7] (2pt)"
# ══════════════════════════════════════════════════════════════════════════════
Set-Content "$T\empty.csv" -Value "id,name,score" -Encoding Ascii
$out = RunAdm "$T\empty.csv" @("list")
if (Has $out "No students found") { Pass "TC07: list 빈 목록 → 'No students found'" 2 } else { Fail "TC07: list 빈 목록 → 'No students found'" 2 }

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "TC08-TC19: add 유효성 검사 [PRD §8.3] (10pt)"
# ══════════════════════════════════════════════════════════════════════════════
mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("add 4 David 88")
if (Has $out "Student added") { Pass "TC08: add 정상 추가 → 'Student added'" 1 } else { Fail "TC08: add 정상 추가 → 'Student added'" 1 }

mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("add 1 Dup 70")
if ((Has $out "duplicate") -or (Has $out "Duplicate")) { Pass "TC09: add 중복 ID → duplicate" 1 } else { Fail "TC09: add 중복 ID → duplicate" 1 }

mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("add abc Name 80")
if (Has $out "Error") { Pass "TC10: add 비숫자 ID → Error" 1 } else { Fail "TC10: add 비숫자 ID → Error" 1 }

mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("add 0 Zero 80")
if (Has $out "Error") { Pass "TC11: add ID=0 → Error" 1 } else { Fail "TC11: add ID=0 → Error" 1 }

mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("add -5 Neg 80")
if (Has $out "Error") { Pass "TC12: add 음수 ID → Error" 1 } else { Fail "TC12: add 음수 ID → Error" 1 }

mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("add 4 David 101")
if (Has $out "Error") { Pass "TC13: add 점수 101 → Error" 1 } else { Fail "TC13: add 점수 101 → Error" 1 }

mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("add 4 David -1")
if (Has $out "Error") { Pass "TC14: add 점수 -1 → Error" 1 } else { Fail "TC14: add 점수 -1 → Error" 1 }

mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("add 4 David abc")
if (Has $out "Error") { Pass "TC15: add 비숫자 점수 → Error" 1 } else { Fail "TC15: add 비숫자 점수 → Error" 1 }

mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("add 4")
if ((Has $out "Error") -or (Has $out "missing")) { Pass "TC16-17: add 인자 부족/없음 → Error/missing" 1 } else { Fail "TC16-17: add 인자 부족/없음 → Error/missing" 1 }

mk3 "$T\s.csv"; $o18=RunAdm "$T\s.csv" @("add 4 Edge 0")
mk3 "$T\s.csv"; $o19=RunAdm "$T\s.csv" @("add 5 Edge 100")
if ((Has $o18 "Student added") -and (Has $o19 "Student added")) { Pass "TC18-19: add 경계값 0/100 정상 추가" 1 } else { Fail "TC18-19: add 경계값 0/100 정상 추가" 1 }

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "TC20-TC22: delete [PRD §8.4] (5pt)"
# ══════════════════════════════════════════════════════════════════════════════
mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("delete 2")
if (Has $out "Student deleted") { Pass "TC20: delete 정상 삭제 → 'Student deleted'" 2 } else { Fail "TC20: delete 정상 삭제 → 'Student deleted'" 2 }
mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("delete 99")
if (Has $out "student not found") { Pass "TC21: delete 미존재 → 'student not found'" 2 } else { Fail "TC21: delete 미존재 → 'student not found'" 2 }
mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("delete xyz")
if (Has $out "Error") { Pass "TC22: delete 잘못된 ID → Error" 1 } else { Fail "TC22: delete 잘못된 ID → Error" 1 }

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "TC23-TC26: update [PRD §8.5] (5pt)"
# ══════════════════════════════════════════════════════════════════════════════
mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("update 1 100")
if (Has $out "Student updated") { Pass "TC23: update 정상 수정 → 'Student updated'" 2 } else { Fail "TC23: update 정상 수정 → 'Student updated'" 2 }
mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("update 99 80")
if (Has $out "student not found") { Pass "TC24: update 미존재 → 'student not found'" 2 } else { Fail "TC24: update 미존재 → 'student not found'" 2 }
mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("update 1 abc")
if (Has $out "Error") { Pass "TC25-26: update 점수 오류 → Error" 1 } else { Fail "TC25-26: update 점수 오류 → Error" 1 }

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "TC27-TC30: find [PRD §8.6] (7pt)"
# ══════════════════════════════════════════════════════════════════════════════
mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("find 1")
if ((Has $out "ID: 1") -and (Has $out "Name: Alice") -and (Has $out "Score: 90")) { Pass "TC27: find 1 Admin → ID:1,Name:Alice,Score:90" 2 } else { Fail "TC27: find 1 Admin → ID:1,Name:Alice,Score:90" 2 }
mk3 "$T\s.csv"; $out=RunCli "$T\s.csv" @("find 2")
if ((Has $out "ID: 2") -and (Has $out "Name: Bob") -and (Has $out "Score: 85")) { Pass "TC28: find 2 Client → ID:2,Name:Bob,Score:85" 2 } else { Fail "TC28: find 2 Client → ID:2,Name:Bob,Score:85" 2 }
mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("find 99")
if (Has $out "student not found") { Pass "TC29: find 미존재 → 'student not found'" 2 } else { Fail "TC29: find 미존재 → 'student not found'" 2 }
mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("find abc")
if (Has $out "Error") { Pass "TC30: find 잘못된 ID → Error" 1 } else { Fail "TC30: find 잘못된 ID → Error" 1 }

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "TC32 + TC34-TC35: save/reload 메시지 [PRD §8.1, §8.2] (5pt)"
# ══════════════════════════════════════════════════════════════════════════════
mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("save")
if ((Has $out "Saved") -and (Has $out "students to")) { Pass "TC32: save → 'Saved N students to'" 2 } else { Fail "TC32: save → 'Saved N students to'" 2 }
Set-Content "$T\reload.csv" -Encoding Ascii -Value @("id,name,score","1,Alice,100","5,New,77")
$out=RunAdm "$T\reload.csv" @("reload")
if ((Has $out "Reloaded") -and (Has $out "from")) { Pass "TC34: reload Admin → 'Reloaded N students from'" 2 } else { Fail "TC34: reload Admin → 'Reloaded N students from'" 2 }
mk3 "$T\s.csv"; $out=RunCli "$T\s.csv" @("reload")
if (Has $out "Reloaded") { Pass "TC35: reload Client → 'Reloaded'" 1 } else { Fail "TC35: reload Client → 'Reloaded'" 1 }

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "TC36-TC38 + TC39: stats [PRD §8.8] (9pt)"
# ══════════════════════════════════════════════════════════════════════════════
mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("stats")
if ((Has $out "Count: 3") -and (Has $out "Average: 90.0") -and (Has $out "Max: 95") -and (Has $out "Min: 85")) { Pass "TC36: stats 3명 → Count:3,Average:90.0,Max:95,Min:85" 3 } else { Fail "TC36: stats 3명 → Count:3,Average:90.0,Max:95,Min:85" 3 }
Set-Content "$T\empty.csv" -Value "id,name,score" -Encoding Ascii; $out=RunAdm "$T\empty.csv" @("stats")
if (Has $out "No student data available") { Pass "TC37: stats 빈 → 'No student data available'" 1 } else { Fail "TC37: stats 빈 → 'No student data available'" 1 }
Set-Content "$T\one.csv" -Encoding Ascii -Value @("id,name,score","42,Solo,73"); $out=RunAdm "$T\one.csv" @("stats")
if ((Has $out "Count: 1") -and (Has $out "Average: 73.0") -and (Has $out "Max: 73") -and (Has $out "Min: 73")) { Pass "TC38: stats 1명 → Count:1,Avg:73.0,Max=Min=73" 2 } else { Fail "TC38: stats 1명 → Count:1,Avg:73.0,Max=Min=73" 2 }
if (Test-Path $StudentsCsv) {
    $out=RunAdm $StudentsCsv @("stats")
    if ((Has $out "Count: 100") -and (Has $out "Max: 100") -and (Has $out "Min: 54")) { Pass "TC39: stats 100명 → Count:100,Max:100,Min:54" 3 } else { Fail "TC39: stats 100명 → Count:100,Max:100,Min:54" 3 }
} else { Write-Host "  [SKIP] TC39: students.csv 없음" -ForegroundColor Yellow }

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "TC44-TC45: help [PRD §8.9] (4pt)"
# ══════════════════════════════════════════════════════════════════════════════
mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("help")
if ((Has $out "save") -and (Has $out "add") -and (Has $out "delete") -and (Has $out "update")) { Pass "TC44: help Admin → save/add/delete/update 표시" 2 } else { Fail "TC44: help Admin → save/add/delete/update 표시" 2 }
mk3 "$T\s.csv"; $out=RunCli "$T\s.csv" @("help")
if ((Has $out "find") -and (Has $out "list") -and (HasNot $out "save")) { Pass "TC45: help Client → find/list 표시, save 미표시" 2 } else { Fail "TC45: help Client → find/list 표시, save 미표시" 2 }

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "TC33 + TC49: 권한 구분 [PRD §6] (4pt)"
# ══════════════════════════════════════════════════════════════════════════════
mk3 "$T\s.csv"; $out=RunCli "$T\s.csv" @("save")
if ((Has $out "Unknown command") -or (Has $out "permission denied")) { Pass "TC33: Client save → 거부" 1 } else { Fail "TC33: Client save → 거부" 1 }
foreach ($cmd in @("add 4 David 88","delete 1","update 1 100")) {
    mk3 "$T\s.csv"; $out=RunCli "$T\s.csv" @($cmd)
    $cn=($cmd -split " ")[0]
    if ((Has $out "Unknown command") -or (Has $out "permission denied")) {
        Write-Host "  [PASS] TC49: Client '$cn' → 거부 (+1pt)" -ForegroundColor Green; $script:SCORE++
    } else { Write-Host "  [FAIL] TC49: Client '$cn' → 거부 실패 (0/1pt)" -ForegroundColor Red }
}

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "TC54-TC58: -f 명령어 파일 [PRD §3.1] (6pt)"
# ══════════════════════════════════════════════════════════════════════════════
mk3 "$T\s.csv"
Set-Content "$T\cmd54.txt" -Encoding Ascii -Value @("list","add 4 David 88","find 4","exit")
$out=RunAdmF "$T\s.csv" "$T\cmd54.txt"
if ((Has $out "[command file:1] list") -and (Has $out "[command file:2] add 4 David 88")) { Pass "TC54-55: -f 줄 번호 형식 '[command file:N] <cmd>'" 2 } else { Fail "TC54-55: -f 줄 번호 형식 '[command file:N] <cmd>'" 2 }
mk3 "$T\s.csv"
Set-Content "$T\cmd56.txt" -Encoding Ascii -Value @("list","update 99 70","find 1","exit")
$out=RunAdmF "$T\s.csv" "$T\cmd56.txt"
if ((Has $out "student not found") -and (Has $out "Skipped line 2") -and (Has $out "[command file:3] find 1")) { Pass "TC56: -f 에러 → 'Skipped line 2' 후 계속" 2 } else { Fail "TC56: -f 에러 → 'Skipped line 2' 후 계속" 2 }
mk3 "$T\s.csv"
Set-Content "$T\cmd57.txt" -Encoding Ascii -Value @("list","exit","add 4 ShouldNotRun 99")
$out=RunAdmF "$T\s.csv" "$T\cmd57.txt"
if ((Has $out "Goodbye") -and (HasNot $out "ShouldNotRun")) { Pass "TC57: -f exit 이후 처리 중단" 1 } else { Fail "TC57: -f exit 이후 처리 중단" 1 }
$psiF=New-Object System.Diagnostics.ProcessStartInfo; $psiF.FileName=(Resolve-Path $AdminPath).Path
$psiF.Arguments="`"$T\s.csv`" -f"; $psiF.RedirectStandardOutput=$true; $psiF.RedirectStandardError=$true
$psiF.UseShellExecute=$false; $psiF.CreateNoWindow=$true
$pF=[System.Diagnostics.Process]::Start($psiF)
$oF=($pF.StandardOutput.ReadToEnd()+$pF.StandardError.ReadToEnd()) -split "`r?`n"; $pF.WaitForExit(2000)|Out-Null
if ((Has $oF "Error") -or (Has $oF "Usage") -or ($pF.ExitCode -ne 0)) { Pass "TC58: -f 파일명 미지정 → 에러" 1 } else { Fail "TC58: -f 파일명 미지정 → 에러" 1 }

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "TC68 + TC70: 에러 처리 [PRD §10] (3pt)"
# ══════════════════════════════════════════════════════════════════════════════
mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("unknowncmd")
if ((Has $out "Unknown command") -or (Has $out "permission denied")) { Pass "TC68: 알 수 없는 명령 → 'Unknown command...'" 2 } else { Fail "TC68: 알 수 없는 명령 → 'Unknown command...'" 2 }
mk3 "$T\s.csv"; $out=Invoke-WithStdin $AdminPath @("$T\s.csv") @("","","list","exit")
if (Has $out "Alice") { Pass "TC70: 빈 줄 무시 → list 정상" 1 } else { Fail "TC70: 빈 줄 무시 → list 정상" 1 }

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "CSV-07: 100명 load+save 데이터 보존 [PRD §7] (8pt)"
# ══════════════════════════════════════════════════════════════════════════════
if (-not (Test-Path $StudentsCsv)) {
    Write-Host "  [SKIP] CSV-07: students.csv 없음" -ForegroundColor Yellow
} else {
    Copy-Item $StudentsCsv "$T\csv07.csv"
    Set-Content "$T\cmd_csv07.txt" -Encoding Ascii -Value @("save","exit")
    RunAdmF "$T\csv07.csv" "$T\cmd_csv07.txt" | Out-Null
    Check-Csv "$T\csv07.csv" $StudentsCsv 8 "CSV-07: students.csv(100명) load→save → 원본과 동일"
}

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "BONUS CSV-05: sort name + save (+4pt)"
# ══════════════════════════════════════════════════════════════════════════════
Copy-Item "$EXPECTED_DIR\CSV05_sort_name\input.csv" "$T\csv05.csv"
Set-Content "$T\cmd_csv05.txt" -Encoding Ascii -Value @("sort name","save","exit")
RunAdmF "$T\csv05.csv" "$T\cmd_csv05.txt" | Out-Null
$r=& powershell -ExecutionPolicy Bypass -File $COMPARE_PS1 -Actual "$T\csv05.csv" -Expected "$EXPECTED_DIR\CSV05_sort_name\expected.csv" 2>&1
if ($LASTEXITCODE -eq 0) { BPass "CSV-05: sort name → save → 알파벳 순서 CSV 정답 일치" 4 }
else { BFail "CSV-05: sort name → save → 알파벳 순서 CSV 정답 일치"
       & powershell -ExecutionPolicy Bypass -File $COMPARE_PS1 -Actual "$T\csv05.csv" -Expected "$EXPECTED_DIR\CSV05_sort_name\expected.csv" }

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "BONUS CSV-06: sort score + save (+4pt)"
# ══════════════════════════════════════════════════════════════════════════════
Copy-Item "$EXPECTED_DIR\CSV06_sort_score\input.csv" "$T\csv06.csv"
Set-Content "$T\cmd_csv06.txt" -Encoding Ascii -Value @("sort score","save","exit")
RunAdmF "$T\csv06.csv" "$T\cmd_csv06.txt" | Out-Null
$r=& powershell -ExecutionPolicy Bypass -File $COMPARE_PS1 -Actual "$T\csv06.csv" -Expected "$EXPECTED_DIR\CSV06_sort_score\expected.csv" 2>&1
if ($LASTEXITCODE -eq 0) { BPass "CSV-06: sort score → save → 점수 오름차순 CSV 정답 일치" 4 }
else { BFail "CSV-06: sort score → save → 점수 오름차순 CSV 정답 일치"
       & powershell -ExecutionPolicy Bypass -File $COMPARE_PS1 -Actual "$T\csv06.csv" -Expected "$EXPECTED_DIR\CSV06_sort_score\expected.csv" }

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "BONUS TC40 + TC43: sort 메시지/에러 (+2pt)"
# ══════════════════════════════════════════════════════════════════════════════
mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("sort name")
if (Has $out "sorted by name") { BPass "TC40: sort name → 'sorted by name'" 1 } else { BFail "TC40: sort name → 'sorted by name'" }
mk3 "$T\s.csv"; $out=RunAdm "$T\s.csv" @("sort badkey")
if (Has $out "Error") { BPass "TC43: sort badkey → Error" 1 } else { BFail "TC43: sort badkey → Error" }

# ══════════════════════════════════════════════════════════════════════════════
Write-Section "BONUS TC60-TC62: 주석/빈줄 처리 (+5pt)"
# ══════════════════════════════════════════════════════════════════════════════
mk3 "$T\s.csv"
Set-Content "$T\cmd_comment.txt" -Encoding Ascii -Value @("# This is a comment","list","# Another comment","find 1","exit")
$out=RunAdmF "$T\s.csv" "$T\cmd_comment.txt"
if ((HasNot $out "This is a comment") -and (HasNot $out "Another comment")) { BPass "TC60: # 주석 내용 출력 안 됨" 2 } else { BFail "TC60: # 주석 내용 출력 안 됨" }
if ((Has $out "[command file:1] list") -and (Has $out "[command file:2] find 1")) { BPass "TC61: 주석 줄 번호 제외 (list=1, find=2)" 2 } else { BFail "TC61: 주석 줄 번호 제외 (list=1, find=2)" }
mk3 "$T\s.csv"
Set-Content "$T\cmd_blank.txt" -Encoding Ascii -Value @("","list","","find 1","exit")
$out=RunAdmF "$T\s.csv" "$T\cmd_blank.txt"
if ((Has $out "[command file:1] list") -and (Has $out "[command file:2] find 1")) { BPass "TC62: 빈 줄 번호 제외 (list=1, find=2)" 1 } else { BFail "TC62: 빈 줄 번호 제외 (list=1, find=2)" }

} finally {
    Remove-Item -Recurse -Force $T -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "======================================" -ForegroundColor White
Write-Host " 필수 점수:   $($script:SCORE) / $MAX pt" -ForegroundColor White
Write-Host " 보너스 점수: $($script:BONUS) / $MAX_BONUS pt" -ForegroundColor White
Write-Host " 총 점수:     $($script:SCORE+$script:BONUS) / $($MAX+$MAX_BONUS) pt" -ForegroundColor White
Write-Host "======================================" -ForegroundColor White
exit $(if ($script:SCORE -eq $MAX -and $script:BONUS -eq $MAX_BONUS) { 0 } else { 1 })
