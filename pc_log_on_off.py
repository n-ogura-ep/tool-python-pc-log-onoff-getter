"""Windows PCのログオン・ログオフ履歴を抽出するモジュール。

`wevtutil` コマンドでシステムイベントログ（EventID 7001: ログオン, 7002: ログオフ）を取得し、
指定した開始日から現在までの日毎のログオン・ログオフ時刻および稼働時間を CSV ファイルへ出力する。
"""

from __future__ import annotations

import datetime as dt
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

# ログオン/ログオフを表すイベントID
EVENT_ID_LOGON = 7001
EVENT_ID_LOGOFF = 7002

# 抽出対象とするイベントの説明文
TARGET_DESCRIPTIONS = [
    "カスタマー エクスペリエンス向上プログラムのユーザー ログオン通知",
    "カスタマー エクスペリエンス向上プログラムのユーザー ログオフ通知",
]

# 稼働時間の算出時に差し引く休憩時間（昼休み）
LUNCH_BREAK = dt.timedelta(hours=1)

# ログの取得・整形に使用するエンコーディング（日本語Windowsのwevtutil出力）
LOG_ENCODING = "cp932"

OUTPUT_DIR_NAME = "log_output"
LOG_TXT_NAME = "log.txt"
LOG_CSV_NAME = "log.csv"
OUTPUT_CSV_NAME = "logon_off.csv"


def _parse_date(date_str: str) -> dt.datetime:
    """ "2022 11 1" のようなスペース区切りの文字列を datetime へ変換する。"""
    year, month, day = (int(part) for part in date_str.split())
    return dt.datetime(year, month, day)


def _fetch_event_log(log_txt_path: Path) -> None:
    """`wevtutil` コマンドでログオン/ログオフのイベントログを取得しテキスト保存する。"""
    cmd = (
        "wevtutil qe system /f:text /rd:true "
        '/q:"*[*[EventID=7001 or EventID=7002]]" '
        f'> "{log_txt_path}"'
    )
    subprocess.run(cmd, shell=True)


def _convert_log_to_csv(log_txt_path: Path, log_csv_path: Path) -> None:
    """wevtutilの出力テキストを整形し、CSV形式へ変換する。"""
    with (
        log_txt_path.open("r", encoding=LOG_ENCODING) as f_in,
        log_csv_path.open("w", encoding=LOG_ENCODING) as f_out,
    ):
        f_out.write("row_No,Date,Time,Event ID,Description\n")
        in_description = False
        for i, row in enumerate(f_in, start=1):
            if "Date" in row:
                date_part = row.strip()[6:]
                date_ = date_part[:10]
                time_ = date_part[11:19]
                f_out.write(f"{i},{date_},{time_},")
            elif "Event ID" in row:
                f_out.write(f"{row.strip()[10:]},")
            elif "Description" in row:
                in_description = True
            elif in_description:
                f_out.write(row.strip() + "\n")
                in_description = False


def _load_and_filter_events(
    log_csv_path: Path, start_day: dt.datetime, end_day: dt.datetime
) -> pd.DataFrame:
    """CSVを読み込み、対象イベントかつ指定期間内の行に絞り込む。"""
    df = pd.read_csv(log_csv_path, encoding=LOG_ENCODING)
    df = df[df["Description"].isin(TARGET_DESCRIPTIONS)].copy()
    df["Date"] = pd.to_datetime(df["Date"])
    return df[(df["Date"] >= start_day) & (df["Date"] <= end_day)]


def _summarize_day(day_df: pd.DataFrame) -> tuple[object, object, object]:
    """1日分のイベントから、ログオン時刻・ログオフ時刻・稼働時間を求める。"""
    logon_times = day_df.loc[day_df["Event ID"] == EVENT_ID_LOGON, "Time"]
    logoff_times = day_df.loc[day_df["Event ID"] == EVENT_ID_LOGOFF, "Time"]

    logon = logon_times.min() if not logon_times.empty else np.nan
    logoff = logoff_times.max() if not logoff_times.empty else np.nan

    operating_time: object = np.nan
    if isinstance(logon, str) and isinstance(logoff, str):
        try:
            operating_time = (
                dt.datetime.strptime(logoff, "%H:%M:%S")
                - dt.datetime.strptime(logon, "%H:%M:%S")
                - LUNCH_BREAK
            )
        except ValueError:
            operating_time = np.nan

    return logon, logoff, operating_time


def _write_summary_csv(df: pd.DataFrame, save_csv_path: Path) -> None:
    """日毎に集計したログオン・ログオフ・稼働時間をCSVへ出力する。

    1日中にPCを一時的にシャットダウンすることも想定し、
    その日最も早い時刻をログオン、最も遅い時刻をログオフとして扱う。
    """
    with save_csv_path.open("w", encoding="utf-8") as f:
        f.write("date,logon,logoff,operating_time\n")
        for date_, day_df in df.groupby("Date"):
            logon, logoff, operating_time = _summarize_day(day_df)
            row = [date_.date().strftime("%Y/%m/%d"), logon, logoff, operating_time]
            f.write(",".join(map(str, row)) + "\n")


def get_log(start_date: str) -> None:
    """指定した開始日から現在までのログオン・ログオフ履歴を抽出しCSVへ保存する。

    Args:
        start_date: "2022 11 1" のようなスペース区切りの日付文字列。
    """
    start_day = _parse_date(start_date)
    end_day = dt.datetime.now()
    print("start day:", start_day)
    print("end day:", end_day)

    save_dir = Path.cwd() / OUTPUT_DIR_NAME
    save_dir.mkdir(parents=True, exist_ok=True)
    print("log output:", save_dir)

    log_txt_path = save_dir / LOG_TXT_NAME
    log_csv_path = save_dir / LOG_CSV_NAME
    save_csv_path = save_dir / OUTPUT_CSV_NAME

    _fetch_event_log(log_txt_path)
    _convert_log_to_csv(log_txt_path, log_csv_path)

    df = _load_and_filter_events(log_csv_path, start_day, end_day)
    _write_summary_csv(df, save_csv_path)

    log_txt_path.unlink(missing_ok=True)
    log_csv_path.unlink(missing_ok=True)


if __name__ == "__main__":
    user_input = input("開始日を入力下さい。スペース区切り。 例) 2022 11 1 \n")
    get_log(user_input)
