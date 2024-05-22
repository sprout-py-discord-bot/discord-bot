from mimetypes import guess_extension
import discord
from discord.ext import commands
import json 
from config import *
from core import Cog_Extension
from random import randint
from bs4 import BeautifulSoup
import requests as rq
from discord import app_commands

class Wordle(Cog_Extension):
    """
    Attributes:
        game_dict (dict): 儲存當前正在進行中的WordleGame, key為使用者ID
    Methods:
        wordle (ctx): 開啟一場新的WordleGame
        guess (ctx): 猜單字
        end (ctx): 結束當前的WordleGame
    
    """



    def __init__(self, bot):
        # Call the parent's constructor
        super().__init__(bot)
        # Load the word list
        raw_html = rq.get("https://www.wordunscrambler.net/word-list/wordle-word-list").text
        word_doc = BeautifulSoup(raw_html, "html.parser")
        word_list = word_doc.find_all(class_ = "invert light")
        Wordle.word_list = list()

        for item in word_list:
            Wordle.word_list.append(item.text[1:-1])

        # The dictionary for game ongoing
        self.game_dict = dict()


    @commands.command()
    async def wordle(self, ctx):
        user_id = ctx.author.id
        if not user_id in self.game_dict:
            self.game_dict[user_id] = WordleGame()
            await ctx.send("The game has started! You have 6 chances, use **$guess [word]** to guess some words!")
        else:
            await ctx.send("The current game has not ended yet, use **$end** to end the current game.")
        
        
    @commands.command()
    async def guess(self, ctx, guesses: str):
        user_id = ctx.author.id
        if not user_id in self.game_dict:
            await ctx.send("The game hasn't started yet. Consider using **$wordle** to start a game.")
        result = self.game_dict[user_id].guess(guesses)

        await ctx.message.delete()

        await ctx.send(result[1])
        if result[0] == GAME_OVER:
            self.game_dict.pop(user_id)

    @commands.command()
    async def end(self, ctx):
        user_id = ctx.author.id        
        answer = self.game_dict[user_id].answer
        self.game_dict.pop(user_id)
        await ctx.send(f"The current game has been terminated, the answer is **{answer}**")
    
class WordleGame():
    """
    Attributes:
        word_count (int): 單字庫的列表長度
        count (int): 目前猜了幾次
        answer (str): 答案的單字
        history (list[str]): 儲存猜測的結果（不儲存不符合規定的）
        
    Methods:
        guess(guesses) -> Tuple(int, discord.Embed): 以Embed形式回傳猜測的結果 -- WIP -- 暫時使用字串回傳
    
    """

    def __init__(self) -> None:
        
        # Attributes for the game itself
        self.word_count = len(Wordle.word_list) - 1
        self.count = 0
        self.answer = Wordle.word_list[randint(0, self.word_count)]
        self.history = list()
        self.word_composition = dict()

        for letter in self.answer:
            if not letter in self.word_composition:
                self.word_composition[letter] = 1
            else:
                self.word_composition[letter] += 1




    
    def guess(self, guesses):
        if guesses == self.answer:
            return (GAME_OVER, f"Congrats! The answer is indeed **{guesses}**")
        else:
            # Check illegal input
            if len(guesses) != 5:
                return (CONTINUE, "The word has to be exactly 5 letters long.")
            elif guesses not in Wordle.word_list:
                return (CONTINUE, f"Unfortunately, **{guesses}** is not in the word list.")
            
            # Compare the guess to the answer
            output = ""
            occurance = dict()

            for i in range(len(guesses)):
                if guesses[i] in self.answer :
                    if not guesses[i] in occurance:
                        occurance[guesses[i]] = 1
                    else:
                        occurance[guesses[i]] += 1
                        
                    if guesses[i] == self.answer[i]:
                        output += ":green_square: "
                    elif occurance[guesses[i]] <= self.word_composition[guesses[i]]:
                        output += ":yellow_square: "
                    else:
                        output += ":black_large_square: "
                else:
                    output += ":black_large_square: "
            output += "\n"
            for i in range(len(guesses)):
                output += f":regional_indicator_{guesses[i]}: "
            self.history.append(output)
            
            self.count += 1
            if self.count == 6:
                return (CONTINUE, output + f"\nGame Over! You've run out of all 6 attempts.\nThe correct answer is {self.answer}.")

            output += f"\n{6 - self.count} guess(es) left!"

            return (CONTINUE, output)
            

async def setup(bot):
    await bot.add_cog(Wordle(bot))