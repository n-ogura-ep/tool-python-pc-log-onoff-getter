import tkinter as tk
from tkinter import messagebox
from pc_log_on_off import get_log


def run_get_log():
    start_date = entry.get()

    if not start_date.strip():
        messagebox.showerror("エラー", "開始日を入力してください（例: 2022 11 1）")
        return

    try:
        get_log(start_date)
        messagebox.showinfo("完了", "ログの取得と保存が完了しました。")

    except Exception as e:
        messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{e}")


root = tk.Tk()
root.title("ログ取得ツール")
root.geometry("300x150")

label = tk.Label(root, text="開始日を入力（例: 2022 11 1）:")
label.pack(pady=5)

entry = tk.Entry(root, width=30)
entry.pack(pady=5)

button = tk.Button(root, text="ログ取得開始", command=run_get_log)
button.pack(pady=10)

root.mainloop()
