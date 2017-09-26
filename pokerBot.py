import discord
import random
import re
import math
import time
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
isRound = 0
nextRound = 0
voteInProgress = 0
voteMessage = None
voted = []
emojis = []
bettingInProgress = 0
playerTurn = 0
players = {}
table = []
playerAmount = {}
hands = defaultdict(list)
flop = []
pokerRole = None
pokerChannel = None
bigBlind = 0
bigBlindPos = 0
smallBlind = 0
smallBlindPos = 1
result = 0
pot = 0
bettingRoundAMount = 0
cardList = [('Hearts', '2'),('Hearts', '3'),('Hearts', '4'),('Hearts', '5'),('Hearts', '6'),
            ('Hearts', '7'),('Hearts', '8'),('Hearts', '9'),('Hearts', '10'),('Hearts', 'Jack'),
            ('Hearts', 'Queen'),('Hearts', 'King'),('Hearts', 'Ace'),
            ('Spades', '2'),('Spades', '3'),('Spades', '4'),('Spades', '5'),
            ('Spades', '6'),('Spades', '7'),('Spades', '8'),('Spades', '9'),('Spades', '10'),
            ('Spades', 'Jack'),('Spades', 'Queen'),('Spades', 'King'),('Spades', 'Ace'),
            ('Diamonds', '2'),('Diamonds', '3'),('Diamonds', '4'),('Diamonds', '5'),
            ('Diamonds', '6'),('Diamonds', '7'),('Diamonds', '8'),('Diamonds', '9'),('Diamonds', '10'),
            ('Diamonds', 'Jack'),('Diamonds', 'Queen'),('Diamonds', 'King'),('Diamonds', 'Ace'),
            ('Clubs', '2'),('Clubs', '3'),('Clubs', '4'),('Clubs', '5'),('Clubs', '6'),
            ('Clubs', '7'),('Clubs', '8'),('Clubs', '9'),('Clubs', '10'),('Clubs', 'Jack'),
            ('Clubs', 'Queen'),('Clubs', 'King'),('Clubs', 'Ace')]

async def showHand(player,printedHand):
    handString = ''
    for printedLine in printedHand:
        handString += printedLine + '\n'
    await bot.send_message(player, handString)

async def showHands():
    for player in table:
        printedHand = printHand(hands[player])
        handString = str(player.display_name) + "'s hand\n"
        for printedLine in printedHand:
            handString += printedLine + '\n'
        await bot.send_message(pokerChannel, handString)

async def showFlop(player,printedFlop):
    flopString = ''
    for printedLine in printedFlop:
        flopString += printedLine + '\n'
    await bot.send_message(player, "*This is the board*\n" + flopString)

async def setupPoker():
    global table
    global playerAmount
    for player in players:
        table.append(player)
        playerAmount[player] = 0
    random.shuffle(table)
    blindNotSet = 1
    while(blindNotSet):
        if players[table[bigBlindPos]] < bigBlind:
            players.pop(table[bigBlindPos], None)
            removedPlayer = table.pop(bigBlindPos)
        else:
            blindNotSet = 0
    await bot.send_message(pokerChannel, "Big blind is " + table[bigBlindPos].display_name)
    await bot.send_message(pokerChannel, "Small blind is " + table[smallBlindPos].display_name)

async def playPokerRound(roundNumber):
    global bigBlind
    global smallBlind
    global table
    global playerAmount
    global bettingInProgress
    if roundNumber == 0:
        players[table[bigBlindPos]] -= bigBlind
        playerAmount[table[bigBlindPos]] = bigBlind
        players[table[smallBlindPos]] -= smallBlind
        playerAmount[table[smallBlindPos]] = smallBlind
        bettingInProgress = 1
        await deal(1)
        await deal(0)
    elif roundNumber == 1:
        bettingInProgress = 1
        await flip(1)
        await flip(1)
        await flip(0)
    elif roundNumber == 2:
        bettingInProgress = 1
        await flip(0)
    elif roundNumber == 3:
        bettingInProgress = 1
        await flip(0)
    #elif roundNumber == 4:

