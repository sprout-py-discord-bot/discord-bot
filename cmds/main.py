import discord
from discord.ext import commands
import json
from core import Cog_Extension
from datetime import datetime


class Main(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        self.to_do_list = {}

    @commands.hybrid_command()
    async def todolist(self, ctx, action, item=None, time=None):
        '''
        Todolist add item date新增一個事項到todolist

        Todolist remove item 從todolist刪除一個事項
                        all 刪除todolist的所有事項
                        None 刪除todolist的所有事項

        Todolist print 印出todolist

        Todolist sort 依字典續排序todolist

        Todolist time 依時間排序todolist

        每個user會依據user id建立不同的todolist (dict)自己的todolist其他人不能進行刪減、排序或輸出,保護使用者的todolist
        '''
        if ctx.author.id not in self.to_do_list:
            self.to_do_list[ctx.author.id] = {}

        if action == 'add':
            if time and len(time.split('/')) == 3:
                year, month, day = time.split('/')
                if self.is_valid_date(year, month, day):
                    if item not in self.to_do_list[ctx.author.id]:
                        self.to_do_list[ctx.author.id][str(item)] = [
                            year, month, day]
                        await ctx.send(embed=discord.Embed(title='success', description=f"{item} is added in Todolist", color=discord.Color.green()))
                    else:
                        await ctx.send(embed=discord.Embed(title='error', description=f'{item} had been added', color=discord.Color.red()))
                else:
                    await ctx.send(embed=discord.Embed(title='error', description="Date is unavailable", color=discord.Color.red()))
            elif time:
                await ctx.send(embed=discord.Embed(title='error', description="Time's forming should be YYYY/MM/DD", color=discord.Color.red()))
            else:
                await ctx.send(embed=discord.Embed(title='error', description='You have to input time', color=discord.Color.red()))

        elif action == 'remove':
            if item != 'all':
                if item:
                    if item in self.to_do_list[ctx.author.id]:
                        self.to_do_list[ctx.author.id].pop(item)
                        await ctx.send(embed=discord.Embed(title='success', description=f'{item} is removed', color=discord.Color.green()))
                    else:
                        await ctx.send(embed=discord.Embed(title='error', description=f'{item} is not in Todolist', color=discord.Color.red()))
                else:
                    self.to_do_list[ctx.author.id] = {}
                    await ctx.send(embed=discord.Embed(title='success', description=f'Todolist is clear', color=discord.Color.green()))
            else:
                self.to_do_list[ctx.author.id] = {}
                await ctx.send(embed=discord.Embed(title='success', description=f'Todolist is clear', color=discord.Color.green()))

        elif action == 'print':
            if len(self.to_do_list[ctx.author.id]) == 0:
                await ctx.send(embed=discord.Embed(title=f'user name : {ctx.author.name}', description=f'```yaml\nNothing in Todolist```', color=discord.Color.green()))
            else:
                i = 0
                for k in self.to_do_list[ctx.author.id]:
                    if len(k) > i:
                        i = len(k)
                result = []
                k = 'item'
                v = 'time'
                while len(k) < i+1:
                    k += ' '
                result.append(f"{k}: {v}")
                for k, v in self.to_do_list[ctx.author.id].items():
                    while len(k) < i+1:
                        k += ' '
                    v = '/'.join(v)
                    result.append(f"{k}: '{v}'")
                result = '\n'.join(result)
                await ctx.send(embed=discord.Embed(title=f'user name : {ctx.author.name}', description=f'```yaml\n{result}```', color=discord.Color.green()))

        elif action == 'sort':
            self.to_do_list[ctx.author.id] = dict(
                sorted(self.to_do_list[ctx.author.id].items()))
            await self.todolist(ctx, 'print')

        elif action == 'time':
            sorted_keys = sorted(
                self.to_do_list[ctx.author.id], key=lambda x: self.sort_by_date(ctx, x))
            self.to_do_list[ctx.author.id] = {
                key: self.to_do_list[ctx.author.id][key] for key in sorted_keys}
            await self.todolist(ctx, 'print')
            # await ctx.send(embed=discord.Embed(title='success', description=f'Todolist is sorted by time', color=discord.Color.green()))

    def sort_by_date(self, ctx, key):
        year, month, day = map(int, self.to_do_list[ctx.author.id][key])
        return datetime(year, month, day)

    def is_valid_date(self, year, month, day):
        try:
            datetime(int(year), int(month), int(day))
            return True
        except ValueError:
            return False

    '''
    TODO
    Add the necessary bot commands here
    Consider using data.json to store some data such as url
    '''


async def setup(bot):
    await bot.add_cog(Main(bot))
