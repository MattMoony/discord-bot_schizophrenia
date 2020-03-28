import json
import gtts
import copy
import discord
import logging
from io import BufferedReader
from tempfile import TemporaryFile
from argparse import ArgumentParser

class Schizophrenia(discord.Client):
    def __init__(self):
        super(Schizophrenia, self).__init__()

        # define possible commands
        self.cmds = {
            'ping': self.pong,
            'join': self.join,
            'leave': self.leave,
            'lang': self.lang,
            'volume': self.volume
        }
        # define internal status
        self.stat = {
            'speak': False,
            'lang': 'en',
            'langs': list(gtts.lang.tts_langs().keys()),
            'volume': 1.,
            'vclient': None
        }

    async def on_ready(self):
        print('[bot.py]: User ({0.user}) ready ... '.format(self))

    async def on_message(self, msg):
        # handle self-written msgs
        if msg.author == self.user:
            return

        # handle commands
        if msg.content.startswith('$'):
            for k, v in self.cmds.items():
                if msg.content.startswith('${:}'.format(k)):
                    await v(msg)
            return

        # handle messages
        if self.stat['speak']:
            sp_fp = TemporaryFile()
            # speech = gtts.gTTS('{0.author.nick}: {0.content}'.format(msg), self.stat['lang'])
            speech = gtts.gTTS(msg.content, lang=self.stat['lang'])
            speech.write_to_fp(sp_fp)

            if self.stat['vclient']:
                sp_fp.seek(0)
                reader = BufferedReader(sp_fp)
                source = discord.FFmpegPCMAudio(reader, pipe=True)
                transf = discord.PCMVolumeTransformer(source, self.stat['volume'])
                self.stat['vclient'].play(transf)

    async def pong(self, msg):
        await msg.channel.send('Pong!')

    async def join(self, msg):
        if not msg.author.voice:
            await msg.channel.send('{0.author.mention}, please join a voice channel first!'.format(msg))
        else:
            if self.stat['speak']:
                await self.leave(msg)

            parts = msg.content.split(' ')
            if len(parts) > 1:
                nmsg = copy.copy(msg)
                nmsg.content = '$lang {:}'.format(parts[1])
                await self.lang(nmsg)

            channel = msg.author.voice.channel
            self.stat['speak']          = True
            self.stat['vclient']        = await channel.connect()

    async def leave(self, msg):
        if not self.stat['vclient']:
            await msg.channel.send('{0.author.mention}, I\'m not in a voice channel!'.format(msg))
        else:
            self.stat['speak']          = False
            self.stat['vclient']        = await self.stat['vclient'].disconnect()

    async def lang(self, msg):
        parts = msg.content.split(' ')

        if len(parts) == 1:
            await msg.channel.send('{0.author.mention}, please specify a language like so: `$lang <language-code>`!'.format(msg))
        elif not parts[1] in self.stat['langs']:
            await msg.channel.send('{0.author.mention}, unknown language!'.format(msg))
        else:
            self.stat['lang'] = parts[1]
            await msg.channel.send('Language has been changed to {:}.'.format(gtts.lang.tts_langs()[parts[1]]))

    async def volume(self, msg):
        parts = msg.content.split(' ')

        if len(parts) == 1:
            await msg.channel.send('{0.author.mention}, please specify a language like so: `$volume <number]0.;...]>`!'.format(msg))
        else:
            try:
                n = float(parts[1])
                if n <= 0:
                    await msg.channel.send('{0.author.mention}, volume has to be greater than 0!'.format(msg))
                else:
                    self.stat['volume'] = n
                    await msg.channel.send('Volume has been raised to {:.2f}%.'.format(100.*n))
            except ValueError:
                await msg.channel.send('{0.author.mention}, volume has to be a floating-point number!'.format(msg))

def main():
    # load auth file
    with open('auth.json', 'r') as f:
        auth = json.load(f)

    # create parser
    parser = ArgumentParser()
    parser.add_argument('--debug', action='store_true', dest='debug', help='Flag; debug mode?')
    args = parser.parse_args()

    if args.debug:
        # set up debug-logger
        logger = logging.getLogger('discord')
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('./bot.log', mode='w', encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        logger.addHandler(handler)
    else:
        # set up warning-logger
        logging.basicConfig(level=logging.WARNING)

    # create bot
    bot = Schizophrenia()
    bot.run(auth['token'])

if __name__ == '__main__':
    main()