async def deal(isFirstCard):
    global cardList
    global table
    for player in table:
        hands[player].append(cardList.pop(0))
        printedHand = printHand(hands[player])
        if not isFirstCard:
            await showHand(player,printedHand)

async def flip(isTwoFirstCard):
    global cardList
    cardFlipped = cardList.pop(0)
    flop.append(cardFlipped)
    printedFlop = printHand(flop)
    if not isTwoFirstCard:
        for player in players:
            await showFlop(player,printedFlop)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_reaction_add(reaction, user):
    global voteInProgress, voted, voteMessage, emojis, bigBlind, smallBlind, result, players
    if voteInProgress and reaction.message.id == voteMessage.id and user.id not in voted and user != bot.user and (reaction.emoji == u"\U0001F44D" or reaction.emoji == u"\U0001F44E"):
        if len(voted) < len(players)-1:
            emojis.append(reaction.emoji)
            voted.append(user.id)
        else:
            emojis.append(reaction.emoji)
            result = emojis.count(u"\U0001F44D")-emojis.count(u"\U0001F44E")
            #await bot.send_message(reaction.message.channel, "Vote results: " + str(results))
            voting = False
            if result > 0:
                voteInProgress = 0
                await bot.send_message(voteMessage.channel, 'Big blind has been set to ' + str(bigBlind) + ' and small blind has been set to ' + str(smallBlind) + '.')
            else:
                await bot.send_message(voteMessage.channel, 'Vote has failed')
                bigBlind = 0
                smallBlind = 0
                voteInProgress = 0

