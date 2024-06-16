from InquirerPy import inquirer
from InquirerPy.utils import get_style
import re
from selenium.webdriver.common.by import By


class InquirerSelect:

    def inq(
        message: str,
        choices: list,
        def_ins_mes=True,
        mandatory=True,
        multiple_select=False,
        search=False,
        confirm=False,
    ):
        if def_ins_mes:
            ins_mes = "Ana menüye dönmek için CTRL-C"
        else:
            ins_mes = " "

        keybindings = {
            "skip": [{"key": "c-c"}],
            "interrupt": [{"key": "c-d"}],
            "toggle-all": [{"key": ["c-r"]}],
        }

        style = get_style(
            {
                "marker": "orange",
                "fuzzy_border": "white",
                "pointer": "red",
                "question": "blue",
                "answer": "purple",
            }
        )
        if multiple_select:
            return inquirer.select(
                message=message,
                choices=choices,
                instruction="Tüm bölümleri seçmek için CTRL-R, Birden fazla bölüm seçmek için ise TAB, Ana menüye dönmek için CTRL-C",
                style=style,
                show_cursor=False,
                qmark="",
                amark="",
                border=True,
                mandatory=mandatory,
                mandatory_message="Bir seçenek seçmelisiniz",
                multiselect=True,
                keybindings=keybindings,
            ).execute()

        if search:
            return inquirer.fuzzy(
                message=message,
                choices=choices,
                instruction=ins_mes,
                style=style,
                qmark="",
                amark="",
                border=True,
                mandatory=mandatory,
                mandatory_message="Bir seçenek seçmelisiniz",
                multiselect=False,
                keybindings=keybindings,
                match_exact=True,
            ).execute()
        if confirm:
            return inquirer.confirm(
                message="Devam etmek istiyor musunuz?",
                default=True,
                mandatory=True,
                reject_letter="y",
                style=style,
                qmark=""
            ).execute()
        else:
            return inquirer.select(
                message=message,
                choices=choices,
                instruction=ins_mes,
                style=style,
                show_cursor=False,
                qmark="",
                amark="",
                border=True,
                mandatory=mandatory,
                mandatory_message="Bir seçenek seçmelisiniz",
                keybindings=keybindings,
            ).execute()


class NameHandler:

    def re_naming(self, name):
        pattern = re.compile(
            rf"(.+)([0-9](?:[0-9]?)(?:[0-9]?)(?:[0-9]?)). Sezon ([0-9](?:[0-9]?)(?:[0-9]?)(?:[0-9]?)). Bölüm"
        )
        try:
            groups = re.findall(pattern, name)
            return f"{groups[0][0]}S{groups[0][1]} E{groups[0][2]}"
        except IndexError:
            return name

    def filter_text(self, text) -> str:
        for i in ["?", ":"]:
            text = text.replace(i, "")
        return text

    def get_series_name(self, wait_and_find_element) -> str:
        series_name = wait_and_find_element(
            By.XPATH, "//h1[@class='title-border']"
        ).text
        return self.filter_text(series_name)
