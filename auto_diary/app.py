from datetime import datetime
import flet as ft
from auto_diary.ui.main_view import AutoDiaryView



def main(page: ft.Page):
    page.title = "AutoDiary — 前日ビュー"
    page.window_width = 1000
    page.window_height = 700
    page.theme_mode = "dark" # for compatibility
    page.padding = 16


    view = AutoDiaryView()
    view.mount(page)




if __name__ == "__main__":
    ft.app(target=main)