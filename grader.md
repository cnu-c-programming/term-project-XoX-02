# Mini Student Shell - Term Project 채점 기준

> 충남대학교 / 2026학년도 1학기 시스템 프로그래밍 Term Project

---

## 목차

1. [개요 — 하이브리드 채점 방식](#1-개요--하이브리드-채점-방식)
2. [빌드 및 채점 스크립트 실행 방법](#2-빌드-및-채점-스크립트-실행-방법)
3. [배점 요약표](#3-배점-요약표)
4. [CSV 비교 테스트 상세 (35점)](#4-csv-비교-테스트-상세-35점)
5. [화면 출력 테스트 상세 (65점)](#5-화면-출력-테스트-상세-65점)
6. [보너스 테스트 (15점)](#6-보너스-테스트-15점)
7. [제외된 테스트 케이스 및 이유](#7-제외된-테스트-케이스-및-이유)
8. [compare_csv 헬퍼 독립 사용법](#8-compare_csv-헬퍼-독립-사용법)
9. [students.csv 형식 요구사항](#9-studentscsv-형식-요구사항)
10. [채점 주의사항 — 대소문자 및 정확한 문자열 형식](#10-채점-주의사항--대소문자-및-정확한-문자열-형식)

---

## 1. 개요 — 하이브리드 채점 방식

이 프로젝트의 채점은 두 가지 독립적인 검증 방법을 조합한 **하이브리드(hybrid) 방식**으로 진행됩니다.

### 1차 — CSV 비교 테스트 (35점 필수)

프로그램을 실행하고 `save` 명령으로 CSV 파일을 생성한 뒤, `compare_csv.sh` / `compare_csv.bat` 헬퍼를 사용하여 생성된 CSV를 `expected/` 폴더의 정답 파일과 **행 단위로 비교**합니다.

- 헤더, 순서, 값이 정답 파일과 **완전히 일치**해야 통과
- 부분 일치는 인정하지 않으며, 한 행이라도 다르면 해당 테스트 전체 실패

### 2차 — 화면 출력 테스트 (65점 필수)

프로그램의 **터미널 출력(stdout + stderr)**을 캡처하여 필수 문자열이 포함되어 있는지, 금지 문자열이 포함되어 있지 않은지를 `grep -qF` (대소문자 구분 고정 문자열 검색)로 확인합니다.

- **필수 문자열**: 출력에 반드시 포함되어야 함 → 미포함 시 실패
- **금지 문자열**: 출력에 절대 포함되지 않아야 함 → 포함 시 실패

### 보너스 — sort 및 주석/빈 줄 처리 (최대 +15점)

sort 명령의 결과는 CSV 비교 방식으로, sort 메시지와 주석/빈 줄 처리는 화면 출력 방식으로 검증합니다.

> **채점 스크립트가 최우선 기준입니다.** 이 문서의 설명과 실제 `criteria.sh` / `criteria.bat` 코드가 다를 경우, 스크립트 코드가 기준입니다.

---

## 2. 빌드 및 채점 스크립트 실행 방법

### 빌드

```bash
# 두 바이너리 모두 빌드 (권장)
make all

# 개별 빌드
make admin    # admin_shell 생성
make client   # client_shell 생성
```

Makefile이 사용하는 컴파일 플래그:

```bash
gcc -Wall -Wextra -std=c11 -DADMIN_MODE  main.c student.c file_io.c command.c -o admin_shell
gcc -Wall -Wextra -std=c11 -DCLIENT_MODE main.c student.c file_io.c command.c -o client_shell
```

### 채점 스크립트 실행

**Linux / macOS / WSL:**

```bash
chmod +x criteria.sh
./criteria.sh
```

**Windows (PowerShell):**

```bat
criteria.bat
```

`criteria.bat`은 내부적으로 `criteria.ps1`을 호출합니다. PowerShell 실행 정책이 제한된 경우 아래 명령을 먼저 실행하세요:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 채점 스크립트 출력 형식

```
[PASS] CSV-01 (9pt): add 후 save CSV 일치
[FAIL] CSV-02 (9pt): delete 후 save CSV 일치
...
[PASS] TC08 (1pt): add 정상 추가 - "Student added"
...
필수 합계: 82 / 100
보너스 합계: 5 / 15
최종 합계: 87 / 115
```

---

## 3. 배점 요약표

| 카테고리 | 테스트 식별자 | 배점 |
|----------|-------------|------|
| **CSV 비교 테스트** | | **35점** |
| add 후 save | CSV-01 | 9점 |
| delete 후 save | CSV-02 | 9점 |
| update 후 save | CSV-03 | 9점 |
| 세션 간 영속성 | CSV-04 | 8점 |
| 100명 대용량 로드/save | CSV-07 | 8점 |
| **화면 출력 테스트** | | **65점** |
| 프로그램 시작 / 인자 처리 | TC01-TC05 | 5점 |
| `list` 명령어 | TC07 | 2점 |
| `add` 명령어 | TC08-TC19 | 12점 |
| `delete` 명령어 | TC20-TC22 | 5점 |
| `update` 명령어 | TC23-TC26 | 6점 |
| `find` 명령어 | TC27-TC30 | 7점 |
| `save` 완료 메시지 | TC32 | 2점 |
| `reload` 명령어 | TC34-TC35 | 3점 |
| `stats` 명령어 | TC36-TC39 | 8점 |
| `help` 명령어 | TC44-TC45 | 4점 |
| 권한 구분 (Client 거부) | TC33 + TC49 | 3점 |
| `-f` 명령어 파일 옵션 | TC54-TC58 | 7점 |
| 에러 처리 | TC68 + TC70 | 3점 |
| **필수 합계** | | **100점** |
| **보너스 테스트** | | |
| sort CSV 비교 | CSV-05 + CSV-06 | +8점 |
| sort 메시지 + 오류 처리 | TC40 + TC43 | +2점 |
| 주석 / 빈 줄 처리 | TC60-TC62 | +5점 |
| **보너스 합계** | | **+15점** |
| **최대 합계** | | **115점** |

> 모든 테스트는 독립적으로 채점됩니다. 한 테스트가 실패해도 나머지 테스트에 영향을 주지 않습니다.

---

## 4. CSV 비교 테스트 상세 (35점)

CSV 비교 테스트는 프로그램 실행 후 `save` 명령으로 생성된 CSV를 `expected/` 폴더의 정답 파일과 비교합니다. `compare_csv.sh` / `compare_csv.bat` 헬퍼가 사용됩니다 (섹션 8 참조).

### 기본 입력 데이터 (CSV-01 ~ CSV-04 공통)

```csv
id,name,score
1,Alice,90
2,Bob,85
3,Charlie,95
```

---

### CSV-01 — add 후 save (9점)

| 항목 | 내용 |
|------|------|
| 시작 데이터 | 3명 (Alice, Bob, Charlie) |
| 명령 시퀀스 | `add 4 David 88` → `save` |
| 정답 파일 | `expected/CSV01_add_save/expected.csv` |

**정답 CSV 내용:**

```csv
id,name,score
1,Alice,90
2,Bob,85
3,Charlie,95
4,David,88
```

**검증 포인트:** 기존 3명의 데이터가 그대로 유지되고, 새로 추가된 David(ID 4, 점수 88)가 마지막 행에 올바르게 저장되어야 합니다.

---

### CSV-02 — delete 후 save (9점)

| 항목 | 내용 |
|------|------|
| 시작 데이터 | 3명 (Alice, Bob, Charlie) |
| 명령 시퀀스 | `delete 2` (Bob 삭제) → `save` |
| 정답 파일 | `expected/CSV02_delete_save/expected.csv` |

**정답 CSV 내용:**

```csv
id,name,score
1,Alice,90
3,Charlie,95
```

**검증 포인트:** Bob(ID 2)이 삭제되고, Alice와 Charlie만 남아 있어야 합니다. 남은 학생들의 ID는 변경되지 않습니다.

---

### CSV-03 — update 후 save (9점)

| 항목 | 내용 |
|------|------|
| 시작 데이터 | 3명 (Alice, Bob, Charlie) |
| 명령 시퀀스 | `update 1 100` (Alice 점수를 100으로 변경) → `save` |
| 정답 파일 | `expected/CSV03_update_save/expected.csv` |

**정답 CSV 내용:**

```csv
id,name,score
1,Alice,100
2,Bob,85
3,Charlie,95
```

**검증 포인트:** Alice의 점수만 100으로 변경되고, Bob과 Charlie의 데이터는 변경 없이 그대로 유지되어야 합니다.

---

### CSV-04 — 세션 간 영속성 (8점)

이 테스트는 **두 번의 독립적인 프로그램 실행**으로 구성됩니다.

| 항목 | 내용 |
|------|------|
| 시작 데이터 | 3명 (Alice, Bob, Charlie) |
| 세션 1 | `add 4 Eve 77` → `save` → 프로그램 종료 |
| 세션 2 | 프로그램 재시작 → `save` |
| 정답 파일 | `expected/CSV04_persist/expected.csv` |

**정답 CSV 내용:**

```csv
id,name,score
1,Alice,90
2,Bob,85
3,Charlie,95
4,Eve,77
```

**검증 포인트:** 세션 1에서 저장된 Eve의 데이터가 세션 2 재시작 후에도 유지되어야 합니다. 세션 2에서 `save`한 결과가 정답 파일과 일치해야 하며, 이는 **세션 1의 `save`가 실제로 디스크에 기록**되었음을 검증합니다.

> **중요:** 이것은 인터-세션(inter-session) 영속성 테스트입니다. 메모리만 변경하고 파일에 쓰지 않으면 세션 2에서 Eve가 사라집니다.

---

### CSV-07 — 100명 대용량 로드/save (8점)

| 항목 | 내용 |
|------|------|
| 시작 데이터 | `students.csv` (100명) |
| 명령 시퀀스 | 프로그램 시작 즉시 `save` |
| 정답 파일 | `students.csv` 자체 (데이터 손실 없음 검증) |

**검증 포인트:** 100명 데이터를 로드한 후 아무 변경 없이 `save`했을 때, 저장된 CSV가 원본 `students.csv`와 완전히 일치해야 합니다. 100명 중 단 한 명의 데이터라도 손실되거나 변경되면 실패입니다.

---

## 5. 화면 출력 테스트 상세 (65점)

화면 출력 테스트는 `grep -qF` (대소문자 구분, 고정 문자열)로 출력을 검사합니다. 아래 표에서:

- **필수 문자열**: 출력에 반드시 포함되어야 통과
- **금지 문자열**: 출력에 포함되면 실패

달리 명시되지 않은 경우 시작 데이터는 Alice(1,90), Bob(2,85), Charlie(3,95) 3명입니다.

---

### 프로그램 시작 / 인자 처리 (5점)

| TC | 배점 | 명령 / 상황 | 필수 문자열 | 금지 문자열 |
|----|------|-----------|-----------|-----------|
| TC01 | 1 | `admin_shell` 시작 | `[Admin Program]` | — |
| TC02 | 1 | `client_shell` 시작 | `[Client Program]` | — |
| TC03 | 1 | 인자 없이 실행 | `Usage` | — |
| TC04 | 1 | 3명 CSV로 시작 | `Loaded 3 students from` | — |
| TC05 | 1 | 잘못된 CSV 헤더 | `Error` 또는 `invalid` 또는 `header` | — |

**TC01 / TC02 참고:** 대괄호 `[` `]`가 반드시 포함되어야 합니다. `Admin Program` (대괄호 없음)은 실패입니다.

**TC03 참고:** `fprintf(stderr, "Usage: ...")` 형태로 stderr에 출력해도 됩니다. 채점 스크립트는 stdout과 stderr를 모두 캡처합니다.

**TC04 참고:** `Loaded 3 students from` — 숫자 `3`과 전치사 `from`이 정확히 포함되어야 합니다. 로드한 CSV 파일명이 뒤따라 오는 형식(`Loaded 3 students from test.csv`)을 권장합니다.

**TC05 참고:** 세 문자열 중 하나만 포함되어도 통과입니다. 올바른 헤더는 `id,name,score`(소문자, 공백 없음)이며, 이 형식이 아닌 경우 오류 처리가 필요합니다.

---

### list 명령어 (2점)

| TC | 배점 | 명령 / 상황 | 필수 문자열 | 금지 문자열 |
|----|------|-----------|-----------|-----------|
| TC07 | 2 | 빈 CSV에서 `list` | `No students found` | — |

**TC07 참고:** 헤더(`id,name,score`)만 있고 데이터 행이 없는 CSV 파일을 사용합니다. `list` 명령 실행 시 학생이 없다는 메시지를 출력해야 합니다.

---

### add 명령어 (12점)

| TC | 배점 | 입력 | 필수 문자열 | 금지 문자열 |
|----|------|------|-----------|-----------|
| TC08 | 1 | `add 4 David 88` | `Student added` | — |
| TC09 | 1 | `add 1 Dup 70` (ID 1 중복) | `duplicate` 또는 `Duplicate` | — |
| TC10 | 1 | `add abc Name 80` | `Error` | — |
| TC11 | 1 | `add 0 Zero 80` | `Error` | — |
| TC12 | 1 | `add -5 Neg 80` | `Error` | — |
| TC13 | 1 | `add 4 David 101` | `Error` | — |
| TC14 | 1 | `add 4 David -1` | `Error` | — |
| TC15 | 1 | `add 4 David abc` | `Error` | — |
| TC16+17 | 1 | `add 4` 또는 `add` (인자 부족/없음) | `Error` 또는 `missing` | — |
| TC18+19 | 1 | `add 4 Edge 0` 및 `add 5 Edge 100` | `Student added` (둘 다) | — |

**TC08 참고:** 반드시 대문자 S로 시작하는 `Student added`여야 합니다. `student added`는 실패입니다.

**TC09 참고:** `duplicate` (소문자) 또는 `Duplicate` (대문자 D) 중 하나가 포함되면 통과입니다.

**TC11 참고:** ID는 반드시 1 이상의 양의 정수여야 합니다. 0은 유효하지 않은 ID입니다.

**TC18+19 참고:** 점수 0과 100은 모두 유효한 경계값입니다. 두 명령 모두 `Student added`를 출력해야 1점 획득합니다. 하나라도 거부하면 실패입니다.

---

### delete 명령어 (5점)

| TC | 배점 | 입력 | 필수 문자열 | 금지 문자열 |
|----|------|------|-----------|-----------|
| TC20 | 2 | `delete 2` (Bob 삭제) | `Student deleted` | — |
| TC21 | 2 | `delete 99` (없는 학생) | `student not found` | — |
| TC22 | 1 | `delete xyz` | `Error` | — |

**TC20 참고:** 반드시 대문자 S로 시작하는 `Student deleted`여야 합니다.

**TC21 참고:** 반드시 소문자 s로 시작하는 `student not found`여야 합니다. `Student not found`는 실패입니다. 이 문자열은 TC24, TC29에서도 동일하게 적용됩니다.

---

### update 명령어 (6점)

| TC | 배점 | 입력 | 필수 문자열 | 금지 문자열 |
|----|------|------|-----------|-----------|
| TC23 | 2 | `update 1 100` | `Student updated` | — |
| TC24 | 2 | `update 99 80` (없는 학생) | `student not found` | — |
| TC25+26 | 1 | `update 1 abc` 또는 `update 1 101` | `Error` | — |

**TC23 참고:** 반드시 대문자 S로 시작하는 `Student updated`여야 합니다.

**TC24 참고:** 소문자 s로 시작하는 `student not found`가 필요합니다.

---

### find 명령어 (7점)

| TC | 배점 | 실행 | 필수 문자열 | 금지 문자열 |
|----|------|------|-----------|-----------|
| TC27 | 2 | `admin_shell`에서 `find 1` | `ID: 1` AND `Name: Alice` AND `Score: 90` | — |
| TC28 | 2 | `client_shell`에서 `find 2` | `ID: 2` AND `Name: Bob` AND `Score: 85` | — |
| TC29 | 2 | `find 99` (없는 학생) | `student not found` | — |
| TC30 | 1 | `find abc` | `Error` | — |

**TC27 / TC28 참고:** 세 문자열 모두 출력에 포함되어야 합니다. 하나라도 빠지면 실패입니다. 형식은 `ID: 1` (콜론 후 공백 하나)이어야 하며, `ID:1` 또는 `ID : 1`은 실패입니다.

**TC28 참고:** `find`는 Client에서도 사용 가능한 조회 명령입니다.

---

### save 완료 메시지 (2점)

| TC | 배점 | 입력 | 필수 문자열 | 금지 문자열 |
|----|------|------|-----------|-----------|
| TC32 | 2 | `save` | `Saved` AND `students to` | — |

**TC32 참고:** 두 문자열 모두 포함되어야 합니다. 출력 예시: `Saved 3 students to students.csv`

> **주의:** save 명령의 파일 쓰기 결과는 CSV 비교 테스트(CSV-01 ~ CSV-04)에서 별도로 검증합니다. TC32는 오직 완료 메시지만 확인합니다.

---

### reload 명령어 (3점)

| TC | 배점 | 실행 | 필수 문자열 | 금지 문자열 |
|----|------|------|-----------|-----------|
| TC34 | 2 | `admin_shell`에서 `reload` | `Reloaded` AND `from` | — |
| TC35 | 1 | `client_shell`에서 `reload` | `Reloaded` | — |

**TC34 참고:** 두 문자열 모두 포함되어야 합니다. 출력 예시: `Reloaded 3 students from students.csv`

**TC35 참고:** `reload`는 Client에서도 사용 가능한 명령입니다.

---

### stats 명령어 (8점)

| TC | 배점 | 설정 | 필수 문자열 | 금지 문자열 |
|----|------|------|-----------|-----------|
| TC36 | 3 | Alice(90), Bob(85), Charlie(95) | `Count: 3` AND `Average: 90.0` AND `Max: 95` AND `Min: 85` | — |
| TC37 | 1 | 빈 CSV | `No student data available` | — |
| TC38 | 2 | 학생 1명: `42,Solo,73` | `Count: 1` AND `Average: 73.0` AND `Max: 73` AND `Min: 73` | — |
| TC39 | 2 | `students.csv` (100명) | `Count: 100` AND `Max: 100` AND `Min: 54` | — |

**TC36 핵심 주의사항:**
- 평균이 정수로 나누어 떨어져도 반드시 소수점 한 자리를 포함해야 합니다: `Average: 90.0` (O), `Average: 90` (X)
- 콜론과 공백 형식: `Count: 3` (O), `Count:3` 또는 `Count : 3` (X)
- 네 문자열 모두 출력에 포함되어야 3점 획득

**TC37 참고:** 헤더만 있는 빈 CSV에서 `stats` 실행 시 `No student data available`을 출력해야 합니다.

**TC38 참고:** 학생 1명일 때 평균 = 최대 = 최소가 동일합니다. `Average: 73.0`(소수점 필수), `Max: 73`, `Min: 73` 모두 필요합니다.

**TC39 참고:** `students.csv`의 최대 점수는 100, 최소 점수는 54입니다 (섹션 9 참조).

---

### help 명령어 (4점)

| TC | 배점 | 실행 | 필수 문자열 | 금지 문자열 |
|----|------|------|-----------|-----------|
| TC44 | 2 | `admin_shell`에서 `help` | `save` AND `add` AND `delete` AND `update` | — |
| TC45 | 2 | `client_shell`에서 `help` | `find` AND `list` | `save` |

**TC44 참고:** Admin help는 쓰기 명령(`save`, `add`, `delete`, `update`)을 포함한 모든 명령어를 나열해야 합니다.

**TC45 참고:** Client help는 `find`와 `list`를 포함해야 하며, `save`는 **출력에 포함되면 실패**합니다. Client는 쓰기 명령을 사용할 수 없으므로 help에도 표시하지 않아야 합니다.

---

### 권한 구분 — Client 거부 (3점)

| TC | 배점 | 실행 | 필수 문자열 | 금지 문자열 |
|----|------|------|-----------|-----------|
| TC33 | 1 | `client_shell`에서 `save` | `Unknown command` 또는 `permission denied` | — |
| TC49 | 2 | `client_shell`에서 `add`, `delete`, `update` 각각 | `Unknown command` 또는 `permission denied` | — |

**TC49 참고:** `add`, `delete`, `update` 세 명령이 모두 거부되어야 2점 획득입니다. 하나라도 실행되면 실패합니다.

---

### -f 명령어 파일 옵션 (7점)

`-f` 옵션 실행 형식: `./admin_shell <csv파일> -f <명령파일>`

명령 파일의 각 줄을 순서대로 실행하며, 실행되는 명령을 `[command file:N] <명령>` 형식으로 출력합니다.

| TC | 배점 | 명령 파일 내용 | 필수 문자열 | 금지 문자열 |
|----|------|-------------|-----------|-----------|
| TC54+55 | 2 | `list` / `add 4 David 88` / `exit` | `[command file:1] list` AND `[command file:2] add 4 David 88` | — |
| TC56 | 2 | `list` / `update 99 70` / `find 1` / `exit` | `student not found` AND `Skipped line 2` AND `[command file:3] find 1` | — |
| TC57 | 1 | `list` / `exit` / `add 4 ShouldNotRun 99` | `Goodbye` | `ShouldNotRun` |
| TC58 | 1 | `-f` 뒤 파일명 없음 | `Error` 또는 `Usage` | — |

**TC54+55 참고:** 줄 번호 뒤에 실행된 명령어 내용이 함께 출력되어야 합니다. `[command file:1]`만 있고 명령어가 없으면 실패입니다. 형식: `[command file:N] <명령>` (대괄호, 콜론, 번호, 공백 하나, 명령).

**TC56 참고:**
- `update 99 70`은 존재하지 않는 ID에 대한 명령으로 `student not found` 오류가 발생
- 오류 발생 시 `Skipped line 2`를 출력하고 다음 명령(`find 1`)을 계속 실행
- `find 1`이 줄 번호 3으로 실행되어 `[command file:3] find 1`이 출력되어야 함

**TC57 참고:** `exit` 이후의 명령(`add 4 ShouldNotRun 99`)은 처리되지 않아야 합니다. `ShouldNotRun` 문자열이 출력에 포함되면 실패입니다.

**TC58 참고:** `Error` 또는 `Usage` 출력, 또는 비정상 exit code(0이 아닌 값) 중 하나라도 해당되면 통과입니다.

---

### 에러 처리 (3점)

| TC | 배점 | 입력 | 필수 문자열 | 금지 문자열 |
|----|------|------|-----------|-----------|
| TC68 | 2 | `unknowncmd` (알 수 없는 명령어) | `Unknown command` 또는 `permission denied` | — |
| TC70 | 1 | 빈 줄 2개 후 `list` | `Alice` | — |

**TC68 참고:** Admin 또는 Client 모드 모두 존재하지 않는 명령어에 대해 `Unknown command` 또는 `permission denied`를 출력해야 합니다.

**TC70 참고:** 빈 줄(엔터만 입력)을 입력했을 때 오류 없이 무시하고 다음 입력을 기다린 뒤, `list` 명령이 정상적으로 실행되어 `Alice`가 출력되어야 합니다.

---

## 6. 보너스 테스트 (15점)

보너스 테스트는 필수 구현 사항이 아닙니다. 구현하지 않아도 100점 만점 달성이 가능합니다.

---

### CSV-05 — sort name 후 save (4점)

| 항목 | 내용 |
|------|------|
| 시작 데이터 | 비정렬 입력 (아래 참조) |
| 명령 시퀀스 | `sort name` → `save` |
| 정답 파일 | `expected/CSV05_sort_name/expected.csv` |

**시작 CSV (비정렬):**

```csv
id,name,score
3,Charlie,95
1,Alice,90
2,Bob,85
```

**정답 CSV (이름 알파벳 오름차순):**

```csv
id,name,score
1,Alice,90
2,Bob,85
3,Charlie,95
```

---

### CSV-06 — sort score 후 save (4점)

| 항목 | 내용 |
|------|------|
| 시작 데이터 | 비점수순 입력 (아래 참조) |
| 명령 시퀀스 | `sort score` → `save` |
| 정답 파일 | `expected/CSV06_sort_score/expected.csv` |

**시작 CSV (비점수순):**

```csv
id,name,score
1,Alice,90
3,Charlie,95
2,Bob,85
```

**정답 CSV (점수 오름차순):**

```csv
id,name,score
2,Bob,85
1,Alice,90
3,Charlie,95
```

---

### TC40 — sort name 메시지 (1점)

| 입력 | `sort name` |
|------|------------|
| 필수 문자열 | `sorted by name` |

---

### TC43 — sort 잘못된 키 거부 (1점)

| 입력 | `sort badkey` |
|------|--------------|
| 필수 문자열 | `Error` |

**참고:** 유효한 정렬 키는 `name`과 `score` 두 가지뿐입니다.

---

### TC60 — 주석 내용 미출력 (2점)

| 명령 파일 내용 | `# This is a comment` / `list` / `find 1` / `exit` |
|-------------|---------------------------------------------------|
| 금지 문자열 | `This is a comment` |

**참고:** `#`으로 시작하는 줄은 주석으로 처리되어 실행되지 않으며, 내용이 출력에 포함되어서는 안 됩니다.

---

### TC61 — 주석 줄이 줄 번호에서 제외 (2점)

TC60과 동일한 명령 파일 사용:

| 필수 문자열 | `[command file:1] list` AND `[command file:2] find 1` |
|-----------|------------------------------------------------------|

**핵심:** 주석 줄은 줄 번호 카운트에서 제외됩니다. 따라서 `list`가 1번, `find 1`이 2번이 됩니다. 주석을 카운트에 포함하면 `list`가 2번, `find 1`이 3번이 되어 실패합니다.

---

### TC62 — 빈 줄이 줄 번호에서 제외 (1점)

| 명령 파일 내용 | (빈 줄) / `list` / (빈 줄) / `find 1` / `exit` |
|-------------|----------------------------------------------|
| 필수 문자열 | `[command file:1] list` AND `[command file:2] find 1` |

**핵심:** 빈 줄도 줄 번호 카운트에서 제외됩니다. TC61과 동일한 번호 규칙입니다.

---

## 7. 제외된 테스트 케이스 및 이유

아래 테스트 케이스들은 이번 채점에서 제외되었습니다. 구현해도 감점되지 않으며, 일부는 다른 테스트에 의해 간접적으로 검증됩니다.

| TC | 제외 이유 |
|----|---------|
| TC06 (list 포맷) | 열 정렬/너비는 구현마다 다름. 데이터 무결성은 CSV 비교 테스트(CSV-01 ~ CSV-04)로 더 객관적으로 검증됨 |
| TC31 (save CSV 내용) | CSV 비교 테스트(CSV-01 ~ CSV-04)가 save 결과를 더 엄밀하게 검증하므로 중복 제거 |
| TC41, TC42 (sort 순서 via list) | list 출력 포맷에 의존적. 보너스 CSV-05, CSV-06이 sort 결과를 정답 파일과 직접 비교하여 더 정확하게 검증함 |
| TC46 (clear ANSI) | ESC 시퀀스(\033[2J)는 파이프를 통해 전달 시 플랫폼마다 처리 방식이 다름. 터미널 포맷 기능으로 자동화 채점 대상에서 제외 |
| TC47 (exit Goodbye) | 모든 테스트에서 exit 명령이 사용되므로 암묵적으로 검증됨. TC57에서도 `Goodbye` 포함 여부를 확인 |
| TC48 (EOF exit code) | 플랫폼 의존적 동작. Windows/Linux/macOS에서 exit code 처리 방식 차이로 자동화 채점 불안정 |
| TC53 (Admin 전체 명령 순차) | 각 명령이 개별 테스트로 검증됨. CSV 비교 테스트(CSV-01 ~ CSV-03)도 여러 명령 순차 실행을 포함하여 충분히 검증됨 |
| TC59 (exit 없는 파일 후 인터랙티브) | -f 파일과 stdin을 동시에 파이프하는 것이 플랫폼별로 불안정. 자동화 채점 부적합 |
| TC63 (add 후 list 반영) | CSV-01(add → save) 테스트가 add 후 메모리 반영 + 파일 저장까지 검증하므로 중복. 인트라-세션 메모리 일관성은 save 동작으로 확인됨 |
| TC64 (delete 후 list 반영) | CSV-02(delete → save)가 동일 기능을 검증 |
| TC65 (update 후 find 반영) | CSV-03(update → save)가 동일 기능을 검증 |
| TC66 (persistence via list) | CSV-04(세션1 save → 세션2 재시작 → save → CSV 비교)가 동일 기능을 더 명확하게 검증함 |
| TC67 (CSV 헤더 형식) | 모든 expected CSV 파일이 `id,name,score` 헤더를 포함하므로 CSV 비교 시 자동 검증됨 |
| TC69 (명령 파일 내 unknown command) | TC56(Skipped line)에서 오류 발생 시 건너뛰기가 검증됨. TC68도 unknown command를 별도로 검증함 |
| TC71 (100명 list 행 수) | list 출력 포맷(구분선, 헤더 행 등)에 의존적. CSV-07(100명 로드 → save)이 데이터 무결성을 직접 검증함 |
| TC72 (100명 stats 정확성) | TC39와 동일한 테스트. 중복 제거 |

---

## 8. compare_csv 헬퍼 독립 사용법

`compare_csv.sh` / `compare_csv.bat`은 채점 스크립트와 독립적으로 실행할 수 있는 CSV 비교 도구입니다. 학생이 자신의 구현을 제출 전에 직접 검증하는 데 사용할 수 있습니다.

### 사용 형식

**Linux / macOS / WSL:**

```bash
chmod +x compare_csv.sh
./compare_csv.sh <실제_파일.csv> <정답_파일.csv>
```

**Windows (배치 파일):**

```bat
compare_csv.bat <실제_파일.csv> <정답_파일.csv>
```

### 예시 — CSV-01 검증

```bash
# Linux
./compare_csv.sh output.csv expected/CSV01_add_save/expected.csv

# Windows
compare_csv.bat output.csv expected\CSV01_add_save\expected.csv
```

### 출력 형식

일치하는 경우:

```
CSV match: output.csv == expected/CSV01_add_save/expected.csv
```

불일치하는 경우 (행 번호별 차이 표시):

```
CSV mismatch at line 4:
  실제: 4,David,99
  정답: 4,David,88
```

### 종료 코드

| 종료 코드 | 의미 |
|---------|------|
| 0 | 두 파일이 완전히 일치 (PASS) |
| 1 | 한 행 이상 불일치 (FAIL) |

### 모든 CSV 테스트를 한 번에 확인하는 방법

```bash
# Linux — 모든 expected 폴더 순회
for dir in expected/CSV*/; do
    testname=$(basename "$dir")
    ./compare_csv.sh my_output.csv "$dir/expected.csv" && echo "[PASS] $testname" || echo "[FAIL] $testname"
done
```

---

## 9. students.csv 형식 요구사항

TC39와 CSV-07은 프로젝트 디렉토리의 `./students.csv` 파일을 직접 사용합니다. 이 파일은 학생이 직접 준비해야 합니다.

### 필수 형식

```csv
id,name,score
1,이름1,점수1
2,이름2,점수2
...
100,이름100,점수100
```

### 검증 조건

| 조건 | 요구값 |
|------|--------|
| 헤더 | 정확히 `id,name,score` (첫 줄, 소문자, 공백 없음) |
| 총 학생 수 | 100명 (ID 1 ~ 100) |
| 최고 점수 | 100점 — Zara(ID:26), Petra(ID:63), Kurt(ID:83) 중 포함 |
| 최저 점수 | 54점 — Yolanda(ID:71) |

### 채점에 사용되는 검증 명령

```
stats 결과에서 반드시 포함되어야 하는 문자열:
  Count: 100
  Max: 100
  Min: 54
```

### 주의사항

- `students.csv`가 프로젝트 디렉토리에 없으면 TC39와 CSV-07이 모두 실패합니다 (총 10점 손실)
- 헤더가 `id,name,score`가 아니면 프로그램이 오류를 출력하고 종료할 수 있습니다 (TC05 로직)
- ID는 중복 없이 1부터 100까지 연속이어야 합니다
- CSV-07은 `save` 후 파일이 원본과 동일해야 하므로, 파일에 불필요한 공백이나 개행이 있으면 비교에서 실패할 수 있습니다

---

## 10. 채점 주의사항 — 대소문자 및 정확한 문자열 형식

채점 스크립트는 `grep -qF` (고정 문자열 검색, **대소문자 구분**)를 사용합니다. 아래 표의 문자열은 **한 글자도 다르면 실패**합니다.

### 필수 출력 문자열 정확도 표

| TC | 필수 문자열 | 자주 하는 실수 |
|----|-----------|-------------|
| TC01 | `[Admin Program]` | `Admin Program` (대괄호 누락) |
| TC02 | `[Client Program]` | `Client Program` (대괄호 누락) |
| TC04 | `Loaded 3 students from` | `Loaded 3 student from` (students → student) |
| TC07 | `No students found` | `No student found` 또는 `no students found` |
| TC08, TC18, TC19 | `Student added` | `student added` (소문자 s) |
| TC20 | `Student deleted` | `student deleted` (소문자 s) |
| TC21, TC24, TC29 | `student not found` | `Student not found` (대문자 S) — 이 항목만 소문자 |
| TC23 | `Student updated` | `student updated` (소문자 s) |
| TC27 | `ID: 1` | `ID:1` 또는 `id: 1` (공백 누락 또는 소문자) |
| TC27 | `Name: Alice` | `name: Alice` (소문자 n) |
| TC27 | `Score: 90` | `score: 90` (소문자 s) |
| TC32 | `Saved` AND `students to` | `saved` 또는 `student to` |
| TC34 | `Reloaded` AND `from` | `reloaded` (소문자) |
| TC36 | `Count: 3` | `Count:3` (공백 누락) |
| TC36 | `Average: 90.0` | `Average: 90` (소수점 누락) — 가장 흔한 실수 |
| TC36 | `Max: 95` | `Max:95` (공백 누락) |
| TC36 | `Min: 85` | `Min:85` (공백 누락) |
| TC37 | `No student data available` | `No students data available` (students → student) |
| TC54+55 | `[command file:1] list` | `[command file: 1] list` (콜론 뒤 공백 삽입) |
| TC56 | `Skipped line 2` | `skipped line 2` (소문자 s) |

### 평균 출력 구현 예시

```c
// 올바른 구현 — 정수로 나누어 떨어져도 .0 출력
printf("Average: %.1f\n", (double)total / count);
```

### -f 옵션 줄 번호 구현 예시

```c
// 올바른 형식: [command file:N] <명령>
printf("[command file:%d] %s\n", line_number, command);
```

### find 출력 구현 예시

```c
// 올바른 형식: 콜론 + 공백
printf("ID: %d\n", student->id);
printf("Name: %s\n", student->name);
printf("Score: %d\n", student->score);
```

### 금지 문자열 주의 (TC45, TC57)

| TC | 금지 문자열 | 설명 |
|----|-----------|------|
| TC45 | `save` | Client help 출력에 `save`가 포함되면 실패 |
| TC57 | `ShouldNotRun` | -f 파일에서 exit 이후 명령이 실행되면 실패 |

---

> 질문은 강의 게시판에 올려주세요. 이 문서의 설명과 실제 `criteria.sh` / `criteria.bat` 코드가 다를 경우, **채점 스크립트 코드가 기준**입니다.
