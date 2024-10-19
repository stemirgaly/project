import flet


answers = [

    ["1) Python", "2) JavaScript", "3) C++"],
    {
        "question": "Какой фреймворк используется для создания веб-приложений на Python?\n1) React\n2) Django\n3) Laravel",
        "correct_answer": "2"
    },
    {
        "question": "Какая библиотека используется для работы с нейронными сетями в Python?\n1) NumPy\n2) TensorFlow\n3) Flask",
        "correct_answer": "2"
    }
]


async def main(page: flet.Page):
    page.title = "Easy Learn"
    page.theme_mode = flet.ThemeMode.LIGHT
    page.vertical_alignment = flet.MainAxisAlignment.CENTER
    page.horizontal_alignment = flet.CrossAxisAlignment.CENTER
    page.fonts = {'TimesNewRoman': "pythonProject7/TimesNewRoman.ttf"}
    page.theme = flet.Theme(font_family='TimesNewRoman')

    score = flet.Text(value="0", size=50, data=0)
    progress_bar = flet.ProgressBar(
        value=0,
        width=page.width - 30,
        bar_height=10,
        color="ff8b1f",
        bgcolor="ffffff"
    )

    await page.add_async(score, progress_bar)

    async def complete():
        def close_banner(e):
            page.close(banner)
            page.add(flet.Text("Action clicked: " + e.control.text))

        action_button_style = flet.ButtonStyle(color=flet.colors.BLUE)
        banner = flet.Banner(
            bgcolor=flet.colors.AMBER_100,
            leading=flet.Icon(flet.icons.WARNING_AMBER_ROUNDED, color=flet.colors.AMBER, size=40),
            content=flet.Text(
                value="Oops, there were some errors while trying to delete the file. What would you like me to do?",
                color=flet.colors.BLACK,
            ),
            actions=[
                flet.TextButton(text="Retry", style=action_button_style, on_click=close_banner),
                flet.TextButton(text="Ignore", style=action_button_style, on_click=close_banner),
                flet.TextButton(text="Cancel", style=action_button_style, on_click=close_banner),
            ],
        )
        await page.add_async(banner)  # Добавляем баннер асинхронно
        await page.open_async(banner)  # Открываем баннер асинхронно

    def handle_change(e):
        print(e.data[2])
        if e.data[2] == 1:
            page.create_task(complete())  # Запускаем асинхронную функцию

    await page.add_async(
        flet.SegmentedButton(
            on_change=handle_change,
            selected_icon=flet.Icon(flet.icons.ONETWOTHREE),
            allow_multiple_selection=False,
            allow_empty_selection=True,
            selected=[],
            segments=[
                flet.Segment(
                    value="1",
                    label=flet.Text(answers[0][0]),
                    icon=flet.Icon(flet.icons.LOOKS_ONE),
                ),
                flet.Segment(
                    value="2",
                    label=flet.Text(answers[0][1]),
                    icon=flet.Icon(flet.icons.LOOKS_TWO),
                ),
                flet.Segment(
                    value="3",
                    label=flet.Text(answers[0][2]),
                    icon=flet.Icon(flet.icons.LOOKS_3),
                ),
                flet.Segment(
                    value="4",
                    label=flet.Text("4"),
                    icon=flet.Icon(flet.icons.LOOKS_4),
                ),
            ],
        )
    )


if __name__ == "__main__":
    flet.app(target=main)
