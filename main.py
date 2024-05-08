from site_interaction import Api
import questionary as qa
import tkinter as tk
from tkinter import filedialog
from os import system
from rich.console import Console
import sys

qa_style = qa.Style(
    [
        ("question", "fg:#cd2adc bold"),
        ("text", " fg:#23d1e3"),
        ("answer", "fg:#23d1e3"),
        ("pointer", "fg:#fd0000"),
    ]
)

console = Console()


clear_console = lambda: system("cls")

with console.status(
    "[green] Webdriver Baslatiliyor", spinner="point", spinner_style="white"
):
    api = Api()


def program(folder):

    api.go_site()
    
    api.go_series()

    links = api.get_episode_links()

    api.download_series(links, folder)


def quit_program():
    with console.status(
        "[green] Cikis yapiliyor", spinner="point", spinner_style="white"
    ):
        api.driver_quit()
        sys.exit(0)


folder_selected = None


def folder_select():
    if folder_selected == None:
        with console.status("Indirme yapilacak klasoru secin"):
            root = tk.Tk()
            root.withdraw()
            folder = filedialog.askdirectory()

        if folder == "":
            raise FileNotFoundError
        return folder
    else:
        pass


try:
    while True:
        # Cancelled by user degisecek

        choice = qa.select(
            message="Secenekler",
            choices=["Anime/Dizi indir", "Cikis yap"],
            qmark="",
            instruction=" ",
            style=qa_style,
        ).ask()

        if choice == None:
            raise KeyboardInterrupt

        if choice == "Anime/Dizi indir":
            if folder_selected == None:
                folder_selected = folder_select()
            else:
                print(folder_selected)
            print(f"Indirilecek klasor --> {folder_selected}")
            program(folder_selected)
            clear_console()

        if choice == "Cikis yap":
            quit_program()
            break


except (KeyboardInterrupt, EOFError, FileNotFoundError):
    quit_program()
