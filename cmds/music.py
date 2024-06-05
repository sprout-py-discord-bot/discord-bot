import discord
from discord.ext import commands
from discord.ui import Button, View
import os
from core import Cog_Extension
import requests as rq
from bs4 import BeautifulSoup
import json
import re

'''
play url 播放音樂
playlist play 開始播放播放清單的歌曲
         add url 將url添加至清單
         remove url 將url從清單刪除
                None/all 清空清單
         insert url way 將url插入至撥放清單第way項(code:way-1,實際:way)
         print 輸出
search name None 搜尋曲名並加至清單
            way 搜尋取名並insert
'''


class Music(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        self.play_list = []

    @commands.command()
    async def play(self, ctx, url):
        song_exist = os.path.isfile("song.mp3")
        try:
            if song_exist:
                os.remove("song.mp3")
        except PermissionError:
            await ctx.send("Wait for the current playing music to end or use the 'stop' command")
            return

        os.system(
            f"yt-dlp.exe --extract-audio --audio-format mp3 --audio-quality 0 {url}")
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if voice is None:
            voiceChannel = discord.utils.get(
                ctx.guild.voice_channels, name='一般')
            await voiceChannel.connect(timeout=600.0)
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                os.rename(file, "song.mp3")

        def play_next(_):
            if len(self.play_list) > 0:
                next_url = self.play_list.pop(0)
                ctx.bot.loop.create_task(self.play(ctx, next_url))

        voice.play(discord.FFmpegPCMAudio(
            executable='ffmpeg.exe', source="song.mp3"), after=play_next)
        await ctx.send(embed=discord.Embed(title="Now Playing", description=url, color=discord.Color.blue()), view=self.create_controls(ctx))

    def create_controls(self, ctx):
        view = View()
        button_play = Button(label="▶️", style=discord.ButtonStyle.green)
        button_pause_resume = Button(
            label="⏸️", style=discord.ButtonStyle.primary)
        button_stop = Button(
            label="⏭️", style=discord.ButtonStyle.danger)

        async def play_callback(interaction):
            if self.play_list:
                await self.play(ctx, self.play_list.pop(0))
                await interaction.response.send_message("Playing next song in the playlist.", ephemeral=True)
            else:
                await interaction.response.send_message("No songs in the playlist.", ephemeral=True)

        async def pause_resume_callback(interaction):
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if voice and voice.is_playing():
                voice.pause()
                button_pause_resume.label = "▶️"
                await interaction.response.send_message("Paused the music.", ephemeral=True)
            elif voice and voice.is_paused():
                voice.resume()
                button_pause_resume.label = "⏸️"
                await interaction.response.send_message("Resumed the music.", ephemeral=True)
            else:
                await interaction.response.send_message("No music is playing.", ephemeral=True)
            await interaction.message.edit(view=view)

        async def stop_callback(interaction):  # 修改回調函數
            voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if voice and (voice.is_playing() or voice.is_paused()):
                voice.stop()
                if self.play_list:
                    next_url = self.play_list.pop(0)
                    await self.play(ctx, next_url)
                    # await interaction.response.send_message("Stopped current song and playing next song in the playlist.", ephemeral=True)
                else:
                    await interaction.response.send_message("Stopped current song. No more songs in the playlist.", ephemeral=True)
            else:
                await interaction.response.send_message("No music is playing.", ephemeral=True)

        button_play.callback = play_callback
        button_pause_resume.callback = pause_resume_callback
        button_stop.callback = stop_callback

        view.add_item(button_play)
        view.add_item(button_pause_resume)
        view.add_item(button_stop)

        return view

    @commands.command()
    async def leave(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        try:
            await voice.disconnect()
            await ctx.send(embed=discord.Embed(title="Disconnected", description="Bot has left the voice channel", color=discord.Color.red()))
        except:
            await ctx.send("The bot is not connected to a voice channel.")

    @commands.command()
    async def search(self, ctx, name, way=None):
        response = rq.get(
            f"https://www.youtube.com/results?search_query={name}")
        doc = BeautifulSoup(response.text, "html.parser")
        scripts = doc.find_all('script')

        yt_initial_data_script = None
        for script in scripts:
            if 'ytInitialData' in script.text:
                yt_initial_data_script = script
                break
        if yt_initial_data_script:
            json_text = re.search(
                r'ytInitialData\s*=\s*(\{.*?\});', yt_initial_data_script.string).group(1)
            data = json.loads(json_text)
            contents = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']

            for content in contents:
                item_section = content.get(
                    'itemSectionRenderer', {}).get('contents', [])
                for item in item_section:
                    video_renderer = item.get('videoRenderer')
                    if video_renderer:
                        video_id = video_renderer.get('videoId')
                        video_title = video_renderer.get('title', {}).get(
                            'runs', [{}])[0].get('text', 'No title found')
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        if way:
                            if int(way)-1 <= len(self.play_list):
                                self.play_list.insert(int(way)-1, video_url)
                                await ctx.send(embed=discord.Embed(
                                    title=video_title, url=video_url, color=discord.Color.blue()))
                        else:
                            self.play_list.append(video_url)
                            await ctx.send(embed=discord.Embed(
                                title=video_title, url=video_url, color=discord.Color.blue()))

                        break
                if video_renderer:
                    break
        else:
            await ctx.send("not found")

    @commands.command()
    async def playlist(self, ctx, action, item=None, way=None):
        if action == 'add':
            if item:
                self.play_list.append(item)
                await ctx.send(embed=discord.Embed(title="Added", description="Song added to the playlist.", color=discord.Color.green()))
            else:
                await ctx.send(embed=discord.Embed(title="Error", description="No song specified to add.", color=discord.Color.red()))
        elif action == 'remove':
            if item and item in self.play_list:
                self.play_list.remove(item)
                await ctx.send(embed=discord.Embed(title="Removed", description="Song removed from the playlist.", color=discord.Color.green()))
            elif not item or item == 'all':
                self.play_list = []
                await ctx.send(embed=discord.Embed(title="Cleared", description="All songs removed from the playlist.", color=discord.Color.green()))
            else:
                await ctx.send(embed=discord.Embed(title="Error", description="Song not found in the playlist.", color=discord.Color.red()))
        elif action == 'print':
            result = '\n'.join(self.play_list)
            if len(self.play_list) > 0:
                await ctx.send(embed=discord.Embed(title="Playlist", description=f'```yaml\n{result}```', color=discord.Color.blue()))
            else:
                await ctx.send(embed=discord.Embed(title='Playlist', description='Nothing', color=discord.Color.red()))
        elif action == 'insert':
            if item and way:
                if way <= len(self.play_list):
                    self.play_list.insert(way-1, item)
                    await ctx.send(embed=discord.Embed(title="Inserted", description=f'{item} is inserted at No.{way}.', color=discord.Color.green()))
                else:
                    await ctx.send(embed=discord.Embed(title="Error", description="Position out of range.", color=discord.Color.red()))
            elif way == None:
                self.play_list.insert(0, item)
                await ctx.send(embed=discord.Embed(title="Inserted", description=f'{item} is inserted at No.1.', color=discord.Color.green()))
            else:
                await ctx.send(embed=discord.Embed(title="Error", description="No song specified to insert.", color=discord.Color.red()))
        elif action == 'play':
            if len(self.play_list) > 0:
                await self.play(ctx, self.play_list.pop(0))
            else:
                await ctx.send(embed=discord.Embed(title="Error", description="Not thing in playlist.", color=discord.Color.red()))


async def setup(bot):
    await bot.add_cog(Music(bot))
