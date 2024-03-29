# RT - Image Captcha

from random import randint
from io import BytesIO

import discord

from jishaku.functools import executor_function
from captcha.image import ImageCaptcha

from core import t

from rtutil.views import TimeoutView
from rtutil.utils import make_random_string

from .part import CaptchaPart, CaptchaContext, FAILED_CODE


LENGTH = 5


class SelectNumber(TimeoutView):
    "画像認証の画像の番号を選択するViewです。"

    def __init__(self, ctx: CaptchaContext, password: str, *args, **kwargs):
        self.ctx, self.password = ctx, password
        super().__init__(*args, **kwargs)
        password_index = randint(0, 24)
        for i in range(25):
            if i == password_index:
                self.on_select.add_option(label=self.password, value=self.password)
            else:
                self.on_select.add_option(
                    label=(value := make_random_string(LENGTH)), value=value
                )

    @discord.ui.select()
    async def on_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == self.password:
            await self.ctx.part.cog.on_success(self.ctx, interaction)
            await interaction.edit_original_message(attachments=(), view=None)
        else:
            await interaction.response.edit_message(
                content=t(FAILED_CODE, interaction), view=None
            )


class ImageCaptchaPart(CaptchaPart):
    "画像認証のパーツです。"
    def __init__(self, *args, **kwargs):
        self.generator = ImageCaptcha()
        super().__init__(*args, **kwargs)

    @executor_function
    def generate_image(self, characters: str | None = None) \
            -> tuple[BytesIO | None, str]:
        "Captcha用の画像を生成します。"
        return self.generator.generate(
            characters := characters or make_random_string(LENGTH)
        ), characters

    async def on_button_push(self, ctx: CaptchaContext, interaction: discord.Interaction) -> None:
        data, password = await self.generate_image()
        if data is None:
            await interaction.response.send_message(t(dict(
                ja="すみませんが、認証に使う画像の生成に失敗しました。\nもう一度お試しください。",
                en="Sorry, we failed to generate the image to be used for authentication.\nPlease try again."
            ), interaction), ephemeral=True)
        else:
            await interaction.response.send_message(t(dict(
                ja="以下にある数字を選んでください。", en="Please select a number below."
            ), interaction), file=discord.File(data, "captcha_image.png"),
            view=SelectNumber(ctx, password), ephemeral=True)