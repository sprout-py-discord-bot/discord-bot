import random
import discord
from discord.ext import commands
import json
from core import Cog_Extension


class ama(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        self.score = {}

    @commands.command()
    async def a_s(self, ctx):
        if ctx.author.id in self.score:
            await ctx.send(embed=discord.Embed(title='Error', description='you are playing now', color=discord.Color.red()))
            return
        self.score[ctx.author.id] = [0]
        sent, self.score[ctx.author.id][0] = plus_()
        await ctx.send(embed=discord.Embed(title='a_s', description=sent, color=discord.Color.green()))
        print(self.score[ctx.author.id])

    @commands.command()
    async def mu(self, ctx):
        if ctx.author.id in self.score:
            await ctx.send(embed=discord.Embed(title='Error', description='you are playing now', color=discord.Color.red()))
            return
        self.score[ctx.author.id] = [0]
        sent, self.score[ctx.author.id][0] = mu_()
        await ctx.send(embed=discord.Embed(title='mu', description=f'{sent[0]}*{sent[1]}', color=discord.Color.green()))
        print(self.score[ctx.author.id])

    @commands.command()
    async def di(self, ctx):
        if ctx.author.id in self.score:
            await ctx.send(embed=discord.Embed(title='Error', description='you are playing now', color=discord.Color.red()))
            return
        self.score[ctx.author.id] = [0]
        sent, self.score[ctx.author.id][0] = di_()
        await ctx.send(embed=discord.Embed(title='di', description=f'{sent[0]}/{sent[1]}', color=discord.Color.green()))
        print(self.score[ctx.author.id])

    @commands.command()
    async def ans(self, ctx, a):
        if ctx.author.id in self.score:
            if int(a) == self.score[ctx.author.id][0]:
                self.score.pop(ctx.author.id)
                await ctx.send(embed=discord.Embed(title='Congratulations', description=f'answer is {a}', color=discord.Color.green()))
            else:
                await ctx.send(embed=discord.Embed(title='try again', description=f'answer is not {a}', color=discord.Color.red()))
            return
        await ctx.send(embed=discord.Embed(title='Error', description='you are not playing', color=discord.Color.red()))


def di_():
    first = int(random.randrange(100, 10000))
    second = int(random.randrange(1, 10))
    while first % second != 0:
        first = random.randrange(100, 10000)
        second = random.randrange(1, 10)
    return [first, second], int(int(first)/int(second))


def plus_():
    choose = [int(i) for i in range(10, 100)]
    result = random.sample(choose, 10)
    re = ''
    for i in range(0, 10):
        if i > 3:
            is_plus = random.randrange(0, 2)
        else:
            is_plus = 1
        if is_plus == 1 and i > 0:
            re += f'\n {result[i]}'
        elif is_plus == 1:
            re = ' '+str(result[0])
        else:
            re += f'\n-{result[i]}'
    ans = 0
    for i in re.split('\n'):
        ans += int(i)
    return re, ans


def mu_():
    choose1 = [int(i) for i in range(100, 1000)]
    first = int(random.sample(choose1, 1)[0])
    second = random.randrange(1, 10)
    return [first, second], int(first)*int(second)


async def setup(bot):
    await bot.add_cog(ama(bot))
