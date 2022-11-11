# these are the libraries used
import asyncio
import discord
from discord.ext import commands, tasks
import youtube_dl
from random import choice

# these are the ytdl format options used to search the song
youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilename': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtosderr': False,
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
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

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


client = commands.Bot(command_prefix=';')
status = ['Bangers', 'Melodies', 'Classics', 'Tunes']


@tasks.loop(seconds=10)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))


@client.event
async def on_ready():
    change_status.start()
    print('MuFi is Online!')


@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'Welcome {member.mention}! Ready to jam out? See `?help` command for details!')


# the ctx/context parameter is used to execute given command from the discord library
@client.command(name='ping', help='This command returns the latency')
async def ping(ctx):
    await ctx.send(f'Pong! Latency: {round(client.latency * 1000)}ms')


@client.command(name='hello', help='This command returns a random welcome message')
async def hello(ctx):
    responses = ('Hey there!!'
                 "\nThank you for choosing **MuFi❤** "
                 '\nThis is your gateway to bliss!! '''
                 '\nYou can use the *Help* command for any help '
                 '\nPlease feel free to contact us for any queries , suggestions and ratings!! '
                 '\nRegards, '
                 '\nTeam **🎶MuFi🎶**')
    await ctx.send(responses)


@client.command(name='credits', help='This command shows credits')
async def credits(ctx):
    responses = ('*Made by* '
                 ' \n**Sanket Satpute** '
                 ' \n**Karan Borade** '
                 ' \n**Sumit Puri** '
                 ' \n**Soham Jadhav** '
                 ' \n**Ketki More** ')
    await ctx.send(responses)


# command for bot to join the channel of the user, if the bot has already joined and is in a different channel,
# it will move to the channel the user is in
@client.command(name='join', help='This command makes the bot join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice.channel:
        await ctx.send("**You are not connected to a voice channel**")
        return

    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()
    await ctx.send("**The bot has joined the voice channel**")


# this command takes the audio from ffmpeg and plays the song in the voice channel
@client.command(name='play', help='This command plays music')
async def play(ctx, url):
    with ctx.typing():
        player = await YTDLSource.from_url(url, loop=client.loop)
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice_channel.play(player, after=lambda e: print('Player error:%s' % e) if e else None)

    await ctx.send('**🎶 Now playing 🎶 :** {}'.format(player.title))


# this command Pauses the song
@client.command(name='pause', help='This command pauses the current playing music')
async def pause(ctx):
    voice_client = ctx.voice_client
    if not voice_client or not voice_client.is_playing():
        embed = discord.Embed(title="", description='I am cuurently not playing anything', color=discord.Color.green())
        return await ctx.send(embed=embed)
    elif voice_client.is_paused():
        return

    voice_client.pause()
    await ctx.send('**Paused ⏸️**')


# This command resumes the Paused song
@client.command(name='resume', help='This command resumes the paused music')
async def resume(ctx):
    voice_client = ctx.voice_client
    if not voice_client or not voice_client.is_connected():
        embed = discord.Embed(title="", description=" I'm not connected to a voice channel",
                              color=discord.Color.green())
        return await ctx.send(embed=embed)
    elif not voice_client.is_paused():
        return
    voice_client.resume()
    await ctx.send("**Resuming ⏯️**")


# this commands disconnects the bot from the voice channel
@client.command(name='stop', help='This command stops the music and makes the bot leave the voice channel')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()
    await ctx.send("**The bot has left the voice channel ❗❗❗ **")

# this contains the bot token.
client.run('Enter Your Bot Token')
