#!/usr/bin/env bash
# grader.sh  –  Mini Student Shell 채점 스크립트 (Linux / macOS)
#
# 사용법:
#   chmod +x grader.sh
#   ./grader.sh [admin_path] [client_path] [students_csv]
#   기본값: ./admin_shell  ./client_shell  ./students.csv
#
# Python 3.9+ 필요
exec python3 "$(dirname "$0")/grader.py" "$@"
