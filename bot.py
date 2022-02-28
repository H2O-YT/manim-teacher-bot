import disnake
from disnake.ext import commands
import os, asyncio
import asyncio.subprocess
import aiofiles as aiof
import aiofiles.os as asyncos
import time


class ManimTeacherBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="!", help_command=None)

bot = ManimTeacherBot()

@bot.event
async def on_ready():
    print("Bot online!")

@bot.command()
async def help(ctx):
    title = "Help for ManimTeacherBot"
    descriptions = ["""`!render`: With this command you can render a Manim scene
in Discord using a code block in your message and entering scene names.
**Example:**
!render ```python
from manim import *


class Scene1(Scene):
    def construct(self):
        self.add(ManimBanner())

class Scene2(Scene):
    def construct(self):
        self.add(Tex("My scene"))
``` Scene1 Scene2
**Important:**
You can't use characters like ` in your code. Also, you can't render gifs, only MP4
and PNG if the code doesn't contain any animation.""",
"""`!save`: Saves for 5 minutes a Python code. You must put a code block in your
message. During those 5 minutes, you can import that code with the given name.
After those 5 minutes, you can't use that.
**Example:**
!save ```python
from manim import *


class TexRainbow(Tex):
    def __init__(self, *tex_strings, **kwargs):
        super().__init__(*tex_strings, **kwargs)
        self.set_color_by_gradient(RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE)
``` my_wonderful_code
**How to use after that?**
!render ```python
from manim import *
from my_wonderful_code import TexRainbow


class TexRainbowScene(Scene):
    def construct(self):
        self.add(TexRainbow("This is a \\\\LaTeX\\\\ rainbow!"))
``` TexRainbowScene""",
"""`!remove`: Removes a code. Use it when you don't need that code anymore.
**Example**
!remove my_wonderful_code"""]
    index = 0
    embed = disnake.Embed(title=title, description=descriptions[index])
    message = await ctx.send(embed=embed)
    await message.add_reaction("◀")
    await message.add_reaction("▶")
    check = lambda r, u: u == ctx.author and str(r.emoji) in "◀▶"
    now = time.time()
    while time.time() - now < 60:
        reaction, _ = await bot.wait_for("reaction_add", check=check)
        if str(reaction.emoji) == "◀":
            if index > 0:
                index -= 1
                embed = disnake.Embed(title=title, description=descriptions[index])
                await message.edit(embed=embed)
            await reaction.remove(ctx.message.author)
        if str(reaction.emoji) == "▶":
            if index < 2:
                index += 1
                embed = disnake.Embed(title=title, description=descriptions[index])
                await message.edit(embed=embed)
            await reaction.remove(ctx.message.author)

async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, _ = await proc.communicate()

    result = proc.returncode
    
    print(str(result)+"\n"+stdout.decode())

    return result

@bot.command()
async def render(ctx, *, message:str):
    if not "```python" in message:
        await ctx.send(f"{ctx.message.author.mention} You need to put a Python code block!")
        return
    content = message.split("```python")[1].split("```")
    code_to_write = content[0]
    scene_names = content[1].split(" ")[1:]
    async with aiof.open("user_code.py", 'w') as file:
        await file.write(code_to_write)
        await file.close()
    to_run = ['manim', 'user_code.py']
    for scene_name in scene_names:
        to_run.append(scene_name)
    result = await run(" ".join(to_run))
    if result != 0:
        await ctx.send(f"{ctx.message.author.mention} Something went wrong! Remember you can learn Manim on <@741341730531704843>'s channel :smile:")
    else:
        files = []
        path1 = "media/images/user_code"
        path2 = "media/videos/user_code/1080p60"
        for file_for_discord in os.listdir(path1):
            if file_for_discord.endswith(".png"):
                files.append(path1+"/"+file_for_discord)
        for file_for_discord in os.listdir(path2):
            if file_for_discord.endswith(".mp4"):
                files.append(path2+"/"+file_for_discord)
        discord_files = [disnake.File(file_for_discord) for file_for_discord in files]
        for discord_file in discord_files:
            await ctx.send(f"{ctx.message.author.mention} Rendered succesfully!", file=discord_file)
        for discord_file in files:
            await asyncos.remove(discord_file)
    await asyncos.remove("user_code.py")


@bot.command()
async def save(ctx, *, message:str):
    content = message.split("```python")[1].split("``` ")
    code = content[0]
    try:
        file_name = content[1]
    except:
        await ctx.send(f"{ctx.message.author.mention} You need to put a name to your code!")
    if not file_name.endswith(".py"):
        file_name += ".py"
    async with aiof.open(file_name, 'w') as file:
        await file.write(code)
        await file.close()
    await ctx.send(f"{ctx.message.author.mention} Saved succesfully! This code will be available for 5 minutes.")
    await asyncio.sleep(300)
    await asyncos.remove(file_name)

@bot.command()
async def remove(ctx, *, message:str):
    file_to_remove = message
    if not file_to_remove.endswith(".py"):
        file_to_remove += ".py"
    try:
        await asyncos.remove(file_to_remove)
        await ctx.send(f"{ctx.message.author.mention} Removed succesfully!")
    except:
        await ctx.send(f"{ctx.message.author.mention} The code doesn't exist!")

token = os.environ.get("DISCORD_BOT_TOKEN")
bot.run(token)