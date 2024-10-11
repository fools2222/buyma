#!/usr/bin/env python
# coding: utf-8

# In[3]:


import customtkinter as ctk
import sqlite3
import csv
import random  # ランダムな値を生成するためのモジュール
import tkinter.ttk as ttk

# データベースの初期化（設定情報の保存用）
def init_db():
    conn = sqlite3.connect("settings.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            listing_limit INTEGER,
            listing_interval_min INTEGER,
            listing_interval_max INTEGER,
            processing_speed_min INTEGER,
            processing_speed_max INTEGER,
            proxy_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 設定情報をデータベースに保存
def save_settings(listing_limit, listing_interval_min, listing_interval_max, processing_speed_min, processing_speed_max, proxy_url):
    conn = sqlite3.connect("settings.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO settings (listing_limit, listing_interval_min, listing_interval_max, processing_speed_min, processing_speed_max, proxy_url)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (listing_limit, listing_interval_min, listing_interval_max, processing_speed_min, processing_speed_max, proxy_url))
    conn.commit()
    conn.close()

# メインアプリのクラス
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BUYMA自動出品ツール　ver1.00")
        self.geometry("600x500")

        # タブビューを作成
        self.tabview = ctk.CTkTabview(self, width=500, height=500)
        self.tabview.pack(expand=True, fill="both")

        # タブの追加
        self.main_tab = self.tabview.add("メイン画面")
        self.login_tab = self.tabview.add("ログイン")
        self.settings_tab = self.tabview.add("システム設定")

        # 各タブのUIを設定
        self.create_main_tab()
        self.create_login_tab()
        self.create_settings_tab()

    def create_main_tab(self):
        '''メイン画面のUIをセットアップ'''
        # ファイルパスを表示するテキストボックス
        self.textbox = ctk.CTkEntry(master=self.main_tab, placeholder_text="CSV ファイルを選択", width=120)
        self.textbox.grid(row=0, column=0, padx=10, pady=(0, 0), sticky="ew")

        # ファイル選択ボタン
        self.button_select = ctk.CTkButton(master=self.main_tab, 
                                           fg_color="transparent", border_width=2, 
                                           text_color=("gray10", "#DCE4EE"), 
                                           command=self.button_select_callback, 
                                           text="ファイル選択")
        self.button_select.grid(row=0, column=1, padx=10, pady=(0, 0))

        # 結果表示用のテーブルを作成
        columns = ("ステータス", "エラー数", "商品名")
        self.table = ttk.Treeview(self.main_tab, columns=columns, show="headings", height=10)

        # 各列のヘッダー設定
        self.table.heading("ステータス", text="ステータス")
        self.table.heading("エラー数", text="エラー数")
        self.table.heading("商品名", text="商品名")

        # 各列の幅を設定
        self.table.column("ステータス", width=100, anchor="center")
        self.table.column("エラー数", width=100, anchor="center")
        self.table.column("商品名", width=300, anchor="w")

        # テーブルの配置
        self.table.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # 行のリサイズを許可する（特にログ用テキストエリアの行）
        self.main_tab.grid_rowconfigure(2, weight=1)  # テキストエリアの行がリサイズされるように

        # ログ表示用のテキストエリアを追加
        self.log_textbox = ctk.CTkTextbox(master=self.main_tab, height=10, wrap="word")
        self.log_textbox.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # ボタン行のレイアウト調整
        self.main_tab.grid_columnconfigure(0, weight=1)
        self.main_tab.grid_columnconfigure(1, weight=1)
        self.main_tab.grid_columnconfigure(2, weight=1)

        # ラジオボタンの変数
        self.mode_var = ctk.StringVar(value="下書きモード")

        # ラジオボタン「下書きモード」
        self.draft_mode_radio = ctk.CTkRadioButton(master=self.main_tab, text="下書きモード", variable=self.mode_var, value="下書きモード")
        self.draft_mode_radio.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        # ラジオボタン「出品モード」
        self.listing_mode_radio = ctk.CTkRadioButton(master=self.main_tab, text="出品モード", variable=self.mode_var, value="出品モード")
        self.listing_mode_radio.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        # 実行ボタン（右側に配置）
        self.button_run = ctk.CTkButton(master=self.main_tab, command=self.button_open_callback, text="実行")
        self.button_run.grid(row=3, column=2, padx=10, pady=10, sticky="ew")

    def button_select_callback(self):
        '''ファイル選択ダイアログを開いて、選択されたファイルパスをテキストボックスに表示'''
        file_name = ctk.filedialog.askopenfilename(filetypes=[("CSV ファイル", "*.csv")])
        if file_name:
            self.textbox.delete(0, "end")
            self.textbox.insert(0, file_name)

    def button_open_callback(self):
        '''選択されたCSVファイルを開いて表示'''
        selected_mode = self.mode_var.get()  # 選択されたモードを取得
        self.log_textbox.insert("end", f"{selected_mode}が選択されました。\n")

        file_name = self.textbox.get()
        if file_name:
            try:
                with open(file_name, newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        status = "成功"
                        error_count = 0
                        self.table.insert("", "end", values=(status, error_count, ', '.join(row)))
                    # 成功メッセージをログに追加
                    self.log_textbox.insert("end", "CSVファイルの処理が正常に完了しました。\n")
            except Exception as e:
                # エラーメッセージをログに追加
                self.log_textbox.insert("end", f"エラーが発生しました: {e}\n")
        else:
            self.log_textbox.insert("end", "ファイルが選択されていません。\n")

    def create_login_tab(self):
        '''ログイン画面のUIをセットアップ'''
        ctk.CTkLabel(self.login_tab, text="email").grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.username_entry = ctk.CTkEntry(self.login_tab)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew", columnspan=2)

        ctk.CTkLabel(self.login_tab, text="パスワード").grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.password_entry = ctk.CTkEntry(self.login_tab, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew", columnspan=2)

        login_button = ctk.CTkButton(self.login_tab, text="ログイン", command=self.check_login)
        login_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.message_label = ctk.CTkLabel(self.login_tab, text="")
        self.message_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

    def check_login(self):
        '''ログイン情報を確認'''
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == "user" and password == "pass":
            self.message_label.configure(text="ログイン成功", text_color="green")
        else:
            self.message_label.configure(text="ユーザー名またはパスワードが違います", text_color="red")

    def create_settings_tab(self):
        '''システム設定タブのUIをセットアップ'''
        self.settings_tab.grid_columnconfigure(0, weight=1)
        self.settings_tab.grid_columnconfigure(1, weight=1)
        self.settings_tab.grid_columnconfigure(2, weight=1)

        # 自動出品制限/日のラベルとエントリー
        ctk.CTkLabel(self.settings_tab, text="自動出品制限/日").grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.listing_limit_entry = ctk.CTkEntry(self.settings_tab)
        self.listing_limit_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew", columnspan=2)

        # 出品間隔範囲（最小・最大）のラベルとエントリー
        ctk.CTkLabel(self.settings_tab, text="出品間隔範囲（秒）").grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        self.listing_interval_min_entry = ctk.CTkEntry(self.settings_tab, placeholder_text="最小")
        self.listing_interval_min_entry.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")
        self.listing_interval_max_entry = ctk.CTkEntry(self.settings_tab, placeholder_text="最大")
        self.listing_interval_max_entry.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="ew")

        # 処理速度範囲（最小・最大）のラベルとエントリー
        ctk.CTkLabel(self.settings_tab, text="処理速度（秒）").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.processing_speed_min_entry = ctk.CTkEntry(self.settings_tab, placeholder_text="最小")
        self.processing_speed_min_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        self.processing_speed_max_entry = ctk.CTkEntry(self.settings_tab, placeholder_text="最大")
        self.processing_speed_max_entry.grid(row=2, column=2, padx=10, pady=10, sticky="ew")

        # プロキシURLのラベルとエントリー
        ctk.CTkLabel(self.settings_tab, text="プロキシURL").grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.proxy_url_entry = ctk.CTkEntry(self.settings_tab, placeholder_text="example@email.com")
        self.proxy_url_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew", columnspan=2)

        # 保存ボタン
        save_button = ctk.CTkButton(self.settings_tab, text="設定を保存", command=self.save_settings)
        save_button.grid(row=4, column=0, columnspan=3, pady=20, sticky="ew")

    def save_settings(self):
        '''設定を保存'''
        listing_limit = self.listing_limit_entry.get()
        listing_interval_min = self.listing_interval_min_entry.get()
        listing_interval_max = self.listing_interval_max_entry.get()
        processing_speed_min = self.processing_speed_min_entry.get()
        processing_speed_max = self.processing_speed_max_entry.get()
        proxy_url = self.proxy_url_entry.get()

        try:
            listing_limit = int(listing_limit)
            listing_interval_min = int(listing_interval_min)
            listing_interval_max = int(listing_interval_max)
            processing_speed_min = int(processing_speed_min)
            processing_speed_max = int(processing_speed_max)

            if listing_interval_min >= listing_interval_max:
                raise ValueError("出品間隔範囲の最小値が最大値以上です")
            if processing_speed_min >= processing_speed_max:
                raise ValueError("処理速度範囲の最小値が最大値以上です")

            save_settings(listing_limit, listing_interval_min, listing_interval_max, processing_speed_min, processing_speed_max, proxy_url)

        except ValueError as e:
            ctk.messagebox.showerror("入力エラー", str(e))

# アプリケーションの実行
if __name__ == "__main__":
    init_db()  # データベースの初期化
    ctk.set_appearance_mode("dark")  # アプリのスタイル設定
    app = App()
    app.mainloop()


# In[ ]:




