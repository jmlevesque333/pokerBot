import discord
import random

description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''
bot = discord.Client()
command_prefix = '?'

token = 'MzYwNzczMzA5MjA3NDEyNzQ3.DKab4A.lFqitkifVbqtioZi6Yj6Y9JtQcU'

isGame = 0
players = {}

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    role = bot.create_role(bot.servers, name = 'N.I.L')
    bot.edit_role(server, role, name = 'pokerPlayer', colour = 'red')


@bot.event
async def on_message(message):
    global isGame
    global players
    if message.author.id != bot.user.id:
        if message.content[0] == command_prefix:
            command = message.content[1:]

            if command == 'playPoker':
                if isGame:
                    
                    await bot.send_message(message.channel,'Games already bing played. Game can be restarted with command restart.')
                else:
                    isGame = 1
                    await bot.send_message(message.channel,'Game is about to start, use command join to join the fun!')

            if command == 'join':
                if isGame:
                    players[message.author] = 3000
                    await bot.send_message(message.channel,'You have been added to the game! :sexyjayjay:')
                    


                    bot.add_roles(message.author,)
                else:
                    await bot.send_message(message.channel,'Game has not been started, use command playPoker to start.')

            if command == 'viewPlayers':
                if isGame:
                    sendPlayers = ''
                    for player,money in players.items():
                        sendPlayers = sendPlayers + player.display_name + ' ' + str(money) + '\n'
                    await bot.send_message(message.channel,sendPlayers)
                else:
                    await bot.send_message(message.channel,'Game has not been started, use command playPoker to start.')

bot.run(token)
