import discord
from discord.ext import commands
import json
from core import Cog_Extension
import requests as rq
from bs4 import BeautifulSoup
import re
import os
'''
meme take name 要求discordbot傳出名字為name的梗圖
     view 印出所有圖片名稱
     search name savekeyword/None 尋找name並下載搜尋的第一張圖，savekeyword==None->以name作為取出的keyword
                                                               else:savekeyword做為取出keyword     
     remove name 刪除特定項目    
     download name將照片下載並命名為name
'''


class Meme(Cog_Extension):
    def __init__(self, bot,):
        super().__init__(bot)
        self.memes_name = {}

    @commands.command()
    async def gallery(self, ctx, action, name=None, savekeyword=None):
        if action == 'take':
            is_find = False
            if name:
                for i in os.listdir('image'):
                    if i == f'{name}.jpg':
                        await ctx.send(file=discord.File(f'image/{i}'))
                        is_find = True
                        break
                if not is_find:
                    await ctx.send(embed=discord.Embed(title='Error', description='Notfound', color=discord.Color.red()))
            else:
                await ctx.send(embed=discord.Embed(title='Error', description='name is a required argument that is missing.d', color=discord.Color.red()))
        elif action == 'remove':
            if name:
                if name:
                    try:
                        os.remove(f'image\{name}.jpg')
                        await ctx.send(embed=discord.Embed(title='success', description=f'{name}.jpg has been removed', color=discord.Color.green()))
                    except:
                        await ctx.send(embed=discord.Embed(title='Error', description=f'{name}.jpg is not defined', color=discord.Color.red()))
                else:
                    await ctx.send(embed=discord.Embed(title='Error', description='"name" object can\'t be None', color=discord.Color.red()))
            else:
                await ctx.send(embed=discord.Embed(title='Error', description='name is a required argument that is missing.d', color=discord.Color.red()))
        elif action == 'search':
            if name:
                if savekeyword is None:
                    savekeyword = name
                if f"{savekeyword}.jpg" in os.listdir('.\image'):
                    await ctx.send(embed=discord.Embed(title='Error', description=f'Name {savekeyword}.jpg has used.Please remove {savekeyword}.jpg and tryagin', color=discord.Color.red()))
                else:
                    link = f'https://www.google.com/search?hl=en&q={name}&tbm=isch'
                    response = rq.get(link)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    image_element = soup.find(
                        "img", {"src": re.compile("gstatic.com")})

                    if not image_element:
                        await ctx.send(embed=discord.Embed(title='Error', description='Not found', color=discord.Color.red()))
                    else:
                        image_url = image_element['src']
                        image_response = rq.get(image_url)

                        image_path = os.path.join(
                            'image', f'{savekeyword}.jpg')
                        with open(image_path, 'wb') as file:
                            file.write(image_response.content)
                        await ctx.send(embed=discord.Embed(title='Success', description=f'Image saved as {savekeyword}.jpg', color=discord.Color.green()))
                        await ctx.send(file=discord.File(f'image\{savekeyword}.jpg'))
            else:
                await ctx.send(embed=discord.Embed(title='Error', description='name is a required argument that is missing.d', color=discord.Color.red()))
        elif action == 'view':
            if len(os.listdir('.\image')) > 0:
                result = '\n'.join(os.listdir('.\image'))
                await ctx.send(embed=discord.Embed(title='file in image', description=f"```yaml\n{result}```", color=discord.Color.green()))
            else:
                await ctx.send(embed=discor.Embed(title='file in image', description='```yaml\nnot found```'))
        elif action == 'download':
            if not name:
                await ctx.send(embed=discord.Embed(title='Error', description='name is a required argument that is missing.', color=discord.Color.red()))
                return
            if f"{name}.jpg" in os.listdir('.\image'):
                await ctx.send(embed=discord.Embed(title='Error', description=f'Name {name}.jpg has used.Please remove {name}.jpg and tryagin', color=discord.Color.red()))
                return
            attachments = ctx.message.attachments
            if len(attachments) == 0:
                await ctx.send(embed=discord.Embed(title='Error', description='No image attachment found.', color=discord.Color.red()))
                return

            attachment = attachments[0]
            image_path = os.path.join('image', f'{name}.jpg')
            await attachment.save(image_path)
            await ctx.send(embed=discord.Embed(title='Success', description=f'Image downloaded and saved as {name}.jpg', color=discord.Color.green()))


async def setup(bot):
    await bot.add_cog(Meme(bot))
