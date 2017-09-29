import discord
import random
import re
import math
import time
#import deuces
from deuces.card import Card
from deuces.evaluator import Evaluator
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
firstRound = 1
voteInProgress = 0
queue = {}
voteMessage = None
voted = []
emojis = []
bettingInProgress = 0
playerTurn = 0
players = {}
table = []
playerAmount = {}
hands = defaultdict(list)
board = []
pokerRole = None
pokerChannel = None
bigBlind = 0
bigBlindPos = 0
smallBlind = 0
smallBlindPos = 1
result = 0
pot = 0
bettingRoundAMount = 0
isTurnTable = 0

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

async def evaluateHand():
    global table
    global hands
    global board
    global firstRound
    finalBoard = []
    finalHands = []
    handWinner = None
    max = 0
    eval = Evaluator()
    #TODO make new tuple of new string in card
    for card in board:
        card[1] = card[1].replace('10', 'T')
        print(card)
        finalBoard.append(Card.new(card[1][0]+card[0][0].lower()))

    print(finalBoard)
    #TODO make new tuple of new string in card
    for p in table:
        for card in hands[p]:
            card[1] = card[1].replace('10', 'T')
            print(card)
            finalHands.append(Card.new(card[1][0]+card[0][0].lower()))

        print(finalHands)

        if eval.evaluate(finalBoard, finalHands) > max:
            max = eval.evaluate(finalBoard, finalHands)
        print(eval.evaluate(finalBoard, finalHands))
        finalHands = []

    handWinner = p
    player[p] += pot
    firstRound = 0
    await bot.send_message(pokerChannel, p + " won the round! Use command startPoker to start another one!")

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

async def showboard(player,printedboard):
    boardString = ''
    for printedLine in printedboard:
        boardString += printedLine + '\n'
    await bot.send_message(player, "*This is the board*\n" + boardString)

async def showTable():
    global table
    global playerTurn
    scoreboard = 'Table\n'
    for player in table:
        if table[playerTurn] == player:
            scoreboard += '* '
        else:
            scoreboard += '  '
        scoreboard += player.display_name + ' '
        scoreboard += str(players[player]) + '$\n'
    await bot.send_message(pokerChannel, scoreboard)

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

async def startNewGame():
    global isRound
    isRound = 0
    global nextRound
    nextRound = 0
    global playerAmount
    playerAmount = {}
    global playerTurn
    playerTurn = 0 
    global pot
    pot = 0
    global hands
    hands = {}
    global bigBlindPos
    global smallBlindPos
    global isTurnTable
    isTurnTable = 0
    global bettingInProgress
    bettingInProgress = 0
    global queue
    for p,money in queue:
        player[p] = money
        table = p
    
    bigBlindPos += bigBlindPos
    smallBlindPos += smallBlindPos
    playerTurn = bigBlindPos

async def showMoney(player, moneyRemaining, bettingAmount):
    global pot
    await bot.send_message(pokerChannel, table[bigBlindPos].display_name + "'s money: " + str(players[table[bigBlindPos]]) + " betting amount: " + str(playerAmount[table[bigBlindPos]]) + "\nPot is at " + str(pot))

