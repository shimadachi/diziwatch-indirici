import tkinter as tk
from tkinter import filedialog
from os import system
from rich.console import Console
import sys
from site_interaction import Api
from tools import InquirerSelect
from download_episodes import Video
import configparser
from InquirerPy.base.control import Choice
from termcolor import colored
import selenium.common.exceptions

console = Console()
clear_console = lambda: system("cls")
api = Api()


class Config:
    def __init__(
        self,
    ):
        self.cfg = configparser.ConfigParser()
        self.read_and_check_config()

    def create_config(self):
        print(colored("Config dosyayı oluşturuluyor", "light_red"))
        self.cfg["GENERAL"] = {"default_folder": "Yok", "re_naming": "Kapali"}
        with open("config.ini", "w") as configfile:
            self.cfg.write(configfile)
            self.read_and_check_config()

    def read_and_check_config(self):
        try:
            self.cfg.read("config.ini")
            self.default_folder = self.cfg["GENERAL"]["default_folder"]
            self.re_naming = self.cfg["GENERAL"]["re_naming"]
        except (configparser.Error, KeyError):
            self.create_config()


def quit_program():
    with console.status(
        "[green] Çıkış yapılıyor", spinner="point", spinner_style="white"
    ):
        api.driver_quit()
        sys.exit(0)


def folder_select():
    with console.status(" :open_file_folder: [green]İndirme yapılacak klasörü seçin"):

        root = tk.Tk()
        root.withdraw()
        folder = filedialog.askdirectory()

        if folder == "":
            raise FileNotFoundError
        return folder


cfg = Config()


def settings():
    cfg.read_and_check_config()
    choice = InquirerSelect.inq(
        message="Ayarlar",
        choices=[
            Choice(value=2, name=f"Yeniden İsimlendirme : {cfg.re_naming}"),
            Choice(value=1, name=f"Varsayılan Klasör: {cfg.default_folder}"),
        ],
        mandatory=False,
    )
    if not choice:
        pass

    if choice == 1:
        cfg.default_folder = folder_select()
        with open("config.ini", "w") as config:
            cfg.cfg["GENERAL"]["default_folder"] = cfg.default_folder
            cfg.cfg.write(config)

    if choice == 2:
        with open("config.ini", "w") as config:
            if cfg.re_naming == "Kapali":
                re_naming_controller = "Acik"
            else:
                re_naming_controller = "Kapali"
            cfg.cfg["GENERAL"]["re_naming"] = re_naming_controller
            cfg.cfg.write(config)


def starter():
    clear_console()
    with console.status(
        "[green] Webdriver Başlatılıyor", spinner="point", spinner_style="white"
    ):
        api.driver_start()

    while True:
        clear_console()
        choice = InquirerSelect.inq(
            message="Seçenekler",
            choices=["Anime/Dizi indir", "Ayarlar", "Çıkış yap"],
            mandatory=False,
            def_ins_mes=False,
        )

        if choice == "Anime/Dizi indir":
            cfg.read_and_check_config()
            if cfg.default_folder == "Yok":
                folder_selected = folder_select()
            else:
                folder_selected = cfg.default_folder
            api.go_site()
            try:
                api.go_series()
                links = api.get_episode_links()
            except (
                AssertionError,
                KeyboardInterrupt,
                selenium.common.exceptions.InvalidArgumentException,
            ):
                continue
            video = Video(api)
            try:
                video.download_episodes(links, folder_selected, cfg.re_naming)
            except KeyboardInterrupt:
                continue

        if choice == "Ayarlar":
            settings()

        if choice == "Çıkış yap":
            quit_program()
            break


if __name__ == "__main__":
    starter()
