from math import floor
from mimetypes import guess_all_extensions, guess_extension
import sqlite3
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
        raw_html = rq.get(
            "https://www.wordunscrambler.net/word-list/wordle-word-list").text
        word_doc = BeautifulSoup(raw_html, "html.parser")
        word_list = word_doc.find_all(class_="invert light")
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
            await ctx.send(embed=discord.Embed(title='Wordle Time!', description="The game has started! You have 6 chances, use **$guess [word]** to guess some words!", color=discord.Color.green()))
        else:
            await ctx.send(embed=discord.Embed(title='Error', description="The current game has not ended yet, use **$end** to end the current game.", color=discord.Color.red()))

    @commands.command()
    async def guess(self, ctx, guesses: str):
        user_id = ctx.author.id
        if not user_id in self.game_dict:
            await ctx.send(embed=discord.Embed(title='Error', description="The game hasn't started yet. Consider using **$wordle** to start a game.", color=discord.Color.red()))
            return
        
        instance = self.game_dict[user_id]

        result = instance.guess(guesses)

        await ctx.message.delete()

        # when game is still on
        if result[0] == ISSUE:
            embed = discord.Embed(title = f"Illegal guesses", description = result[1], color = discord.Color.red())
            await ctx.send(embed = embed)
        elif instance.count == 1:
            embed = discord.Embed(title = f'{ctx.author.name}\'s Wordle', description = f"Guesses left: {6 - instance.count}", color = discord.Color.blue())
            embed.add_field(name = f"Attempt {instance.count}", value = result[1], inline = False)
            instance.message = await ctx.send(embed=embed)
        else:
            embed = instance.message.embeds[0]
            embed.description = f"Guesses left: {6 - instance.count}"
            embed.add_field(name = f"Attempt {instance.count}", value = result[1], inline = False)
            await instance.message.edit(embed = embed)
        
        # when game over
        if result[0] == CORRECT:
            embed = discord.Embed(title = f"You Win!", description = f"Congrats! The answer is indeed **{instance.answer}**.", color = discord.Color.yellow())
            await ctx.send(embed = embed)
            self.updateInfo(user_id, instance, CORRECT)
            self.game_dict.pop(user_id)
        if result[0] == GAME_OVER:
            embed = discord.Embed(title = f"Game Over", description = f"\nGame Over! You've run out of all 6 attempts.\nThe correct answer is **{instance.answer}**.", color = discord.Color.yellow())
            await ctx.send(embed = embed)
            self.updateInfo(user_id, instance, GAME_OVER)
            self.game_dict.pop(user_id)

    @commands.command()
    async def end(self, ctx):
        user_id = ctx.author.id
        if not user_id in self.game_dict:
            await ctx.send(embed=discord.Embed(title='Error', description="The game hasn't started yet. Consider using **$wordle** to start a game.", color=discord.Color.red()))
            return
        user_id = ctx.author.id
        answer = self.game_dict[user_id].answer
        self.game_dict.pop(user_id)
        await ctx.send(embed=discord.Embed(title='End', description=f"The current game has been terminated. The answer is **{answer}**", color=discord.Color.blue()))

    @commands.command()
    async def wordleInfo(self, ctx):
        user_id = ctx.author.id 
        con = sqlite3.connect("user_data.db")
        cur = con.cursor()
        res = cur.execute(f"SELECT * FROM wordle_data WHERE user_id = {user_id}")
        user_data = res.fetchone()
        if user_data == None:
            await ctx.send(embed = discord.Embed(title="Error", description="Data not found.", color = discord.Color.red()))
        else:
            count = user_data[3:]
            minimum = min(count)
            delta = max(count) - min(count)
            proportion = [floor(6 * (x - minimum) / delta) for x in count]
            embed = discord.Embed(title = f"{ctx.author.name}'s Info")
            embed.add_field(name = "Game(s) Played", value = user_data[1])
            embed.add_field(name = "Game(s) Finished", value = user_data[2])
            embed.add_field(name = "Win Rates", value = f"{round(user_data[2] * 100 / user_data[1], 2)}%")
            embed.add_field(name = "Guess Distribution", value = "\n".join([f":number_{i + 1}: " + ":green_square:" * block + "  " + str(user_data[i + 3]) for (i, block) in enumerate(proportion)]), inline = False)
            await ctx.send(embed = embed)
        con.close()    

    
    def updateInfo(self, user_id, instance, result):
        con = sqlite3.connect("user_data.db")
        cur = con.cursor()
        res = cur.execute(f"SELECT * FROM wordle_data WHERE user_id = {user_id}")
        user_data = res.fetchone()
        if user_data == None:
            if result == CORRECT:
                cur.execute(f"INSER INTO wordle_data VALUES ({user_id}, 1, 1, 0, 0, 0, 0, 0, 0);")
                cur.execute(f"UPDATE wordle_data SET finished_{instance.count} = 1 WHERE user_id = {user_id};")
            else:
                cur.execute(f"INSERT INTO wordle_data VALUES ({user_id}, 1, 0, 0, 0, 0, 0, 0, 0);")
        else:
            if result == CORRECT:
                cur.execute((
                            "UPDATE wordle_data\n"
                            "SET\n"
                            f"finished_{instance.count} = finished_{instance.count} + 1,\n"
                            "played_count = played_count + 1,\n"
                            "finished_count = finished_count + 1\n"
                            f"WHERE user_id = {user_id};"
                ))
            else:
                cur.execute((
                            "UPDATE wordle_data\n"
                            "SET\n"
                            "played_count = played_count + 1\n"
                            f"WHERE user_id = {user_id};"
                ))
        con.commit()
        con.close()


class WordleGame():
    """
    Attributes:
        word_count (int): 單字庫的列表長度
        count (int): 目前猜了幾次
        answer (str): 答案的單字
        history (list[str]): 儲存猜測的結果（不儲存不符合規定的）
        word_composition (dict): 單字組成。
        message (int): 每個Instance的訊息的ID，在第一次猜測時初始化。

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
        self.message = None

        for letter in self.answer:
            if not letter in self.word_composition:
                self.word_composition[letter] = 1
            else:
                self.word_composition[letter] += 1

    def guess(self, guesses):
        # Check illegal input
        if len(guesses) != 5:
            return (ISSUE, "The word has to be exactly 5 letters long.")
        elif guesses not in Wordle.word_list:
            return (ISSUE, f"Unfortunately, **{guesses}** is not in the word list.")

        # Compare the guess to the answer
        output = [":black_large_square:" for _ in range(5)]
        answer = [letter for letter in self.answer]

        # Check those correct one
        for i in range(0, 5):
            if guesses[i] == answer[i]:
                output[i] = ":green_square:"
                answer[i] = ""
        for i in range(0, 5):
            if output[i] == ":green_square:":
                continue
            if guesses[i] in answer:
                output[i] = ":yellow_square:"
                answer.remove(guesses[i])

        output = " ".join(output) + "\n"
       
        for i in range(len(guesses)):
            output += f":regional_indicator_{guesses[i]}: "
        self.history.append(output)
        self.count += 1
        if guesses == self.answer:
            return (CORRECT, output)

        if self.count == 6:
            return (GAME_OVER, output)

        #output += f"\n{6 - self.count} guess(es) left!"
        return (CONTINUE, output, None)


async def setup(bot):
    await bot.add_cog(Wordle(bot))
