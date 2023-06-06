import tkinter as tk
from tkinter import scrolledtext
import requests
import json
import webbrowser
import random
from PIL import ImageTk, Image
class DateCourseApp:
    def __init__(self, window):
        self.window = window
        self.window.title("데이트 코스 추천 프로그램")
        self.window.geometry("800x600")

        # 배경 이미지 설정
        self.background_image = ImageTk.PhotoImage(Image.open("image.png"))
        self.background_label = tk.Label(self.window, image=self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.locations = set()  # 지역 정보를 저장할 set

        self.create_widgets()

    def create_widgets(self):
        # 프로그램 이름
        program_name_label = tk.Label(self.window, text="데이트 코스 추천 프로그램", font=("Arial", 16, "bold"))
        program_name_label.pack(pady=10)
        program_name_label.config(bg=self.window.cget("bg"))

        # 옵션 프레임
        option_frame = tk.Frame(self.window)
        option_frame.pack(pady=10)

        # 테마 선택을 위한 OptionMenu
        theme_label = tk.Label(option_frame, text="테마 선택:", font=("Arial", 14))
        theme_label.pack(side=tk.LEFT)

        self.theme_var = tk.StringVar(self.window)
        self.theme_var.set("")  # 초기 선택값은 빈 문자열로 설정

        self.theme_option_menu = tk.OptionMenu(option_frame, self.theme_var, "맛집", "카페",command=self.update_location_menu)
        self.theme_option_menu.config(width=7, highlightbackground='white')  # 배경 색상 변경
        self.theme_option_menu.pack(side=tk.LEFT, padx=(20, 10))

        # 지역 선택을 위한 OptionMenu
        location_label = tk.Label(option_frame, text="지역 선택:", font=("Arial", 14))
        location_label.pack(side=tk.LEFT)

        self.location_var = tk.StringVar(self.window)
        self.location_var.set("")  # 초기 선택값은 빈 문자열로 설정

        self.location_menu = tk.OptionMenu(option_frame, self.location_var, "", *self.locations)
        self.location_menu.config(width=12, highlightbackground='white')  # 배경 색상 변경
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

        self.result_text = scrolledtext.ScrolledText(result_frame, height=15, width=30)  # 폭 조정
        self.result_text.pack(side=tk.LEFT, padx=(0, 5), pady=5, anchor=tk.NW)
        self.result_text.config(font=("Arial", 12))

        self.address_text = scrolledtext.ScrolledText(result_frame, height=15, width=40)  # 폭 조정
        self.address_text.pack(side=tk.LEFT, pady=5, anchor=tk.NW)
        self.address_text.config(font=("Arial", 12))

        # 리스트 칸을 오른쪽으로 이동
        result_frame.pack_configure(anchor=tk.CENTER)

    def update_location_menu(self, theme):
        # 테마 선택에 따라 모든 지역을 가져옴
        self.get_all_locations(theme)

        # 지역 선택 OptionMenu 업데이트
        self.location_menu['menu'].delete(0, 'end')  # 기존 메뉴 삭제
        for location in self.locations:
            full_location = f"{location}"
            self.location_menu['menu'].add_command(label=full_location, command=lambda loc=location: self.update_location(loc))

    def get_all_locations(self, theme):
        # 선택한 테마에 따라 URL 선택
        if theme == "맛집":
            url = "https://openapi.gg.go.kr/Genrestrtstandpub?KEY=073a67dd2f404141bda409a5cf579366&pIndex=1&Type=json"
        elif theme == "카페":
            url = "https://openapi.gg.go.kr/Genrestrtcate?KEY=34d47489070244e2ac22cc1d11fedad0&pIndex=1&Type=json"
        else:
            # 다른 테마에 대한 처리 추가 가능
            return

        response = requests.get(url)
        data = response.json()

        # API 응답이 유효한지 확인
        if "Genrestrtstandpub" not in data and "Genrestrtcate" not in data:
            return

        # 선택한 테마에 따라 적절한 키 추출
        if theme == "맛집":
            key = "Genrestrtstandpub"
        elif theme == "카페":
            key = "Genrestrtcate"

        # API 응답에서 지역 정보 추출하여 set에 추가
        self.locations.clear()
        for row in data[key][1]['row']:
            refine_lotno_addr = row['REFINE_LOTNO_ADDR']
            location = refine_lotno_addr.split()[1]  # 주소에서 두 번째 단어를 지역 정보로 가정 (ex. 경기도 xx시)
            self.locations.add(location)

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

            # 가게 정보를 클릭했을 때 이벤트 처리를 위한 바인딩
            self.result_text.tag_bind(tk.END, "<Button-1>",
                                      lambda event, name=name, address=address: self.show_selected_restaurant(name,
                                                                                                              address))

    def show_selected_restaurant(self, name, address):
        # 선택된 가게 정보를 오른쪽 리스트에 표시
        self.selected_restaurant_text.delete(1.0, tk.END)
        self.selected_restaurant_text.insert(tk.END, f"가게명: {name}\n주소: {address}\n")

    def update_location(self, location):
        self.location_var.set(location)

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

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    window = tk.Tk()
    app = DateCourseApp(window)
    app.run()