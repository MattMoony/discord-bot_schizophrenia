import json, discord, datetime, random, asyncio, threading
from discord.ext import commands
from bs4 import BeautifulSoup
import pydub as pb
import requests as req

with open('conf.json', 'r') as f:
    conf = json.load(f)

bot = commands.Bot(command_prefix=conf['command_prefix'])

# == EVENT-LOOPS =================================================== #

async def _bully_loop():
    while not bot.is_closed():
        for u in conf['bullying']:
            await do_bully(u)
        await asyncio.sleep(conf['bully_timeout'])

# == HELPERS ======================================================= #

async def _send_rnd_msg(u):
    await u.trigger_typing()
    await u.send(get_random_chuck())

async def _disconnect(u):
    await u.move_to(None, reason='lel')

async def _mute(u):
    await u.edit(mute=True)

async def _deafen(u):
    await u.edit(deafen=True)

async def _change_nick(u):
    await u.edit(nick=get_random_nick())

async def do_bully(u):
    try:
        await WEAPONRY[random.randint(0,len(WEAPONRY)-1)](u)
    except Exception:
        pass

def get_random_chuck():
    res = req.get('https://api.icndb.com/jokes/random')
    if not res.ok:
        return conf['bully_msg']
    res = json.loads(res.text)
    if res['type'] != 'success':
        return conf['bully_msg']
    return res['value']['joke']

def get_random_nick():
    try:
        # return '_'.join(json.loads(req.get('http://names.drycodes.com/2?nameOptions=objects&combine=1').text)).lower() +\
        #     ' - ' +\
        #     json.loads(req.get('https://api.namefake.com/').text)['name']
        return json.load(req.get('https://api.namefake.com').text)['name']
    except Exception as e:
        print(e)
        return '1337 - Nick Name'

WEAPONRY = [ _send_rnd_msg, _disconnect, _mute, _deafen, _change_nick]

# == COMMANDS ====================================================== #

@bot.command()
async def join(ctx):
    if conf['vc']:
        await leave(ctx)
    conf['vc'] = await ctx.author.voice.channel.connect()
    
@bot.command()
async def leave(ctx):
    if not conf['vc']:
        await ctx.message.channel.send('{}: I\'m in no voice channel'.format(ctx.author.mention))
        return
    await conf['vc'].disconnect()
    conf['vc'] = None

@bot.command()
async def bully(ctx):
    if not ctx.message.mentions:
        await ctx.message.channel.send('{}: You forgot to tag a user ... *pathetic*'.format(ctx.author.mention))
        return
    await ctx.message.channel.send('{}: {} will be bullied! (I\'ll put my best man on it ... me :smiling_imp:)'.format(ctx.author.mention, ', '.join([u.nick for u in ctx.message.mentions])))
    conf['bullying'] = [*conf['bullying'], *ctx.message.mentions]

@bot.command()
async def nbully(ctx):
    if not ctx.message.mentions:
        await ctx.message.channel.send('{}: You forgot to tag somebody ... *dummy*'.format(ctx.author.mention))
        return
    await ctx.message.channel.send('{}: {} won\'t be bullied anymore ... :cry:'.format(ctx.author.mention, ', '.join([u.nick for u in ctx.message.mentions if u in conf['bullying']])))
    conf['bullying'] = filter(lambda u: u not in ctx.message.mentions, conf['bullying'])

@bot.command()
async def lbully(ctx):
    if not conf['bullying']:
        await ctx.message.channel.send('{}: Currently bullying no one ... :cry:'.format(ctx.author.mention))
        return
    await ctx.message.channel.send('{}: Currently bullying: {} ... noice!'.format(ctx.author.mention, ', '.join([u.nick for u in conf['bullying']])))

# == EVENTS ======================================================== #

@bot.event
async def on_ready():
    print('[schizophrenia]: Ready as {} ...'.format(bot.user.name))
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=conf['activities'][random.randint(0,len(conf['activities'])-1)]))

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    if msg.content.startswith(bot.command_prefix):
        await bot.process_commands(msg)
        return
    await msg.channel.send(msg.content)

def main():
    asyncio.ensure_future(_bully_loop())
    bot.run(conf['token'])

if __name__ == '__main__':
    main()