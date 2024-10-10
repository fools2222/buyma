#!/usr/bin/env python
# coding: utf-8

# In[8]:


import tkinter as tk
from tkinter import filedialog, messagebox, Text
import sqlite3
import csv

# データベースの初期化（設定情報の保存用）
def init_db():
    conn = sqlite3.connect("settings.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            listing_limit INTEGER,
            listing_interval_range TEXT,
            processing_speed INTEGER,
            proxy_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 設定情報をデータベースに保存
def save_settings(listing_limit, listing_interval_range, processing_speed, proxy_url):
    conn = sqlite3.connect("settings.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO settings (listing_limit, listing_interval_range, processing_speed, proxy_url)
        VALUES (?, ?, ?, ?)
    ''', (listing_limit, listing_interval_range, processing_speed, proxy_url))
    conn.commit()
    conn.close()
    messagebox.showinfo("設定保存", "設定が保存されました。")

# メインアプリのクラス
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ログイン後のCSVファイル選択と設定管理")
        self.geometry("500x500")

        # フレームの設定
        self.frames = {}
        for F in (LoginPage, FilePage, SystemSettingsPage):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        '''指定したページを表示'''
        frame = self.frames[page_name]
        frame.tkraise()

# ログインページのフレーム
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # ユーザー名ラベルとエントリー
        tk.Label(self, text="ユーザー名").pack(pady=10)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        # パスワードラベルとエントリー
        tk.Label(self, text="パスワード").pack(pady=10)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        # ログインボタン
        login_button = tk.Button(self, text="ログイン", command=self.check_login)
        login_button.pack(pady=20)

        # ログインメッセージ表示ラベル
        self.message_label = tk.Label(self, text="")
        self.message_label.pack()

    def check_login(self):
        '''ログイン情報を確認して次のページに遷移'''
        username = self.username_entry.get()
        password = self.password_entry.get()

        # シンプルな認証（ここではユーザー名とパスワードを固定）
        if username == "user" and password == "pass":
            self.controller.show_frame("FilePage")
        else:
            self.message_label.config(text="ユーザー名またはパスワードが違います", fg="red")

# ファイル選択ページのフレーム
class FilePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # ファイル選択ボタン
        button = tk.Button(self, text="CSVファイルを開く", command=self.open_file)
        button.pack(pady=20)

        # 選択されたファイルパスを表示するラベル
        self.label = tk.Label(self, text="ファイルが選択されていません")
        self.label.pack(pady=10)

        # 選択されたCSVファイルの内容を表示するテキストウィジェット
        self.text_widget = Text(self, wrap="word", height=10)
        self.text_widget.pack(pady=10, fill="both", expand=True)

        # エラーログやステータスメッセージを表示するテキストウィジェット
        self.log_widget = Text(self, wrap="word", height=5, bg="lightgray")
        self.log_widget.pack(pady=10, fill="both", expand=True)

        # 設定ページに移動するボタン
        settings_button = tk.Button(self, text="システム設定に移動", command=lambda: controller.show_frame("SystemSettingsPage"))
        settings_button.pack(pady=10)

    def open_file(self):
        '''CSVファイルを開いて内容を表示'''
        try:
            # CSVファイル選択ダイアログを表示し、ファイルパスを取得
            file_path = filedialog.askopenfilename(
                title="CSVファイルを選択してください", 
                filetypes=[("CSVファイル", "*.csv"), ("すべてのファイル", "*.*")]
            )

            # ファイルパスをラベルに表示
            if file_path:
                self.label.config(text=f"選択されたファイル: {file_path}")

                # CSVファイルを読み込み、内容を表示
                with open(file_path, newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    self.text_widget.delete(1.0, tk.END)  # テキストウィジェットをクリア
                    for row in reader:
                        self.text_widget.insert(tk.END, ', '.join(row) + '\n')  # 各行を表示

                # 正常に読み込めた場合、ログをクリアして成功メッセージを表示
                self.log_widget.delete(1.0, tk.END)
                self.log_widget.insert(tk.END, "ファイルが正常に読み込まれました。\n")
            else:
                self.log_widget.insert(tk.END, "ファイルが選択されませんでした。\n")

        except Exception as e:
            # エラーメッセージをログウィジェットに表示
            self.log_widget.insert(tk.END, f"エラーが発生しました: {e}\n")

# システム設定ページのフレーム
class SystemSettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="自動出品制限/日").pack(pady=10)
        self.listing_limit_entry = tk.Entry(self)
        self.listing_limit_entry.pack()

        tk.Label(self, text="出品間隔範囲（秒）").pack(pady=10)
        self.listing_interval_entry = tk.Entry(self)
        self.listing_interval_entry.pack()

        tk.Label(self, text="処理速度（秒）").pack(pady=10)
        self.processing_speed_entry = tk.Entry(self)
        self.processing_speed_entry.pack()

        tk.Label(self, text="プロキシURL").pack(pady=10)
        self.proxy_url_entry = tk.Entry(self)
        self.proxy_url_entry.pack()

        # 設定保存ボタン
        save_button = tk.Button(self, text="設定を保存", command=self.save_settings)
        save_button.pack(pady=20)

    def save_settings(self):
        # 入力値を取得
        listing_limit = self.listing_limit_entry.get()
        listing_interval_range = self.listing_interval_entry.get()
        processing_speed = self.processing_speed_entry.get()
        proxy_url = self.proxy_url_entry.get()

        try:
            # 数値のバリデーションを追加
            listing_limit = int(listing_limit)
            processing_speed = int(processing_speed)

            # 出品間隔範囲のフォーマット確認（例: "100-200"）
            if '-' not in listing_interval_range:
                raise ValueError("出品間隔範囲は '100-200' の形式で入力してください。")
            interval_start, interval_end = map(int, listing_interval_range.split('-'))
            if interval_start >= interval_end:
                raise ValueError("出品間隔範囲の開始値が終了値よりも小さくなければなりません。")

            # 設定をデータベースに保存
            save_settings(listing_limit, listing_interval_range, processing_speed, proxy_url)

        except ValueError as e:
            messagebox.showerror("入力エラー", str(e))

# アプリケーションの実行
if __name__ == "__main__":
    init_db()  # データベースの初期化
    app = App()
    app.mainloop()


# In[ ]:




