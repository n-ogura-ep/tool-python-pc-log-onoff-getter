"""ログオン・ログオフ抽出ツールのGUIエントリーポイント。"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from pc_log_on_off import get_log

WINDOW_TITLE = "ログ取得ツール"
WINDOW_SIZE = "300x150"


def run_get_log(entry: tk.Entry) -> None:
    """入力された開始日をもとにログを取得し、結果をダイアログで表示する。"""
    start_date = entry.get().strip()

    if not start_date:
        messagebox.showerror("エラー", "開始日を入力してください（例: 2022 11 1）")
        return

    try:
        get_log(start_date)
        messagebox.showinfo("完了", "ログの取得と保存が完了しました。")
    except Exception as e:
        messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{e}")


def main() -> None:
    """GUIウィンドウを構築し、イベントループを開始する。"""
    root = tk.Tk()
    root.title(WINDOW_TITLE)
    root.geometry(WINDOW_SIZE)

    label = tk.Label(root, text="開始日を入力（例: 2022 11 1）:")
    label.pack(pady=5)

    entry = tk.Entry(root, width=30)
    entry.pack(pady=5)

    button = tk.Button(root, text="ログ取得開始", command=lambda: run_get_log(entry))
    button.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