async def playPokerRound(roundNumber):
    global bigBlind
    global smallBlind
    global table
    global playerAmount
    global bettingInProgress
    global pot
    global nextRound
    nextRound = 0
    if roundNumber == 0:
        players[table[bigBlindPos]] -= bigBlind
        playerAmount[table[bigBlindPos]] = bigBlind
        pot += bigBlind
        players[table[smallBlindPos]] -= smallBlind
        playerAmount[table[smallBlindPos]] = smallBlind
        pot += smallBlind
        await showMoney(table[bigBlindPos], players[table[bigBlindPos]], playerAmount[table[bigBlindPos]])
        bettingInProgress = 1
        await deal(1)
        await deal(0)
        await showTable()
    elif roundNumber == 1:
        bettingInProgress = 1
        await flip(1)
        await flip(1)
        await flip(0)
        await showTable()
    elif roundNumber == 2:
        bettingInProgress = 1
        await flip(0)
        await showTable()
    elif roundNumber == 3:
        bettingInProgress = 1
        await flip(0)
        await showTable()
    elif roundNumber == 4:
        await evaluateHand()


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
    board.append(cardFlipped)
    printedboard = printHand(board)
    if not isTwoFirstCard:
        for player in players:
            await showboard(player,printedboard)

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
            voteInProgress = 0
            if result > 0:
                await bot.send_message(voteMessage.channel, 'Big blind has been set to ' + str(bigBlind) + ' and small blind has been set to ' + str(smallBlind) + '.')
            else:
                await bot.send_message(voteMessage.channel, 'Vote has failed')
                bigBlind = 0
                smallBlind = 0

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
    global isTurnTable
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
                    isRound = 0
                    bettingInProgress = 0
                    voteInProgress = 0
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
                        queue[message.author] = 3000
                        await bot.send_message(message.channel,'You have been added to the queue, wait until the next game')
                else:
                    await bot.send_message(message.channel,'Game has not been initiated yet, use command playPoker to start.')

            if command == 'startPoker':
                if isGame:
                    if not isRound:
                        if len(players) > 1:
                            shuffle(cardList)
                            if firstRound:
                                await setupPoker()
                            else:
                                await startNewGame()
                            isRound = 1
                            await playPokerRound(0)
                        else:
                            await bot.send_message(message.channel, 'Not enough players in the lobby.' + '\n' +
                                                                    'Use the command viewPlayers to see the lobby.' + '\n' +
                                                                    'Use the command join to add yourself to the lobby.')
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
                    if len(board) < 3:
                        await playPokerRound(1)
                    elif len(board) < 4:
                        await playPokerRound(2)
                    elif len(board) < 5:
                        await playPokerRound(3)
                    elif len(board) == 5:
                        await playPokerRound(4)
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
                if bettingInProgress:
                    if message.author == table[playerTurn]:
                        raisedAmount = int(re.search(r'\d+$',command).group())
                        if raisedAmount <= players[message.author]:
                            if raisedAmount + playerAmount[message.author] > max(playerAmount.values()):
                                players[message.author] -= raisedAmount
                                playerAmount[message.author] += raisedAmount
                                pot += raisedAmount
                                if ((playerTurn + 1) % (len(table))) == bigBlindPos:
                                    isTurnTable = 1
                                await showMoney(table[playerTurn], players[table[playerTurn]], playerAmount[table[playerTurn]])
                                if all( value == max(playerAmount.values()) for value in playerAmount.values()) and isTurnTable:
                                    bettingInProgress = 0
                                    nextRound = 1
                                    playerTurn = bigBlindPos
                                    isTurnTable = 0
                                    await bot.send_message(message.channel, 'Round is over, use command nextRound to start the next one.')
                                else:
                                    playerTurn = (playerTurn + 1) % (len(table))
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
                if bettingInProgress:
                    if message.author == table[playerTurn]:
                        if playerAmount[message.author] == max(playerAmount.values()):
                            if ((playerTurn + 1) % (len(table))) == bigBlindPos:
                                isTurnTable = 1
                            await showMoney(table[playerTurn], players[table[playerTurn]], playerAmount[table[playerTurn]])
                            if all( value == max(playerAmount.values()) for value in playerAmount.values()) and isTurnTable:
                                bettingInProgress = 0
                                nextRound = 1
                                playerTurn = bigBlindPos
                                isTurnTable = 0
                                await bot.send_message(message.channel, 'Round is over, use command nextRound to start the next one.')
                            else:
                                playerTurn = (playerTurn + 1) % (len(table))
                                await bot.send_message(message.channel, message.author.display_name + ' has checked.')
                                await bot.send_message(message.channel, "It's now " + table[playerTurn].display_name + "'s turn.")
                        else:
                            await bot.send_message(message.channel, "You can't call dummy. Learn how to play the game!")
                    else:
                        await bot.send_message(message.channel, "Wait for your turn. Jeez.")
            #NOTTESTED
            if command == 'call':
                if bettingInProgress:
                    if message.author == table[playerTurn]:
                        raisedAmount = max(playerAmount.values()) - playerAmount[message.author]
                        if raisedAmount <= players[message.author]:
                            players[message.author] -= raisedAmount
                            playerAmount[message.author] += raisedAmount
                            pot += raisedAmount
                            if ((playerTurn + 1) % (len(table))) == bigBlindPos:
                                isTurnTable = 1
                            await showMoney(table[playerTurn], players[table[playerTurn]], playerAmount[table[playerTurn]])
                            if all( value == max(playerAmount.values()) for value in playerAmount.values()) and isTurnTable:
                                    bettingInProgress = 0
                                    nextRound = 1
                                    playerTurn = bigBlindPos
                                    isTurnTable = 0
                                    await bot.send_message(message.channel, 'Round is over, use command nextRound to start the next one.')
                            else:
                                playerTurn = (playerTurn + 1) % (len(table))
                                await bot.send_message(message.channel, message.author.display_name + ' has called.')
                                await bot.send_message(message.channel, "It's now " + table[playerTurn].display_name + "'s turn.")
                        else:
                            await bot.send_message(message.channel, 'Your too poor for that')
                    
                    else:
                        await bot.send_message(message.channel, "Wait for your turn. Jeez.")

            if command == 'fold':
                if bettingInProgress:
                    if message.author == table[playerTurn]:
                        name = table[playerTurn].display_name
                        del hands[table[playerTurn]]
                        del table[playerTurn]
                        if ((playerTurn + 1) % (len(table))) == bigBlindPos:
                            isTurnTable = 1
                        if all( value == max(playerAmount.values()) for value in playerAmount.values()) and isTurnTable:
                            bettingInProgress = 0
                            nextRound = 1
                            playerTurn = bigBlindPos
                            isTurnTable = 0
                            await bot.send_message(message.channel, name + ' has been removed from the table.')
                        else:
                            playerTurn = (playerTurn + 1) % (len(table))
                            await bot.send_message(message.channel, name + " has been removed from the table\nIt's now " + table[playerTurn].display_name + "'s turn.")
                    else:
                        await bot.send_message(message.channel, "Wait for your turn. Jeez.")

            

bot.run(token)
