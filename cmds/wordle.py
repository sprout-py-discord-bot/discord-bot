import discord
from discord.ext import commands
import json 
from core import Cog_Extension
from random import randint

class Wordle(Cog_Extension):
        
    def __init__(self, bot):
        super().__init__(bot)
        with open("./wordle.json", "r") as f:
            Wordle.word_list = json.load(f)
        self.word_amount = len(Wordle.word_list) - 1
        self.answer = "glass"
        self.finished = True


    @commands.command()
    async def wordle(self, ctx):
        if not self.finished:
            await ctx.send("The current game has not ended yet, please wait for the game to end or use **$end** to end the current game.")
            return
        self.finished = False
        self.answer = Wordle.word_list[randint(0, self.word_amount)]
        self.count = 0
        await ctx.send("The game has started! You have 6 chances, use **$guess [word]** to guess some words!")
        
    @commands.command()
    async def guess(self, ctx, guesses: str):
        if self.finished:
            await ctx.send("The game hasn't started yet. Consider using **$wordle** to start a game.")
            return

        if guesses == self.answer:
            await ctx.send(f"Congratualtion! The answer is indeed **{self.answer}**")
            self.finished = True
            return
        else:
            if len(guesses) != 5:
                await ctx.send("The word has to be exactly 5 letters long.")
                return
            elif guesses not in Wordle.word_list:
                await ctx.send(f"Unfortunately, **{guesses}** is not in the word list.")
                return
            
            output = ""
            for i in range(len(guesses)):
                if guesses[i] == self.answer[i]:
                    output += ":green_square:"
                elif guesses[i] in self.answer:
                    output += ":yellow_square:"
                else:
                    output += ":black_large_square:"
            output += "\n"
            for i in range(len(guesses)):
                output += f":regional_indicator_{guesses[i]}:"
            
            await ctx.send(output)
            self.count += 1
            if self.count == 6:
                await ctx.send(f"Game Over! You've run out of guesses.\n The correct answer is {self.answer}.")

            await ctx.send(f"{6 - self.count} guess(es) left!")

            
    

    @commands.command()
    async def end(self, ctx):
        if self.finished:
            await ctx.send("The game hasn't started yet. Consider using **$wordle** to start a game.")
            return
        self.finished = True
        await ctx.send(f"The current game has been terminated, the answer is **{self.answer}**")
    
    @commands.command()
    async def gimme(self, ctx):
        await ctx.send(self.answer)
    

async def setup(bot):
    await bot.add_cog(Wordle(bot))