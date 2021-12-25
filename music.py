import discord
import asyncio
from discord.ext import commands 
import youtube_dl

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(id)s.mp3',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)

        self.data = data

        self.id = data.get('id')
        self.title = data.get('title')
        self.url = data.get('url')
    
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            
            data = data['entries'][0]
           

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class music(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.queue = []

        self.REMOVE_DOWNLOADS = True
    
    @commands.command()
    async def join(self,ctx):
      if ctx.author.voice is None:
        await ctx.send("You'r not connected to a voice channel")
      voice_channel = ctx.author.voice.channel
      if ctx.voice_client is None:
        await voice_channel.connect()
      else:
        await ctx.voice_client.move_to(voice_channel)
    
    @commands.command()
    async def disconnect(self,ctx):
      await ctx.voice_client.disconnect()

    @commands.command(name='play', description='Play\'s music', aliases=['p'])
    async def play(self, ctx, *, url):
        if ctx.voice_client == None:
            await ctx.author.voice.channel.connect()

        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        

        if ctx.voice_client.is_playing():
            self.queue.insert(0,player)
            await ctx.send(f'Queued: `{url}`')
        else:
            def loop_play(e):
                if e:
                    print('Player error: %s' % e)
                else:
                    if len(self.queue) > 0:
                        ctx.voice_client.play(self.queue.pop(), after=loop_play)
                    else:
                        return

            ctx.voice_client.play(player, after=loop_play)
        await self.nowplaying(ctx)

    @commands.command(name='nowplaying', description='Music playing now', aliases=['np'])
    async def nowplaying(self,ctx):
        if ctx.voice_client != None:
            tmp = f'Now playing:  `{ctx.voice_client.source.title}`' \
                if ctx.voice_client.is_playing() else 'Not playing anything!'

            embed = discord.Embed(title=tmp, color=self.bot.embed_color)
            await ctx.send(embed=embed)

    @commands.command(name='queue', description='List music queue', aliases=['q'])
    async def queue(self,ctx):
        if ctx.voice_client != None:
            # TODO: indicate that is paused if that's the case
            if ctx.voice_client.source != None:
                embed = discord.Embed(title=f'Now playing:  `{ctx.voice_client.source.title}`',color=self.bot.embed_color)
                # self.nowplaying(ctx)
                
                _sizeq = len(self.queue)
                for i in range(_sizeq):
                    embed.add_field(name=f'**{i+1}.** `{self.queue[_sizeq-i-1].title}`', value='============================', inline=False)
                await ctx.send(embed=embed)
            elif self.queue == []:
               await ctx.send(embed=discord.Embed(title='Sadly the queue is empty :c',color=self.bot.embed_color))

    @commands.command()
    async def pause(self,ctx):
      await ctx.voice_client.pause()
      await ctx.send("Paused")

    @commands.command()
    async def resume(self,ctx):
      await ctx.voice_client.resume()
      await ctx.send("resume")

    @commands.command(name='skip', description='Stops current playing music and plays next in the queue',aliases=['s','n','next'])
    async def skip(self,ctx, next_idx=1):
        if next_idx < 0 or next_idx % int(next_idx) or next_idx > len(self.queue):
            print('invalid arg')
            return
        if ctx.voice_client.is_playing():
            if next_idx != 1:
                self.queue = self.queue[:(-1)*(next_idx-1)]
            ctx.voice_client.stop()
            print('ctx.voice_client.stop()')

def setup(client):
    client.add_cog(music(client))
