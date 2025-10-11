from datetime import datetime, timedelta
from typing import Optional
import flet as ft

from auto_diary.config import DATE_FMT
from auto_diary.core.db import init_db
from auto_diary.core.diary import get_entry, upsert_entry
from auto_diary.core.screenshots import list_day_images
from auto_diary.services.autogen import generate_from_images


class AutoDiaryView:
    def __init__(self):
        init_db()

        self.page: Optional[ft.Page] = None
        self.today = datetime.now().date()
        self.yesterday = self.today - timedelta(days=1)
        self.current = self.yesterday

        # UI controls
        self.date_text: Optional[ft.Text] = None
        self.edit_tip: Optional[ft.Text] = None
        self.image_grid: Optional[ft.GridView] = None
        self.body_field: Optional[ft.TextField] = None
        self.dp: Optional[ft.DatePicker] = None

    # -------- helpers --------
    def date_str(self, d) -> str:
        return d.strftime(DATE_FMT)

    def can_edit(self, d) -> bool:
        return d == self.yesterday

    # -------- lifecycle --------
    def mount(self, page: ft.Page):
        self.page = page

        self.date_text = ft.Text(size=18, weight=ft.FontWeight.W_600)
        self.edit_tip = ft.Text(size=12, color="grey")

        prev_btn = ft.ElevatedButton("◀ 前の日", on_click=self.on_prev)
        next_btn = ft.ElevatedButton("次の日 ▶", on_click=self.on_next)
        today_btn = ft.TextButton("今日へ", on_click=self.on_today)

        self.dp = ft.DatePicker(on_change=self.on_pick_date, first_date=datetime(2020, 1, 1), last_date=datetime(2100, 1, 1))
        pick_btn = ft.ElevatedButton("日付を指定", on_click=lambda _: self.page.open(self.dp))

        header = ft.Row([
            self.date_text,
            ft.Container(width=12),
            self.edit_tip,
            ft.Container(expand=True),
            prev_btn,
            next_btn,
            today_btn,
            pick_btn,
            self.dp,
        ], alignment=ft.MainAxisAlignment.START)

        # images
        self.image_grid = ft.GridView(expand=1, runs_count=5, max_extent=180, child_aspect_ratio=1.6, spacing=8, run_spacing=8)
        image_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("スクショ", size=16, weight=ft.FontWeight.W_600),
                    self.image_grid,
                ], tight=True),
                padding=16,
            ),
            elevation=2,
        )

        # body
        self.body_field = ft.TextField(
            label="本文（前日だけ編集可）",
            multiline=True,
            min_lines=12,
            max_lines=20,
            border_radius=12,
            filled=True,
            hint_text="ここに日記を書くか、画像から自動生成ボタンを押してください",
        )

        save_btn = ft.FilledButton("保存", on_click=self.on_save)
        autogen_btn = ft.OutlinedButton("画像から自動生成", on_click=self.on_autogen)

        body_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    self.body_field,
                    ft.Row([autogen_btn, save_btn], alignment=ft.MainAxisAlignment.END),
                ], tight=True),
                padding=16,
            ),
            elevation=2,
        )

        page.add(header, ft.ResponsiveRow([ft.Column(col=12, controls=[image_card]), ft.Column(col=12, controls=[body_card])]))
        self.load_day(self.current)

    # -------- data binding --------
    def load_day(self, d):
        date_s = self.date_str(d)
        print("DB読み込み:", date_s, get_entry(date_s))
        entry = get_entry(date_s)
        imgs = list_day_images(date_s)

        # auto-gen if yesterday & empty & has images
        if d == self.yesterday:
            if entry and (entry.body.strip() == "") and imgs:
                gen = generate_from_images(date_s, imgs)
                if gen:
                    upsert_entry(date_s, gen, ai_generated=True)
                    entry = get_entry(date_s)

        if not entry:
            from ..core.diary import Entry
            entry = Entry(date=date_s, body="", ai_generated=False)

        if self.date_text:
            self.date_text.value = f"日付: {date_s}"

        if self.image_grid:
            self.image_grid.controls.clear()
            for p in imgs:
                self.image_grid.controls.append(
                    ft.Container(
                        content=ft.Image(src=str(p), width=160, height=100, fit=ft.ImageFit.COVER),
                        tooltip=p.name,
                        width=160,
                        height=110,
                        padding=5,
                        bgcolor="#00000014",
                        border_radius=8,
                    )
                )

        if self.body_field:
            self.body_field.value = entry.body
            self.body_field.read_only = not self.can_edit(d)

        if self.edit_tip:
            self.edit_tip.value = "（前日ページのみ編集可／保存は下のボタン）" if self.can_edit(d) else "（このページは編集できません）"

        if self.page:
            self.page.update()

    # -------- events --------
    def on_prev(self, _):
        self.current = self.current - timedelta(days=1)
        self.load_day(self.current)

    def on_next(self, _):
        self.current = self.current + timedelta(days=1)
        self.load_day(self.current)

    def on_today(self, _):
        self.current = self.today
        self.load_day(self.current)

    def on_pick_date(self, e: ft.ControlEvent):
        dp: ft.DatePicker = e.control
        if dp.value:
            self.current = dp.value.date()
            self.load_day(self.current)

    def on_save(self, _):
        if not self.can_edit(self.current):
            return
        body = (self.body_field.value or "").strip()
        upsert_entry(self.date_str(self.current), body, ai_generated=False)

        if self.page:
            # SnackBarを直接作成して開く
            snackbar = ft.SnackBar(content=ft.Text("保存しました"))
            self.page.overlay.append(snackbar)  # ← overlay に追加
            snackbar.open = True
            self.page.update()


    def on_autogen(self, _):
        if not self.can_edit(self.current):
            return
        date_s = self.date_str(self.current)
        imgs = list_day_images(date_s)
        if not imgs:
            if self.page:
                self.page.snack_bar = ft.SnackBar(ft.Text("この日のスクショがありません"))
                self.page.snack_bar.open = True
                self.page.update()
            return
        body = generate_from_images(date_s, imgs)
        if body and self.body_field:
            self.body_field.value = body
            self.page.update()