@bot.event
async def on_message(message):
    global isGame
    global isRound
    global nextRound
    global players
    global playerAmount
    global playerTurn
    global pot
    global pokerRole
    global pokerChannel
    global hands
    global bigBlind
    global smallBlind
    global bettingInProgress
    global voteInProgress, voted, voteMessage, emojis
    if message.author.id != bot.user.id:
        if message.content[0] == command_prefix:
            command = message.content[1:]

            if command == 'playPoker':
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
                    if not isRound:
                        players[message.author] = 3000
                        await bot.add_roles(message.author, pokerRole)
                        await bot.send_message(message.channel,'You have been added to the game!')
                    else:
                        await bot.send_message(message.channel,'Round in progress, but you can still join in the next one!')
                else:
                    await bot.send_message(message.channel,'Game has not been initiated yet, use command playPoker to start.')

            if command == 'startPoker':
                if isGame:
                    if not isRound:
                        #if len(players) > 1:
                        shuffle(cardList)
                        await setupPoker()
                        isRound = 1
                        await playPokerRound(0)
                        #else:
                            #await bot.send_message(message.channel, 'Not enough players in the lobby.' + '\n' +
                            #                                        'Use the command viewPlayers to see the lobby.' + '\n' +
                            #                                        'Use the command join to add yourself to the lobby.')
                    else:
                        await bot.send_message(message.channel,'Round already in progress.')
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
            #NOTTESTED
            if command == 'nextRound':
                if nextRound == 1:
                    if len(flop) < 3:
                        await playPokerRound(1)
                    elif len(flop) < 4:
                        await playPokerRound(2)
                    elif len(flop) < 5:
                        await playPokerRound(3)
            #NOTTESTED
            if re.search(r'setBlind [0-9]+$',command):
                if isGame:
                    if not voteInProgress:
                        bigBlind = int(re.search(r'\d+$',command).group())
                        smallBlind = math.floor(bigBlind/2)
                        voteInProgress = 1
                        voted = []
                        emojis = []
                        voteMessage = await bot.send_message(message.channel, "Set blind to " + str(bigBlind) + "?")
                        await bot.add_reaction(voteMessage, u"\U0001F44D")
                        await bot.add_reaction(voteMessage, u"\U0001F44E")
                    else:
                        await bot.send_message(message.channel, 'A vote is already in progress')
            #NOTTESTED
            #Commands that work when betting is in progress
            if re.search(r'raise [0-9]+$',command):
                print(bettingInProgress)
                if bettingInProgress:
                    print(playerTurn)
                    print(table[playerTurn])
                    print(message.author)
                    if message.author == table[playerTurn]:
                        raisedAmount = re.search(r'\d+$',command)
                        if raisedAmount <= players[message.author]:
                            if raisedAmount + playerAmount[message.author] > max(playerAmount.values()):
                                players[message.author] - raisedAmount
                                playerAmount[message.author] += raisedAmount
                                pot += raisedAmount
                                if all( value == max(playerAmount.values()) for value in playerAmount.values()):
                                    bettingInProgress = 0
                                    nextRound = 1
                                    playerTurn = table[bigBlindPos]
                                    await bot.send_message(message.channel, 'Round is over, use command nextRound to start the next one.')
                                else:
                                    playerTurn += 1 % len(table)
                                    await bot.send_message(message.channel, message.author.display_name + ' has raised.')
                                    await bot.send_message(message.channel, "It's now " + table[playerTurn].display_name + "'s turn.")
                            else:
                                await bot.send_message(message.channel, 'Not a raise')
                        else:
                            await bot.send_message(message.channel, 'Your too poor for that')
                    else:
                        await bot.send_message(message.channel, "Wait for your turn. Jeez.") 
            #NOTTESTED
            if command == 'check':
                print(bettingInProgress)
                if bettingInProgress:
                    print(playerTurn)
                    print(table[playerTurn])
                    print(message.author)
                    if message.author == table[playerTurn]:
                        print(max(playerAmount.values()))
                        print(playerAmount[message.author])
                        if playerAmount[message.author] == max(playerAmount.values()):
                            if all( value == max(playerAmount.values()) for value in playerAmount.values()):
                                bettingInProgress = 0
                                nextRound = 1
                                playerTurn = table[bigBlindPos]
                                await bot.send_message(message.channel, 'Round is over, use command nextRound to start the next one.')
                            else:
                                playerTurn += 1 % len(table)
                                await bot.send_message(message.channel, message.author.display_name + ' has checked.')
                                await bot.send_message(message.channel, "It's now " + table[playerTurn].display_name + "'s turn.")
                        else:
                            await bot.send_message(message.channel, "You can't call dummy. Learn how to play the game!")
                    else:
                        await bot.send_message(message.channel, "Wait for your turn. Jeez.")
            #NOTTESTED
            if command == 'call':
                print(bettingInProgress)
                if bettingInProgress:
                    print(playerTurn)
                    print(table[playerTurn])
                    print(message.author)
                    if message.author == table[playerTurn]:
                        print(max(playerAmount.values()))
                        print(playerAmount[message.author])
                        raisedAmount = max(playerAmount.values()) - playerAmount[message.author]
                        if raisedAmount <= players[message.author]:
                            players[message.author] - raisedAmount
                            playerAmount[message.author] += raisedAmount
                            pot += raisedAmount
                            if all( value == max(playerAmount.values()) for value in playerAmount.values()):
                                    bettingInProgress = 0
                                    nextRound = 1
                                    playerTurn = table[bigBlindPos]
                                    await bot.send_message(message.channel, 'Round is over, use command nextRound to start the next one.')
                            else:
                                playerTurn += 1 % len(table)
                                await bot.send_message(message.channel, message.author.display_name + ' has called.')
                                await bot.send_message(message.channel, "It's now " + table[playerTurn].display_name + "'s turn.")
                        else:
                            await bot.send_message(message.channel, 'Your too poor for that')
                    
                    else:
                        await bot.send_message(message.channel, "Wait for your turn. Jeez.")

            if command == 'fold':
                if bettingInProgress:
                    if message.author == table[playerTurn]:
                        del table[player]
                        del hands[player]
                        if all( value == max(playerAmount.values()) for value in playerAmount.values()):
                            bettingInProgress = 0
                            nextRound = 1
                            playerTurn = table[bigBlindPos]
                        else:
                            playerTurn += 1 % len(table)
                    else:
                        await bot.send_message(message.channel, "Wait for your turn. Jeez.")

bot.run(token)
