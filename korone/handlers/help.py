# This file is part of Korone (Telegram Bot)
# Copyright (C) 2021 AmanoTeam

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import html

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

from korone.handlers import COMMANDS_HELP

help_text = "Por favor, selecione uma categoria para obter ajuda!"

start_text = """
Oi <b>{}</b>!

Eu sou o <b>{}</b>, um korone interativo que adora participar de grupos! ^^
"""

about_text = """
🚮 <b>PyKorone</b> é um korone criado por diversão para o grupo <b>Spam-Therapy</b>.
Seu foco é trazer funções legais e um design funcional com tecnologia e criatividade.

📦 Powered by <a href='https://docs.pyrogram.org/'>Pyrogram</a> with <a href='https://github.com/usernein/pyromod'>Pyromod</a>.

🗂 <b>Links:</b> <a href='https://github.com/AmanoTeam/PyKorone'>GitHub</a> | <a href='https://t.me/SpamTherapy'>Chat</a>
"""


@Client.on_message(filters.cmd(command="about", action="Informações sobre o korone."))
async def about_cmd(c: Client, m: Message):
    await m.reply_text(about_text, disable_web_page_preview=True)


@Client.on_message(
    filters.cmd(command="start", action="Envia a mensagem de inicialização do Bot.")
)
async def start(c: Client, m: Message):
    query = m.text.split()
    if len(query) > 1:
        field = query[1]
        query = field.split("_")
        if query[0] == "help":
            module = query[1]
            await help_module(m, module)
    else:
        keyboard = []
        text = (start_text).format(m.from_user.first_name, c.me.first_name)
        if m.chat.type == "private":
            keyboard.append([("📚 Ajuda", "help_cb"), ("ℹ️ Sobre", "about")])
            keyboard.append([("👥 Grupo Off-Topic", "https://t.me/SpamTherapy", "url")])
        else:
            keyboard.append(
                [
                    (
                        "Clique aqui para obter ajuda!",
                        f"http://t.me/{c.me.username}?start",
                        "url",
                    )
                ]
            )
            text += (
                "Você pode ver tudo que eu posso fazer clicando no koroneão abaixo..."
            )
        await m.reply_text(
            text,
            reply_markup=c.ikb(keyboard),
        )


@Client.on_message(filters.cmd("help (?P<module>.+)"))
async def help_m(c: Client, m: Message):
    module = m.matches[0]["module"]
    if m.chat.type == "private":
        await help_module(m, module)
    else:
        keyboard = [
            [("Ir ao PM", f"https://t.me/{c.me.username}/?start=help_{module}", "url")]
        ]
        await m.reply_text(
            text="Para ver isso, vá ao meu PM.", reply_markup=c.ikb(keyboard)
        )


@Client.on_message(
    filters.cmd(command="help", action="Envia o menu de ajuda do Bot.")
    & filters.private
)
async def help(c: Client, m: Message):
    await help_module(c, m)


@Client.on_callback_query(filters.regex("^help_cb$"))
async def help_cb(c: Client, m: CallbackQuery):
    await help_module(c, m)


async def help_module(c: Client, m: Message, module: str = None):
    is_query = isinstance(m, CallbackQuery)
    text = ""
    keyboard = []
    success = False
    if not module or module == "start":
        keyboard.append([("Comandos", "help_commands"), ("Filtros", "help_filters")])
        keyboard.append([("⬅️ Voltar", "start_back")])
        text = "Por favor, selecione uma categoria para obter ajuda!"
        success = True
    else:
        if module in ["commands", "filters"]:
            text = "Escolha um módulo ou use <code>/help &lt;módulo&gt;</code>.\n"
            keyboard = [[]]
            index = 0
            for key, value in COMMANDS_HELP.items():
                if module in value and "help" in value and value["help"]:
                    if len(keyboard[index]) == 3:
                        index += 1
                        keyboard.append([])
                    keyboard[index].append(
                        (
                            value["name"] if "name" in value else key.capitalize(),
                            f"help_{key}",
                        )
                    )
            success = True
            keyboard.append([("⬅️ Voltar", "help_start")])
        elif module in COMMANDS_HELP.keys():
            text = f"<b>Módulo</b>: <code>{module}</code>\n"
            module = COMMANDS_HELP[module]
            text += f'\n{module["text"]}\n'

            type = "commands" if "commands" in module else "filters"
            if len(module[type]) > 0:
                text += f'\n<b>{"Comandos" if type == "commands" else "Filtros"}</b>:'
                for key, value in module[type].items():
                    action = value["action"]
                    if len(action) > 0:
                        regex = ""
                        if type == "commands":
                            regex = key.split()[0]
                            if "<" in key and ">" in key:
                                left = key[len(regex) :].split("<")[1:]
                                for field in left:
                                    regex += " <" + field.split(">")[0] + ">"
                        else:
                            regex = key
                        if action == " " and type == "filters":
                            text += f"\n  - <code>{html.escape(regex)}</code>"
                        elif action not in [" ", ""] and type == "filters":
                            text += f"\n  - <code>{html.escape(regex)}</code>: {action}"
                        else:
                            text += f'\n  - <b>{"/" if type == "commands" else ""}{html.escape(regex)}</b>: <i>{action}</i>'
            success = True
            keyboard.append([("⬅️ Voltar", f"help_{type}")])

    kwargs = {}
    if keyboard:
        kwargs["reply_markup"] = c.ikb(keyboard)

    if success:
        await (m.edit_message_text if is_query else m.reply_text)(text, **kwargs)


@Client.on_callback_query(filters.regex("help_(?P<module>.+)"))
async def on_help_callback(c: Client, cq: CallbackQuery):
    module = cq.matches[0]["module"]
    await help_module(c, cq, module)


@Client.on_callback_query(filters.regex("^about$"))
async def about(c: Client, m: CallbackQuery):
    keyboard = c.ikb([[("⬅️ Voltar", "start_back")]])
    await m.message.edit_text(
        about_text,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


@Client.on_callback_query(filters.regex("^start_back$"))
async def start_back(c: Client, m: CallbackQuery):
    text = (start_text).format(m.from_user.first_name, c.me.first_name)
    keyboard = [
        [("📚 Ajuda", "help_cb"), ("ℹ️ Sobre", "about")],
        [("👥 Grupo Off-Topic", "https://t.me/SpamTherapy", "url")],
    ]
    await m.message.edit_text(text, reply_markup=c.ikb(keyboard))