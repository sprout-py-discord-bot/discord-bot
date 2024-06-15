import json
from discord.ext import commands
from typing import List
import discord

from core import Cog_Extension
from random import randint, shuffle

class Abacus(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        with open("data.json", "r", encoding = "utf-8") as f:
            self.context= json.load(f)
        self.instances = dict()


    @commands.command()
    async def abacus(self, ctx, abacus: str, level: int):
        user_id = ctx.author.id
        if user_id not in self.instances:
            self.instances[user_id] = AbacusInstance(abacus, self.context[level])
            await ctx.send(embed=discord.Embed(title=f"Abacus Level {level}", description = "Use $a [answer] to answer.", color=discord.Color.green()))
            await ctx.send(embed=discord.Embed(title=1, description = self.instances[user_id].problem_set[0][0].question))
        else:
            await ctx.send("Please finish the current session first.")
    
    @commands.command()
    async def a(self, ctx, answer: int):
        user_id = ctx.author.id 
        if user_id not in self.instances:
            await ctx.send("Error occured. Use **$abacus [abacus|mental] [level]** to start an instance.")
        else:
            if self.instances[user_id].count < 29:
                await ctx.send(embed=discord.Embed(title=self.instances[user_id].count + 1, description = self.instances[user_id].next(answer)))
            else:
                result = self.instances[user_id].finish(answer)
                await ctx.send(f"{ctx.author.name} 的結果\n分數：{result[1]}/200", embeds = result[0])







class AbacusInstance():
    def __init__(self, category: str, context: dict):
        self.context = context
        self.problem_set = [[], [], []]
        self.count = 0
        self.answer = []
        # [0]: +- [1]: * [2]:/
        for _ in range(0, 10):
            for i in range(0, 3):
                self.problem_set[i].append(AbacusProblem(category == "abacus", i, context))
    def next(self, answer):
        self.answer.append(answer)
        self.count += 1
        return self.problem_set[self.count // 10][self.count % 10].question
    def finish(self, answer):
        title = ["加減算", "乘算", "除算"]
        embed_list = []
        self.answer.append(answer)
        answer = [self.answer[0: 10], self.answer[10: 20], self.answer[20: 30]]
        score = 0
        for i in range(0, 3):
            embed_list.append(discord.Embed(title = title[i]))
            for j in range(0, 10):
                if answer[i][j] == self.problem_set[i][j]:
                    score += 10 - 5 * min(1, i)
                else:
                    answer[i][j] = f"**{answer[i][j]}**"
            embed_list[i].add_field(name = "你的答案", value = "\n".join(answer[i]))
            embed_list[i].add_field(name = "正確答案", value = "\n".join([str(self.problem_set[i][m].answer) for m in range(0, 10)]))
        return (embed_list, score)
        
        


class AbacusProblem():
    def __init__(self, abacus: bool, operation_type: int, context: dict):
        self.question = ""
        self.answer = 0
        if abacus:
            category = "珠算"
        else:
            category = "心算"
        
        if operation_type == 0:
            self.plus(context[category]["加減算"][0],
                        context[category]["加減算"][1],
                        context[category]["加減算"][2],
                        context[category]["加減算"][3])
        elif operation_type == 1:
            self.multiplication(context[category]["乘算"][randint(0, len(context[category]["乘算"]) - 1)])
        else:
            self.division(context[category]["除算"][randint(0, len(context[category]["除算"]) - 1)])

    def plus(self, digit: list, minus: int, decimal = False, to_shuffle = False):
        if to_shuffle:
            shuffle(digit)
        index = 1
        for _ in range(0, minus):
            index += randint(1, (len(digit) - 1) // minus)
            digit[index] *= -1

        for item in digit:
            if item < 0:
                number = randint(10 ** abs(item), 10 ** (abs(item) + 1) - 1)
                number *= -1
            else:
                number = randint(10 ** item, 10 ** (item + 1) - 1)
            self.answer += number
            if decimal:
                self.question += f"{number}.{number % 100}\n"
            else:
                self.question += f"{number}\n"
        if decimal:
            self.answer /= 100
            
    
    def multiplication(self, digit: list):
        multiplicand = randint(10 ** digit[0], 10 ** (digit[0] + 1) - 1)
        multiplier = randint(10 ** digit[1], 10 ** (digit[1] + 1) - 1)
        self.question = f"{multiplicand} × {multiplier} = "
        self.answer = multiplicand * multiplier
    
    def division(self, digit: list):
        divisor = randint(10 ** digit[0], 10 ** (digit[0] + 1) - 1)
        quotient = randint(10 ** digit[1], 10 ** (digit[1] + 1) - 1)
        self.question = f"{divisor * quotient} ÷ {divisor} = "
        self.answer = quotient
    

        


async def setup(bot):
    await bot.add_cog(Abacus(bot))