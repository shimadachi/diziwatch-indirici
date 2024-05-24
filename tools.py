from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.utils import get_style
import re


class InquirerSelect:

    def inq(message: str, choices: list, episode_select=False):
        style = get_style(
            {
                "marker": "orange",
                "fuzzy_border": "white",
                "pointer": "red",
                "question": "blue",
                "answer": "purple",
            }
        )
        if episode_select:
            return inquirer.select(
                message=message,
                choices=choices,
                instruction="Tüm bölümleri seçmek için CTRL-R, Birden fazla bölüm seçmek için ise TAB",
                style=style,
                show_cursor=False,
                qmark="",
                amark="",
                border=True,
                mandatory=True,
                multiselect=True,
            ).execute()
        else:
            return inquirer.select(
                message=message,
                choices=choices,
                instruction=" ",
                style=style,
                show_cursor=False,
                qmark="",
                amark="",
                border=True,
                mandatory=True,
            ).execute()


class NameHandler:

    def re_naming(self, name):
        pattern = re.compile(rf"(.+)([0-9](?:[0-9]?)). Sezon ([0-9](?:[0-9]?)). Bölüm")
        try:
            groups = re.findall(pattern, name)
            return f"{groups[0][0]}S{groups[0][1]} E{groups[0][2]}"
        except IndexError:
            return name

    def filter_text(self, text) -> str:
        for i in ["?", ":"]:
            text = text.replace(i, "")
        return text