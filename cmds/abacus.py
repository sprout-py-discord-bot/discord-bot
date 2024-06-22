import json
import time
from discord.ext import commands
import discord
import sqlite3
from core import Cog_Extension
from random import randint, shuffle

class Abacus(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        with open("data.json", "r", encoding = "utf-8") as f:
            self.context= json.load(f)
        self.instances = dict()



    @commands.hybrid_command()
    async def abacus(self, ctx, level: int):
        user_id = ctx.author.id
        if user_id not in self.instances:
            if level < 0 or level > 10:
                await ctx.send(embed = discord.Embed(title = "格式錯誤", description = "**等級應介於0~10之間"))
                return
            else:
                if level > 5:
                    self.instances[user_id] = SepInstance(self.context[level], 0)
                    await ctx.send(embed=discord.Embed(title=f"Abacus Level {level}", description = "使用 $a [answer] 以回答.", color=discord.Color.green()))
                    await ctx.send(embed=discord.Embed(title=1, description = self.instances[user_id].problem_set[0].question))
                else:
                    self.instances[user_id] = AbacusInstance(self.context[level])
                    await ctx.send(embed=discord.Embed(title=f"Abacus Level {level}", description = "使用 $a [answer] 以回答.", color=discord.Color.green()))
                    await ctx.send(embed=discord.Embed(title=1, description = self.instances[user_id].problem_set[0][0].question))
                self.instances[user_id].time = time.time()
        else:
            await ctx.send(embed = discord.Embed(title = "失敗", description = "請先完成當前測驗。"))
    
    @commands.hybrid_command()
    async def abacus_session(self, ctx, level: int, category: int):
        user_id = ctx.author.id
        if user_id not in self.instances:
            if level < 0 or level > 10:
                await ctx.send(embed = discord.Embed(title = "格式錯誤", description = "**等級應介於0~10之間"))
                return
            else:
                self.instances[user_id] = SepInstance(self.context[level], category)
                await ctx.send(embed=discord.Embed(title=f"Abacus Level {level}", description = "使用 $a [answer] 以回答.", color=discord.Color.green()))
                await ctx.send(embed=discord.Embed(title=1, description = self.instances[user_id].problem_set[0].question))
                self.instances[user_id].time = time.time()
        else:
            await ctx.send(embed = discord.Embed(title = "失敗", description = "請先完成當前測驗。"))

    @commands.hybrid_command()
    async def a(self, ctx, answer: float):
        user_id = ctx.author.id 
        if user_id not in self.instances:
             await ctx.send(embed = discord.Embed(title = "失敗", description = "測驗尚未開始. 使用 **$abacus [level]** 以開始測驗"))
        else:
            if answer.is_integer():
                answer = int(answer)
            if (isinstance(self.instances[user_id], AbacusInstance) and self.instances[user_id].count < 29) or (isinstance(self.instances[user_id], SepInstance) and self.instances[user_id].count < 9):
                desc =  self.instances[user_id].next(answer)
                await ctx.send(embed=discord.Embed(title=(self.instances[user_id].count + 1), description = desc))
            else:
                result = self.instances[user_id].finish(answer)
                if isinstance(self.instances[user_id], SepInstance):
                    await ctx.send(f"{ctx.author.name} 的結果\n分數：{result[1]}/100\n總花費時間：{result[2]}分{result[3]}秒", embeds = result[0])
                else:
                    await ctx.send(f"{ctx.author.name} 的結果\n分數：{result[1]}/200\n總花費時間：{result[2]}分{result[3]}秒", embeds = result[0])
                self.instances.pop(user_id)
    @commands.hybrid_command()
    async def abacus_end(self, ctx):
        user_id = ctx.author.id 
        if user_id not in self.instances:
            await ctx.send(embed = discord.Embed(title = "失敗", description = "測驗尚未開始. 使用 **$abacus [level]** 以開始測驗"))
        else:
            self.instances.pop(user_id)
            await ctx.send(embed = discord.Embed(title="成功", description="成功離開當前測驗。"))

class AbacusInstance():
    def __init__(self, context: dict):
        self.context = context
        self.problem_set = [[], [], []]
        self.count = 0
        self.answer = []
        self.time = 0.0
        # [0]: +- [1]: * [2]:/
        for i in range(0, 10):
            for j in range(0, 3):
                self.problem_set[j].append(AbacusProblem(j, context, i))
    def next(self, answer):
        self.answer.append(answer)
        self.count += 1
        return self.problem_set[self.count // 10][self.count % 10].question
    def finish(self, answer):
        curr_time = time.time()
        time_spent = int(curr_time - self.time)
        title = ["加減算", "乘算", "除算"]
        embed_list = []
        self.answer.append(answer)
        answer = [self.answer[0: 10], self.answer[10: 20], self.answer[20: 30]]
        score = 0
        for i in range(0, 3):
            embed_list.append(discord.Embed(title = title[i]))
            for j in range(0, 10):
                if answer[i][j] == self.problem_set[i][j].answer:
                    score += 10 - 5 * min(1, i)
                else:
                    answer[i][j] = f"**{answer[i][j]}**"
            embed_list[i].add_field(name = "你的答案", value = "\n".join([str(answer[i][m]) for m in range(0, 10)]))
            embed_list[i].add_field(name = "正確答案", value = "\n".join([str(self.problem_set[i][m].answer) for m in range(0, 10)]))

        return (embed_list, score, time_spent // 60, time_spent % 60)

class SepInstance():
    def __init__(self, context: dict, category: int):
        self.context = context
        self.problem_set = []
        self.count = 0
        self.answer = []
        self.time = 0.0
        self.category = category
        # [0]: +- [1]: * [2]:/
        for i in range(0, 10):
            self.problem_set.append(AbacusProblem(self.category, context, i))
    def next(self, answer):
        self.answer.append(answer)
        self.count += 1
        return self.problem_set[self.count].question
    def finish(self, answer):
        curr_time = time.time()
        time_spent = int(curr_time - self.time)
        title = ["加減算", "乘算", "除算"]
        embed_list = []
        self.answer.append(answer)
        score = 0
        embed_list.append(discord.Embed(title = title[self.category]))
        for i in range(0, 10):
            if self.answer[i] == self.problem_set[i].answer:
                score += 10
            else:
                self.answer[i] = f"**{self.answer[i]}**"
        embed_list[0].add_field(name = "你的答案", value = "\n".join([str(self.answer[j]) for j in range(0, 10)]))
        embed_list[0].add_field(name = "正確答案", value = "\n".join([str(self.problem_set[j].answer) for j in range(0, 10)]))

        return (embed_list, score, time_spent // 60, time_spent % 60)
        
        


class AbacusProblem():
    def __init__(self, operation_type: int, context: dict, number: int):
        self.question = ""
        self.answer = 0
        
        if len(context["加減算"][0]) == 1 or (number < 5):
            k = 0
        else:
            k = 1

        if operation_type == 0:
            if number + 1 % 2 == 0:
                self.plus(context["加減算"][0][k],
                        0,
                        context["加減算"][2],
                        context["加減算"][3],
                        (number + 1) % 2 == 0)
            else:
                self.plus(context["加減算"][0][k],
                            context["加減算"][1],
                            context["加減算"][2],
                            context["加減算"][3],
                            (number + 1) % 2 == 0)
        elif operation_type == 1:
            self.multiplication(context["乘算"][randint(0, len(context["乘算"]) - 1)])
        else:
            self.division(context["除算"][randint(0, len(context["除算"]) - 1)])

    def plus(self, digit: list, minus: int, decimal = False, to_shuffle = False, even = False):
        value = digit.copy()
        if to_shuffle:
            shuffle(value)
        index = 1
        if even:
            minus = 0
        for _ in range(0, minus):
            index += randint(1, (len(value) - 1) // minus - 1)
            value[index] *= -1

        for item in value:
            if item < 0:
                number = randint(10 ** (abs(item) - 1), 10 ** abs(item) - 1)
                number *= -1
            else:
                number = randint(10 ** (item - 1), 10 ** item - 1)
            self.answer += number
            if decimal:
                self.question += f"{number // 100}.{number % 100}\n"
            else:
                self.question += f"{number}\n"
        if decimal:
            self.answer = round(self.answer / 100, 2)

        if self.answer < 0:
            self.question = ""
            self.plus(digit, minus, decimal, to_shuffle, even)
            
            
    
    def multiplication(self, digit: list):
        multiplicand = randint(10 ** (digit[0] - 1), 10 ** digit[0] - 1)
        multiplier = randint(10 ** (digit[1] - 1) + 1, 10 ** digit[1] - 1)
        self.question = f"{multiplicand} × {multiplier} = "
        self.answer = multiplicand * multiplier
    
    def division(self, digit: list):
        divisor = randint(10 ** (digit[0] - 1) + 1, 10 ** digit[0] - 1)
        quotient = randint(10 ** (digit[1] - 1), 10 ** digit[1] - 1)
        self.question = f"{divisor * quotient} ÷ {divisor} = "
        self.answer = quotient
    

        


async def setup(bot):
    await bot.add_cog(Abacus(bot))