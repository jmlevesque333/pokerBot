import discord
import random
from printCard import *
from random import shuffle
from collections import defaultdict

description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''
bot = discord.Client()
command_prefix = '?'

token = 'MzYwNzczMzA5MjA3NDEyNzQ3.DKab4A.lFqitkifVbqtioZi6Yj6Y9JtQcU'

isGame = 0
players = {}
hands = defaultdict(list)
pokerRole = None
pokerChannel = None
cardList = [('Hearts', '1'),('Hearts', '2'),('Hearts', '3'),('Hearts', '4'),('Hearts', '5'),
            ('Hearts', '6'),('Hearts', '7'),('Hearts', '8'),('Hearts', '9'),('Hearts', '10'),
            ('Hearts', 'Jack'),('Hearts', 'Queen'),('Hearts', 'King'),('Hearts', 'Ace'),
            ('Spades', '1'),('Spades', '2'),('Spades', '3'),('Spades', '4'),('Spades', '5'),
            ('Spades', '6'),('Spades', '7'),('Spades', '8'),('Spades', '9'),('Spades', '10'),
            ('Spades', 'Jack'),('Spades', 'Queen'),('Spades', 'King'),('Spades', 'Ace'),
            ('Diamonds', '1'),('Diamonds', '2'),('Diamonds', '3'),('Diamonds', '4'),('Diamonds', '5'),
            ('Diamonds', '6'),('Diamonds', '7'),('Diamonds', '8'),('Diamonds', '9'),('Diamonds', '10'),
            ('Diamonds', 'Jack'),('Diamonds', 'Queen'),('Diamonds', 'King'),('Diamonds', 'Ace'),
            ('Clubs', '1'),('Clubs', '2'),('Clubs', '3'),('Clubs', '4'),('Clubs', '5'),
            ('Clubs', '6'),('Clubs', '7'),('Clubs', '8'),('Clubs', '9'),('Clubs', '10'),
            ('Clubs', 'Jack'),('Clubs', 'Queen'),('Clubs', 'King'),('Clubs', 'Ace')]

async def deal():
    global cardList
    for player in players:
        hands[player].append(cardList.pop(0))
        printedHand = printHand(hands[player])
        await bot.send_message(player, printedHand)

async def flip():
    global cardList
    cardFlipped = cardList.pop(0)
    for player in players:
        hands[player].append(cardFlipped)
        printedHand = printHand(hands[player])
        await bot.send_message(player,printedHand)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_message(message):
    global isGame
    global players
    global pokerRole
    global pokerChannel
    global hands
    message.content.encode('utf-8')
    msg = message.content
    if message.author.id != bot.user.id:
        print(msg[0])
        print(msg)
        if message.content[0] == command_prefix:
            command = message.content[1:]

            if command == 'playPoker':
                await bot.send_message(message.channel,u"\u02E5")
                if isGame:
                    await bot.send_message(message.channel,'Games already bing played. Game can be restarted with command restart.')
                else:
                    isGame = 1
                    pokerRole = await bot.create_role(message.server)
                    await bot.edit_role(message.server, pokerRole, name = 'pokerPlayer')
                    pokerPlayerPerms = discord.PermissionOverwrite(read_messages=False)
                    everyoneElsePerms = discord.PermissionOverwrite(read_messages=True)
                    pokerPlayers = discord.ChannelPermissions(target=pokerRole, overwrite=pokerPlayerPerms)
                    everyoneElse = discord.ChannelPermissions(target=message.server.default_role, overwrite=everyoneElsePerms)
                    pokerChannel = await bot.create_channel(message.server, 'pokerSpectators',everyoneElse, pokerPlayers)
                    await bot.send_message(message.channel,'Game is about to start, use command join to join the fun!')

            if command == 'stopPoker':
                if isGame:
                    isGame = 0
                    await bot.delete_channel(pokerChannel)
                    await bot.delete_role(message.server, pokerRole)
                    await bot.send_message(message.channel, "Game has been stopped.")
                else:
                    await bot.send_message(message.channel, "No game in progress.")

            if command == 'join':
                if isGame:
                    players[message.author] = 3000
                    await bot.add_roles(message.author, pokerRole)
                    await bot.send_message(message.channel,'You have been added to the game!')
                else:
                    await bot.send_message(message.channel,'Game has not been initiated yet, use command playPoker to start.')

            if command == 'startPoker':
                if isGame:
                    #if len(players) > 1:
                    shuffle(cardList)
                    await deal()
                    await deal()
                    #else:
                        #await bot.send_message(message.channel, 'Not enough players in the lobby.' + '\n' +
                        #                                        'Use the command viewPlayers to see the lobby.' + '\n' +
                        #                                        'Use the command join to add yourself to the lobby.')
                else:
                    await bot.send_message(message.channel, 'Game has not been initiated yet.')

            if command == 'viewPlayers':
                if isGame:
                    sendPlayers = ''
                    for player,money in players.items():
                        sendPlayers = sendPlayers + player.display_name + ' ' + str(money) + '\n'
                    await bot.send_message(message.channel,sendPlayers)
                else:
                    await bot.send_message(message.channel,'Game has not been started, use command playPoker to start.')

bot.run(token)
