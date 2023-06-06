import tkinter as tk
import requests
import json
from tkinter import scrolledtext
import webbrowser
import random

class DateCourseApp:
    def __init__(self, window):
        self.window = window
        self.window.title("데이트 코스 추천 프로그램")
        self.window.geometry("800x600")
        self.window.configure(bg="light blue")

        self.locations = set()  # 지역 정보를 저장할 set

        self.recommendations = []  # 추천된 가게들을 저장할 리스트

        self.create_widgets()

    def run(self):
        self.window.mainloop()

    def create_widgets(self):
        # 프로그램 이름
        program_name_label = tk.Label(self.window, text="데이트 코스 추천 프로그램", font=("Arial", 16, "bold"))
        program_name_label.pack(pady=10)

        # 옵션 프레임
        option_frame = tk.Frame(self.window)
        option_frame.pack(pady=10)

        # 테마 선택을 위한 OptionMenu
        theme_label = tk.Label(option_frame, text="테마 선택:", font=("Arial", 14), bg="light blue")
        theme_label.pack(side=tk.LEFT)

        self.theme_var = tk.StringVar(self.window)
        self.theme_var.set("")  # 초기 선택값은 빈 문자열로 설정

        self.theme_option_menu = tk.OptionMenu(option_frame, self.theme_var, "맛집", "카페", command=self.update_location_menu)
        self.theme_option_menu.config(width=10)
        self.theme_option_menu.pack(side=tk.LEFT, padx=(20, 10))

        # 지역 선택을 위한 OptionMenu
        location_label = tk.Label(option_frame, text="지역 선택:", font=("Arial", 14), bg="light blue")
        location_label.pack(side=tk.LEFT)

        self.location_var = tk.StringVar(self.window)
        self.location_var.set("")  # 초기 선택값은 빈 문자열로 설정

        self.location_menu = tk.OptionMenu(option_frame, self.location_var, "", *self.locations)
        self.location_menu.config(width=15)
        self.location_menu.pack(side=tk.LEFT)

        # 검색 버튼
        search_button = tk.Button(option_frame, text="검색", font=("Arial", 14), command=self.get_restaurants)
        search_button.pack(side=tk.LEFT, padx=(10, 0))

        # 랜덤 추천 버튼
        random_button = tk.Button(option_frame, text="랜덤 추천", font=("Arial", 14), command=self.random_recommend)
        random_button.pack(side=tk.LEFT, padx=(10, 0))

        # 결과를 출력할 텍스트 상자
        result_frame = tk.Frame(self.window)
        result_frame.pack(padx=10, pady=10, anchor=tk.NW)

        self.result_text = scrolledtext.ScrolledText(result_frame, height=20, width=30)
        self.result_text.pack(side=tk.LEFT, padx=10, pady=5, anchor=tk.NW)
        self.result_text.config(font=("Arial", 12))

        self.address_text = scrolledtext.ScrolledText(result_frame, height=20, width=50)
        self.address_text.pack(side=tk.LEFT, padx=10, pady=5, anchor=tk.NW)
        self.address_text.config(font=("Arial", 12))

        # 추천된 가게 저장 버튼
        save_button = tk.Button(option_frame, text="저장", font=("Arial", 14), command=self.save_recommendations)
        save_button.pack(side=tk.LEFT, padx=(10, 0))

        # 추천된 가게 취소 버튼
        cancel_button = tk.Button(option_frame, text="취소", font=("Arial", 14), command=self.cancel_recommendations)
        cancel_button.pack(side=tk.LEFT, padx=(10, 0))

        # 저장된 가게 리스트 텍스트 상자
        saved_frame = tk.Frame(self.window)
        saved_frame.pack(padx=10, pady=10, anchor=tk.NW)

        saved_label = tk.Label(saved_frame, text="저장된 가게 리스트:", font=("Arial", 14), bg="light blue")
        saved_label.pack(anchor=tk.NW)

        self.saved_text = scrolledtext.ScrolledText(saved_frame, height=10, width=50)
        self.saved_text.pack(padx=10, pady=5, anchor=tk.NW)
        self.saved_text.config(font=("Arial", 12))

    def update_location(self, location):
        self.location_var.set(location)

    def get_restaurants(self):
        selected_location = self.location_var.get()

        # 선택한 테마에 따라 URL 선택
        if self.theme_var.get() == "맛집":
            url = f"https://openapi.gg.go.kr/Genrestrtstandpub?KEY=073a67dd2f404141bda409a5cf579366&pIndex=1&Type=json&SIGUN_NM={selected_location}"
        elif self.theme_var.get() == "카페":
            url = f"https://openapi.gg.go.kr/Genrestrtcate?KEY=34d47489070244e2ac22cc1d11fedad0&pIndex=1&Type=json&SIGUN_NM={selected_location}"
        else:
            # 다른 테마에 대한 처리 추가 가능
            return

        response = requests.get(url)
        data = response.json()

        # API 응답이 유효한지 확인
        if "Genrestrtstandpub" not in data and "Genrestrtcate" not in data:
            return

        # 선택한 테마에 따라 적절한 키 추출
        if self.theme_var.get() == "맛집":
            key = "Genrestrtstandpub"
        elif self.theme_var.get() == "카페":
            key = "Genrestrtcate"

        # 결과 초기화
        self.result_text.delete(1.0, tk.END)
        self.address_text.delete(1.0, tk.END)

        # API 응답에서 가게 정보 추출하여 결과 텍스트 상자에 추가
        for row in data[key][1]['row']:
            name = row['BIZPLC_NM']
            address = row['REFINE_LOTNO_ADDR']
            self.result_text.insert(tk.END, f"- {name}\n")
            self.address_text.insert(tk.END, f"- {address}\n")

    def random_recommend(self):
        selected_location = self.location_var.get()

        # 선택한 테마와 위치에 따라 추천 가게 선택
        if self.theme_var.get() == "맛집":
            url = f"https://openapi.gg.go.kr/Genrestrtstandpub?KEY=073a67dd2f404141bda409a5cf579366&pIndex=1&Type=json&SIGUN_NM={selected_location}"
        elif self.theme_var.get() == "카페":
            url = f"https://openapi.gg.go.kr/Genrestrtcate?KEY=34d47489070244e2ac22cc1d11fedad0&pIndex=1&Type=json&SIGUN_NM={selected_location}"
        else:
            # 다른 테마에 대한 처리 추가 가능
            return

        response = requests.get(url)
        data = response.json()

        # API 응답이 유효한지 확인
        if "Genrestrtstandpub" not in data and "Genrestrtcate" not in data:
            return

        # 선택한 테마에 따라 적절한 키 추출
        if self.theme_var.get() == "맛집":
            key = "Genrestrtstandpub"
        elif self.theme_var.get() == "카페":
            key = "Genrestrtcate"

        # API 응답에서 가게 정보 추출하여 랜덤하게 선택
        rows = data[key][1]['row']
        if len(rows) > 0:
            random_row = random.choice(rows)
            name = random_row['BIZPLC_NM']
            address = random_row['REFINE_LOTNO_ADDR']

            # 결과 텍스트 상자에 선택된 가게 정보 추가
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, name)

            # 주소 텍스트 상자에 선택된 가게의 주소 추가
            self.address_text.delete(1.0, tk.END)
            self.address_text.insert(tk.END, address)

    def save_recommendations(self):
        if len(self.recommendations) == 0:
            return

        file = open("recommendations.txt", "a")

        for restaurant in self.recommendations:
            file.write(f"{restaurant['name']}\n")
            file.write(f"{restaurant['address']}\n")
            file.write("\n")

        file.close()
        self.recommendations = []

        self.load_saved_recommendations()

    def cancel_recommendations(self):
        self.recommendations = []
        self.load_saved_recommendations()

    def load_saved_recommendations(self):
        file = open("recommendations.txt", "r")
        saved_data = file.read()
        file.close()

        self.saved_text.delete("1.0", tk.END)
        self.saved_text.insert(tk.END, saved_data)

    def open_website(self, event):
        selected_text = self.saved_text.get(tk.SEL_FIRST, tk.SEL_LAST)
        selected_lines = selected_text.split("\n")

        if len(selected_lines) < 2:
            return

        url = selected_lines[1]
        webbrowser.open_new(url)


if __name__ == "__main__":
    window = tk.Tk()
    app = DateCourseApp(window)
    app.run()
