import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import requests
import folium
import threading
import sys
import json
import webbrowser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
from PIL import ImageTk, Image
from cefpython3 import cefpython as cef
class DateCourseApp:
    def __init__(self, window):
        self.window = window
        self.window.title("데이트 코스 추천 프로그램")
        self.window.geometry("800x600")

        # 배경 이미지 설정
        self.background_image = ImageTk.PhotoImage(Image.open("C:/Users/user/OneDrive - 한국산업기술대학교/바탕 화면/image.png"))
        self.background_label = tk.Label(self.window, image=self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.locations = set()  # 지역 정보를 저장할 set

        self.create_widgets()
        # 메모장 칸을 추가하기 위한 함수 호출
        self.create_memo_pad()
        self.restaurants = {}  # 가게 이름과 주소를 저장하는 딕셔너리

    def search_restaurant(self):
        # 왼쪽 텍스트 상자에서 선택된 번호 가져오기
        selected_number = self.result_text.get("current linestart", "current lineend")
        selected_number = selected_number.strip()

        # 선택된 번호에 해당하는 가게 정보 표시
        self.show_selected_restaurant(selected_number)

        keyword = self.search_entry.get()  # 검색어 가져오기

        # 검색 결과를 저장할 리스트
        search_results = []

        # 검색어와 일치하는 가게를 찾아 검색 결과에 추가
        for name, address in self.restaurants.items():
            if keyword.lower() in name.lower():
                search_results.append((name, address))

    def create_widgets(self):
        # 프로그램 이름
        program_name_label = tk.Label(self.window, text="DATE COURSE", font=("Bauhaus 93", 35, "bold"))
        program_name_label.pack(pady=10)
        program_name_label.config(bg=self.window.cget("bg"))
        program_name_label.configure(bg='light pink')

        # 옵션 프레임
        option_frame = tk.Frame(self.window)
        option_frame.pack(pady=10)
        option_frame.configure(bg='light pink')

        # 테마 선택을 위한 OptionMenu
        theme_label = tk.Label(option_frame, text="테마 선택:", font=("맑은 고딕", 14))
        theme_label.pack(side=tk.LEFT)
        theme_label.configure(bg='light pink')
        self.theme_var = tk.StringVar(self.window)

        self.theme_var.set("")  # 초기 선택값은 빈 문자열로 설정

        self.theme_option_menu = tk.OptionMenu(option_frame, self.theme_var, "맛집", "카페", "영화", command=self.update_location_menu)
        self.theme_option_menu.config(width=7, highlightbackground='light pink')  # 배경 색상 변경
        self.theme_option_menu.configure(bg='white')
        self.theme_option_menu.pack(side=tk.LEFT, padx=(20, 10))

        # 지역 선택을 위한 OptionMenu
        location_label = tk.Label(option_frame, text="지역 선택:", font=("맑은 고딕", 14))
        location_label.configure(bg='light pink')
        location_label.pack(side=tk.LEFT)

        self.location_var = tk.StringVar(self.window)
        self.location_var.set("")  # 초기 선택값은 빈 문자열로 설정

        self.location_menu = tk.OptionMenu(option_frame, self.location_var, "", *self.locations)
        self.location_menu.config(width=12, highlightbackground='light pink')  # 배경 색상 변경
        self.location_menu.configure(bg='white')
        self.location_menu.pack(side=tk.LEFT)

        # 검색 버튼
        search_button = tk.Button(option_frame, text="검색", font=("맑은 고딕", 14), command=self.get_restaurants)
        search_button.pack(side=tk.LEFT, padx=(10, 0))
        search_button.configure(bg='pink')

        # 랜덤 추천 버튼
        random_button = tk.Button(option_frame, text="랜덤 추천", font=("맑은 고딕", 14), command=self.random_recommend)
        random_button.pack(side=tk.LEFT, padx=(10, 0))
        random_button.configure(bg='pink')

        # 결과를 출력할 텍스트 상자
        result_frame = tk.Frame(self.window)
        result_frame.pack(padx=10, pady=10, anchor=tk.CENTER)
        result_frame.configure(bg='light pink')

        self.result_text = scrolledtext.ScrolledText(result_frame, height=15, width=25)  # 폭 조정
        self.result_text.pack(side=tk.LEFT, padx=(0, 5), pady=5, anchor=tk.CENTER)
        self.result_text.config(font=("맑은 고딕", 12))

        self.address_text = scrolledtext.ScrolledText(result_frame, height=15, width=35)  # 폭 조정
        self.address_text.pack(side=tk.LEFT, pady=5, anchor=tk.CENTER)
        self.address_text.config(font=("맑은 고딕", 12))

    def save_course(self):
        course = self.result_text.get(1.0, tk.END).strip()  # 결과 텍스트 상자의 내용을 가져와서 공백 제거
        if course:
            self.saved_courses.append(course)
            messagebox.showinfo("저장 완료", "코스가 저장되었습니다.")

    def update_location_menu(self, theme):
        # 테마 선택에 따라 모든 지역을 가져옴
        if theme == "맛집":
            key = "Genrestrtstandpub"
        elif theme == "카페":
            key = "Genrestrtcate"
        elif theme == "영화":
            key = "MovieTheater"
        else:
            return

        self.locations = set()  # 지역 정보를 저장할 집합(set)을 초기화합니다.
        self.get_all_locations(theme, key)  # 모든 지역 정보를 가져옵니다.

        # 지역 선택 OptionMenu 업데이트
        self.location_menu['menu'].delete(0, 'end')  # 기존 메뉴 삭제
        for location in self.locations:
            full_location = f"{location}"
            self.location_menu['menu'].add_command(label=full_location,
                                                   command=lambda loc=location: self.update_location(loc))

    def get_all_locations(self, theme, key):
        # 선택한 테마에 따라 URL 선택
        if theme == "맛집":
            url = "https://openapi.gg.go.kr/Genrestrtstandpub?KEY=073a67dd2f404141bda409a5cf579366&pIndex=1&Type=json"
        elif theme == "카페":
            url = "https://openapi.gg.go.kr/Genrestrtcate?KEY=34d47489070244e2ac22cc1d11fedad0&pIndex=1&Type=json"
        elif theme == "영화":
            url = "https://openapi.gg.go.kr/MovieTheater?KEY=20706406f12c4505bdfa0997a06f939a&pIndex=1&Type=json"
        else:
            # 다른 테마에 대한 처리 추가 가능
            return

        response = requests.get(url)
        data = response.json()

        # API 응답이 유효한지 확인
        if key not in data:
            return

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
        elif self.theme_var.get() == "영화":
            url = f"https://openapi.gg.go.kr/MovieTheater?KEY=20706406f12c4505bdfa0997a06f939a&pIndex=1&Type=json&SIGUN_NM={selected_location}"
        else:
            # 다른 테마에 대한 처리 추가 가능
            return

        response = requests.get(url)
        data = response.json()

        # API 응답이 유효한지 확인
        if "Genrestrtstandpub" not in data and "Genrestrtcate" not in data and "MovieTheater" not in data:
            return

        # 선택한 테마에 따라 적절한 키 추출
        if self.theme_var.get() == "맛집":
            key = "Genrestrtstandpub"
        elif self.theme_var.get() == "카페":
            key = "Genrestrtcate"
        elif self.theme_var.get() == "영화":
            key = "MovieTheater"

        # 결과 초기화
        self.result_text.delete(1.0, tk.END)
        self.address_text.delete(1.0, tk.END)

        # API 응답에서 가게 정보 추출하여 결과 텍스트 상자에 추가
        counter = 1
        for row in data[key][1]['row']:
            name = row['BIZPLC_NM']
            address = row['REFINE_LOTNO_ADDR']
            self.result_text.insert(tk.END, f"{counter}. {name}\n\n")
            self.address_text.insert(tk.END, f"{counter}. {address}\n\n")
            counter += 1

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
        elif self.theme_var.get() == "영화":
            url = f"https://openapi.gg.go.kr/MovieTheater?KEY=20706406f12c4505bdfa0997a06f939a&pIndex=1&Type=json&SIGUN_NM={selected_location}"
        else:
            # 다른 테마에 대한 처리 추가 가능
            return

        response = requests.get(url)
        data = response.json()

        # API 응답이 유효한지 확인
        if "Genrestrtstandpub" not in data and "Genrestrtcate" not in data and "MovieTheater" not in data:
            return

        # 선택한 테마에 따라 적절한 키 추출
        if self.theme_var.get() == "맛집":
            key = "Genrestrtstandpub"
        elif self.theme_var.get() == "카페":
            key = "Genrestrtcate"
        elif self.theme_var.get() == "영화":
            key = "MovieTheater"

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

    def create_memo_pad(self):
        # 메모 프레임
        memo_frame = tk.Frame(self.window)
        memo_frame.pack(pady=10)
        memo_frame.configure(bg='pink')

        # 메모 제목 레이블
        memo_label = tk.Label(memo_frame, text="메모", font=("맑은 고딕", 14))
        memo_label.pack(side=tk.LEFT, padx=(0, 10))
        memo_label.configure(bg='pink')

        # 메모장 칸
        self.memo_text = tk.Text(memo_frame, height=8, width=40)
        self.memo_text.pack(side=tk.LEFT)
        self.memo_text.configure(bg='white')

        # 저장 버튼
        save_button = tk.Button(memo_frame, text="저장", font=("맑은 고딕", 14), command=self.save_memo)
        save_button.pack(side=tk.LEFT, padx=(10, 0))
        save_button.configure(bg='light pink')

        # 취소 버튼
        cancel_button = tk.Button(memo_frame, text="취소", font=("맑은 고딕", 14), command=self.cancel_memo)
        cancel_button.pack(side=tk.LEFT, padx=(10, 0))
        cancel_button.configure(bg='light pink')

        # 지도 및 그래프 버튼 프레임
        map_graph_button_frame = tk.Frame(memo_frame)
        map_graph_button_frame.pack(side=tk.LEFT)
        map_graph_button_frame.configure(bg='light pink')

        # 지도 버튼
        map_button = tk.Button(map_graph_button_frame, text="지도", font=("맑은 고딕", 20), command=self.open_map)
        map_button.pack(side=tk.LEFT, padx=10)
        map_button.configure(bg='light pink')

        # 그래프 버튼
        graph_button = tk.Button(map_graph_button_frame, text="그래프", font=("맑은 고딕", 20), command=self.open_graph)
        graph_button.pack(side=tk.LEFT, padx=10)
        graph_button.configure(bg='light pink')

    def showMap(frame):
        global browser
        sys.excepthook = cef.ExceptHook
        window_info = cef.WindowInfo(frame.winfo_id())
        window_info.SetAsChild(frame.winfo_id(), [0, 0, 800, 600])
        cef.Initialize()
        browser = cef.CreateBrowserSync(window_info, url='file:///map.html')
        cef.MessageLoop()
    def open_map(self):
        location = self.memo_text.get("1.0", tk.END).strip()  # 메모장의 내용을 가져옵니다.
        if location:
            url = 'https://www.google.com/maps/search/' + location
            webbrowser.open_new_tab(url)
        else:
            # 메모장이 비어있을 경우에 대한 처리
            messagebox.showinfo("알림", "메모 내용을 입력해주세요.")
    def save_memo(self):
        # 메모장 칸의 내용을 가져와서 저장하는 기능을 구현할 수 있습니다.
        memo = self.memo_text.get("1.0", tk.END)
        # 메모 저장에 대한 추가적인 동작을 원하신다면 여기에 작성할 수 있습니다.
        # 저장 확인 메시지 박스
        messagebox.showinfo("저장 완료", "메모가 저장되었습니다.")
        # 메모장 내용 저장
        memo_content = self.memo_text.get(1.0, tk.END)
        with open("memo.txt", "w") as file:
            file.write(memo_content)

    def cancel_memo(self):
        # 메모 취소 시 메모장 초기화
        self.memo_text.delete("1.0", tk.END)

    def open_graph(self):
        memo_content = self.memo_text.get("1.0", tk.END).strip()  # 메모장의 내용을 가져옵니다.
        if not memo_content:
            messagebox.showinfo("알림", "메모 내용을 입력해주세요.")
            return

        url_restaurant = "https://openapi.gg.go.kr/Genrestrtstandpub"
        api_key_restaurant = "073a67dd2f404141bda409a5cf579366"
        restaurant_data = self.get_data_from_api(memo_content, url_restaurant, api_key_restaurant)
        if not restaurant_data:
            messagebox.showinfo("데이터 오류", "맛집 데이터를 가져오는 중 오류가 발생했습니다.")
            return

        url_cafe = "https://openapi.gg.go.kr/Genrestrtcate"
        api_key_cafe = "34d47489070244e2ac22cc1d11fedad0"
        cafe_data = self.get_data_from_api(memo_content, url_cafe, api_key_cafe)
        if not cafe_data:
            messagebox.showinfo("데이터 오류", "카페 데이터를 가져오는 중 오류가 발생했습니다.")
            return

        url_theater = "https://openapi.gg.go.kr/MovieTheater"
        api_key_theater = "20706406f12c4505bdfa0997a06f939a"
        theater_data = self.get_data_from_api(memo_content, url_theater, api_key_theater)
        if not theater_data:
            messagebox.showinfo("데이터 오류", "영화관 데이터를 가져오는 중 오류가 발생했습니다.")
            return

        try:
            sigun_nm_list = [item['SIGUN_NM'] for item in restaurant_data]  # SIGUN_NM 데이터 추출
            restaurant_count_list = [item['RESTAURANT_COUNT'] for item in restaurant_data]  # 맛집 개수 데이터 추출
            cafe_count_list = [item['CAFE_COUNT'] for item in cafe_data]  # 카페 개수 데이터 추출
            theater_count_list = [item['THEATER_COUNT'] for item in theater_data]  # 영화관 개수 데이터 추출
        except KeyError:
            messagebox.showinfo("데이터 오류", "데이터 처리 중 오류가 발생했습니다.")
            return

        # 그래프 생성
        plt.figure(figsize=(10, 6))
        plt.bar(sigun_nm_list, restaurant_count_list, label='맛집 개수')
        plt.bar(sigun_nm_list, cafe_count_list, label='카페 개수')
        plt.bar(sigun_nm_list, theater_count_list, label='영화관 개수')
        plt.xlabel('지역')
        plt.ylabel('개수')
        plt.title('지역별 맛집, 카페, 영화관 개수 그래프')
        plt.xticks(rotation=45)
        plt.legend()

        # 그래프를 이미지 파일로 저장
        plt.savefig('graph.png')

    def get_data_from_api(self, keyword, api_url, api_key):
        params = {
            "KEY": api_key,
            "pIndex": 1,
            "Type": "json",
            "SIGUN_NM": keyword
        }
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'row' in data:
                return data['row']
        return None

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    window = tk.Tk()
    app = DateCourseApp(window)
    app.run()
