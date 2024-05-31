import discord
from discord.ext import commands
import json
from core import Cog_Extension
from datetime import datetime


class Main(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        self.to_do_list = {}

    @commands.command()
    async def Hello(self, ctx):
        await ctx.send("Hello, world")

    @commands.command()
    async def Todolist(self, ctx, action, item=None, time=None):
        '''
        Todolist add item 新增一個事項到todolist

        Todolist remove item 從todolist刪除一個事項
                        all 刪除todolist的所有事項

        Todolist print 印出todolist

        Todolist sort 依字典續排序todolist

        Todolist time 依時間排序todolist

        每個user會依據user id建立不同的todolist(type dict)自己的todolist其他人不能進行刪減、排序或輸出,保戶使用者的todolist
        '''
        if ctx.author.id not in self.to_do_list:
            self.to_do_list[ctx.author.id] = {}
        if action == 'add':
            if time != None and len(time.split('/')) == 3:
                if item not in self.to_do_list and len(str(time.split('/')[0])) == 4 and len(str(time.split('/')[1])) == 2 and len(str(time.split('/')[2])) == 2:
                    self.to_do_list[ctx.author.id][str(item)] = time.split('/')
                    await ctx.send('success')
                elif item not in self.to_do_list:
                    await ctx.send("Time's forming should be YYYY/MM/DD")
                else:
                    await ctx.send(f'{item} had been added')
            elif time != None:
                await ctx.send(f'{item} had been added')
            else:
                await ctx.send('You have to input time')
        elif action == 'remove':
            if item != 'all':
                if item != None:
                    if item in self.to_do_list[ctx.author.id]:
                        self.to_do_list[ctx.author.id].pop(item)
                        await ctx.send('success')
                    else:
                        await ctx.send(f'{item} not in to do list')
                else:
                    self.to_do_list[ctx.author.id] = {}
                    await ctx.send('success')
            else:
                self.to_do_list[ctx.author.id] = {}
                await ctx.send('success')
        elif action == 'print':
            if len(self.to_do_list[ctx.author.id]) == 0:
                await ctx.send(f"```yaml\nuser name : {ctx.author.name}\n\nnot thing in todolist```")
            else:
                i = 0
                for k in self.to_do_list[ctx.author.id]:
                    if len(k) > i:
                        i = len(k)
                result = [f"user name : {ctx.author.name}\n"]
                k = 'item'
                v = 'date'
                while len(k) < i+1:
                    k += ' '
                result.append(f"{k}: {v}")
                for k, v in self.to_do_list[ctx.author.id].items():
                    while len(k) < i+1:
                        k += ' '
                    v = '/'.join(v)
                    result.append(f"{k}: '{v}'")
                result = '\n'.join(result)
                await ctx.send(f'```yaml\n{result}\n```')

        elif action == 'sort':
            self.to_do_list[ctx.author.id] = dict(
                sorted(self.to_do_list[ctx.author.id].items()))
            await ctx.send('success')
        elif action == 'time':
            sorted_keys = sorted(
                self.to_do_list[ctx.author.id], key=lambda x: self.sort_by_date(ctx, x))
            self.to_do_list[ctx.author.id] = {
                key: self.to_do_list[ctx.author.id][key] for key in sorted_keys}
            await ctx.send('success')

    def sort_by_date(self, ctx, key):
        year, month, day = map(int, self.to_do_list[ctx.author.id][key])
        return datetime(year, month, day)

    '''
    TODO
    Add the necessary bot commands here
    Consider using data.json to store some data such as url
    '''


async def setup(bot):
    await bot.add_cog(Main(bot))
