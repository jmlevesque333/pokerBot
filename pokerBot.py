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

isGame = []
isRound = []
nextRound = []
firstRound = []
voteInProgress = []
voteMessage = []
voted = []
emojis = []
bettingInProgress = []
playerTurn = []
players = []
table = []
playerAmount = []
hands = []
board = []
pokerRole = []
pokerChannel = []
bigBlind = []
bigBlindPos = []
smallBlind = []
smallBlindPos = []
result = []
pot = []
bettingRoundAMount = []
isTurnTable = []
servers = []

cardList = []

async def evaluateHand(whichServer):
    global table
    global hands
    global board
    global isRound
    global firstRound
    global players
    global pot
    finalBoard = []
    finalHands = []
    handWinner = []
    max = 100000
    eval = Evaluator()
    #TODO make new tuple of new string in card
    for card in board[whichServer]:
        temp1 = card[1].replace('10', 'T')
        temp2 = card[0].lower()
        temp3 = Card.new(temp1[0]+temp2[0])
        finalBoard.append(temp3)

    #TODO make new tuple of new string in card
    for p in table[whichServer]:
        for card in hands[whichServer][p]:
            temp1 = card[1].replace('10', 'T')
            temp2 = card[0].lower()
            temp3 = Card.new(temp1[0]+temp2[0])
            finalHands.append(temp3)

        valueOfHand = eval.evaluate(finalBoard, finalHands)

        if valueOfHand < max:
            max = valueOfHand
            handWinner = []
            handWinner.append(p)
        elif valueOfHand == max:
            handWinner.append(p)

        print(eval.evaluate(finalBoard, finalHands))
        finalHands = []

    pot[whichServer] /= len(handWinner)
    for winners in handWinner:
        players[whichServer][winners] += pot[whichServer]
        await bot.send_message(pokerChannel[whichServer], winners.display_name + " won the round! They won "+ str(pot[whichServer]) +"$. Use command startPoker to start another one!")
    firstRound[whichServer] = 0
    pot[whichServer] = 0
    isRound[whichServer] = 0

async def showHand(player,printedHand):
    handString = ''
    for printedLine in printedHand:
        handString += printedLine + '\n'
    await bot.send_message(player, handString)

async def showHands(whichServer):
    global hands
    global pokerChannel
    for player in table[whichServer]:
        printedHand = printHand(hands[whichServer][player])
        handString = str(player.display_name) + "'s hand\n"
        for printedLine in printedHand:
            handString += printedLine + '\n'
        await bot.send_message(pokerChannel[whichServer], handString)

async def showboard(printedboard, whichServer):
    boardString = ''
    for printedLine in printedboard:
        boardString += printedLine + '\n'
    await bot.send_message(pokerChannel[whichServer], "*This is the board*\n" + boardString)

async def showTable(whichServer):
    global table
    global playerTurn
    scoreboard = 'Table\n'
    for player in table[whichServer]:
        if table[whichServer][playerTurn[whichServer]] == player:
            scoreboard += '* '
        else:
            scoreboard += '  '
        scoreboard += player.display_name + ' '
        scoreboard += str(players[whichServer][player]) + '$\n'
    await bot.send_message(pokerChannel[whichServer], scoreboard)

async def setupPoker(whichServer):
    global table
    global playerAmount
    global pokerChannel
    for player in table[whichServer]:
        playerAmount[whichServer][player] = 0
    random.shuffle(table[whichServer])
    blindNotSet = 1
    while(blindNotSet):
        if players[whichServer][table[whichServer][bigBlindPos[whichServer]]] < bigBlind[whichServer]:
            players[whichServer].pop(table[whichServer][bigBlindPos[whichServer]], None)
            removedPlayer = table[whichServer].pop(bigBlindPos[whichServer])
        else:
            blindNotSet = 0
    await bot.send_message(pokerChannel[whichServer], "Big blind is " + table[whichServer][bigBlindPos[whichServer]].display_name)
    await bot.send_message(pokerChannel[whichServer], "Small blind is " + table[whichServer][smallBlindPos[whichServer]].display_name)
#TODO
async def startNewGame(whichServer):
    global isRound
    isRound[whichServer] = 0
    global nextRound
    nextRound[whichServer] = 0
    global playerAmount
    playerAmount[whichServer] = {}
    global playerTurn
    playerTurn[whichServer] = 0 
    global pot
    pot[whichServer] = 0
    global hands
    global board
    board[whichServer] = []
    global bigBlindPos
    global smallBlindPos
    global isTurnTable
    isTurnTable[whichServer] = 0
    global table
    global players
    global bettingInProgress
    bettingInProgress[whichServer] = 0
    global cardList
    for p,money in players[whichServer].items():
        if p not in table[whichServer]:
            table[whichServer].append(p)
    cardList[whichServer] = [('Hearts', '2'),('Hearts', '3'),('Hearts', '4'),('Hearts', '5'),('Hearts', '6'),
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
    random.shuffle(cardList[whichServer])
    bigBlindPos[whichServer] = (bigBlindPos[whichServer] +1) % (len(table[whichServer]))
    smallBlindPos[whichServer] = (smallBlindPos[whichServer] + 1) % (len(table[whichServer]))
    playerTurn[whichServer] = bigBlindPos[whichServer]
    for player in hands[whichServer]:
        hands[whichServer][player] = []

async def showMoney(player, moneyRemaining, bettingAmount, whichServer):
    global pot
    await bot.send_message(pokerChannel[whichServer], player.display_name + "'s money: " + str(players[whichServer][player]) + " betting amount: " + str(playerAmount[whichServer][player]) + "\nPot is at " + str(pot[whichServer]))

async def playPokerRound(roundNumber, whichServer):
    global bigBlind
    global smallBlind
    global table
    global playerAmount
    global bettingInProgress
    global pot
    global nextRound
    nextRound[whichServer] = 0
    if roundNumber == 0:
        players[whichServer][table[whichServer][bigBlindPos[whichServer]]] -= bigBlind[whichServer]
        playerAmount[whichServer][table[whichServer][bigBlindPos[whichServer]]] = bigBlind[whichServer]
        pot[whichServer] += bigBlind[whichServer]
        players[whichServer][table[whichServer][smallBlindPos[whichServer]]] -= smallBlind[whichServer]
        playerAmount[whichServer][table[whichServer][smallBlindPos[whichServer]]] = smallBlind[whichServer]
        pot[whichServer] += smallBlind[whichServer]
        await showMoney(table[whichServer][bigBlindPos[whichServer]], players[whichServer][table[whichServer][bigBlindPos[whichServer]]], playerAmount[whichServer][table[whichServer][bigBlindPos[whichServer]]], whichServer)
        bettingInProgress[whichServer] = 1
        await deal(1, whichServer)
        await deal(0, whichServer)
        await showTable(whichServer)
    elif roundNumber == 1:
        bettingInProgress[whichServer] = 1
        await flip(1, whichServer)
        await flip(1, whichServer)
        await flip(0, whichServer)
        await showTable(whichServer)
    elif roundNumber == 2:
        bettingInProgress[whichServer] = 1
        await flip(0, whichServer)
        await showTable(whichServer)
    elif roundNumber == 3:
        bettingInProgress[whichServer] = 1
        await flip(0, whichServer)
        await showTable(whichServer)
    elif roundNumber == 4:
        await evaluateHand(whichServer)
        bettingInProgress[whichServer] = 0

async def deal(isFirstCard, whichServer):
    global cardList
    global table
    for player in table[whichServer]:
        hands[whichServer][player].append(cardList[whichServer].pop(0))
        printedHand = printHand(hands[whichServer][player])
        if not isFirstCard:
            await showHand(player,printedHand)

async def flip(isTwoFirstCard, whichServer):
    global cardList
    cardFlipped = cardList[whichServer].pop(0)
    board[whichServer].append(cardFlipped)
    printedboard = printHand(board[whichServer])
    if not isTwoFirstCard:
        await showboard(printedboard, whichServer)

async def playNextRound(whichServer):
    global nextRound, board, table
    if nextRound[whichServer] == 1:
        if len(table[whichServer]) > 1:
            if len(board[whichServer]) < 3:
                await playPokerRound(1, whichServer)
            elif len(board[whichServer]) < 4:
                await playPokerRound(2, whichServer)
            elif len(board[whichServer]) < 5:
                await playPokerRound(3, whichServer)
            elif len(board[whichServer]) == 5:
                await playPokerRound(4, whichServer)
        else:
            if len(board[whichServer]) < 3:
                await playPokerRound(1, whichServer)
            if len(board[whichServer]) < 4:
                await playPokerRound(2, whichServer)
            if len(board[whichServer]) < 5:
                await playPokerRound(3, whichServer)
            if len(board[whichServer]) == 5:
                await playPokerRound(4, whichServer)

@bot.event
async def on_ready():
    global servers, isGame, isRound, nextRound, firstRound, voteInProgress, voteMessage, voted, emojis, bettingInProgress, playerTurn, players, tabe, playerAmount, hands, board, pokerRole, pokerChannel, bigBlind, bigBlindPos, smallBlind, smallBlindPos, result, pot, bettingRoundAMount, isTurnTable
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    for server in bot.servers:
        servers.append(server)
        isGame.append(0)
        isRound.append(0)
        nextRound.append(0)
        firstRound.append(1)
        voteInProgress.append(0)
        voteMessage.append(None)
        voted.append([])
        emojis.append([])
        bettingInProgress.append(0)
        playerTurn.append(0)
        players.append({})
        table.append([])
        playerAmount.append({})
        hands.append(defaultdict(list))
        board.append([])
        pokerRole.append(None)
        pokerChannel.append(None)
        bigBlind.append(0)
        bigBlindPos.append(0)
        smallBlind.append(0)
        smallBlindPos.append(1)
        result.append(0)
        pot.append(0)
        bettingRoundAMount.append(0)
        isTurnTable.append(0)
        cardList.append([('Hearts', '2'),('Hearts', '3'),('Hearts', '4'),('Hearts', '5'),('Hearts', '6'),
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
            ('Clubs', 'Queen'),('Clubs', 'King'),('Clubs', 'Ace')])

@bot.event
async def on_reaction_add(reaction, user):
    global voteInProgress, servers, voted, voteMessage, emojis, bigBlind, smallBlind, result, players
    whichServer = None
    for i, server in enumerate(servers):
        if reaction.message.server == server:
            whichServer = i
    if voteInProgress[whichServer] and reaction.message.id == voteMessage.id and user.id not in voted[whichServer] and user != bot.user and (reaction.emoji == u"\U0001F44D" or reaction.emoji == u"\U0001F44E"):
        if len(voted[whichServer]) < len(players[whichServer])-1:
            emojis[whichServer].append(reaction.emoji)
            voted[whichServer].append(user.id)
        else:
            emojis[whichServer].append(reaction.emoji)
            result = emojis[whichServer].count(u"\U0001F44D")-emojis[whichServer].count(u"\U0001F44E")
            #await bot.send_message(reaction.message.channel, "Vote results: " + str(results))
            voteInProgress[whichServer] = 0
            if result > 0:
                await bot.send_message(voteMessage.channel, 'Big blind has been set to ' + str(bigBlind[whichServer]) + ' and small blind has been set to ' + str(smallBlind[whichServer]) + '.')
            else:
                await bot.send_message(voteMessage.channel, 'Vote has failed')
                bigBlind[whichServer] = 0
                smallBlind[whichServer] = 0

@bot.event
async def on_server_join(server):
    global servers
    servers.append(server)
    isGame.append(0)
    isRound.append(0)
    nextRound.append(0)
    firstRound.append(1)
    voteInProgress.append(0)
    voteMessage.append(None)
    voted.append([])
    emojis.append([])
    bettingInProgress.append(0)
    playerTurn.append(0)
    players.append({})
    table.append([])
    playerAmount.append({})
    hands.append(defaultdict(list))
    board.append([])
    pokerRole.append(None)
    pokerChannel.append(None)
    bigBlind.append(0)
    bigBlindPos.append(0)
    smallBlind.append(0)
    smallBlindPos.append(1)
    result.append(0)
    pot.append(0)
    bettingRoundAMount.append(0)
    isTurnTable.append(0)
    cardList.append([('Hearts', '2'),('Hearts', '3'),('Hearts', '4'),('Hearts', '5'),('Hearts', '6'),
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
            ('Clubs', 'Queen'),('Clubs', 'King'),('Clubs', 'Ace')])

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
    whichServer = None
    for i, server in enumerate(servers):
        if message.server == server:
            whichServer = i
    if message.author.id != bot.user.id:
        if message.content[0] == command_prefix:
            command = message.content[1:]

            if command == 'playPoker':
                if isGame[whichServer]:
                    await bot.send_message(message.channel,'Games already being played. Game can be restarted with command restart.')
                else:
                    isGame[whichServer] = 1
                    chnnlFlag = 0
                    for chnnl in message.server.channels:
                        if chnnl.name == 'pokerchannel':
                            chnnlFlag = 1
                            pokerChannel[whichServer] = chnnl
                    if chnnlFlag == 0:
                        pokerChannel[whichServer] = await bot.create_channel(message.server, 'pokerchannel')
                    #pokerRole = await bot.create_role(message.server)
                    #await bot.edit_role(message.server, pokerRole, name = 'pokerPlayer')
                    #pokerPlayerPerms = discord.PermissionOverwrite(read_messages=False)
                    #everyoneElsePerms = discord.PermissionOverwrite(read_messages=True)
                    #pokerPlayers = discord.ChannelPermissions(target=pokerRole, overwrite=pokerPlayerPerms)
                    #everyoneElse = discord.ChannelPermissions(target=message.server.default_role, overwrite=everyoneElsePerms)
                    await bot.send_message(pokerChannel[whichServer],'Game is about to start, use command join to join the fun!')

            if command == 'stopPoker':
                if isGame[whichServer]:
                    isGame[whichServer] = 0
                    isRound[whichServer] = 0
                    bettingInProgress[whichServer] = 0
                    voteInProgress[whichServer] = 0
                    #await bot.delete_channel(pokerChannel)
                    #await bot.delete_role(message.server, pokerRole)
                    await bot.send_message(message.channel, "Game has been stopped.")
                else:
                    await bot.send_message(message.channel, "No game in progress.")

            if command == 'join':
                if isGame[whichServer]:
                    if not message.author in players[whichServer]:
                        if not isRound[whichServer]:
                            players[whichServer][message.author] = 3000
                            table[whichServer].append(message.author)
                            #await bot.add_roles(message.author, pokerRole)
                            await bot.send_message(message.channel,'You have been added to the game!')
                        else:
                            players[whichServer][message.author] = 3000
                            await bot.send_message(message.channel,'You have been added to the queue, you will be included in the next game')
                    else:
                        await bot.send_message(message.channel,'You are already in the list of players. Wait for a new game to start.')
                else:
                    await bot.send_message(message.channel,'Game has not been initiated yet, use command playPoker to start.')

            if command == 'startPoker':
                if isGame[whichServer]:
                    if not isRound[whichServer]:
                        if len(players[whichServer]) > 1:
                            
                            if firstRound[whichServer]:
                                random.shuffle(cardList[whichServer])
                                await setupPoker(whichServer)
                            else:
                                await startNewGame(whichServer)
                            isRound[whichServer] = 1
                            await playPokerRound(0, whichServer)
                        else:
                            await bot.send_message(message.channel, 'Not enough players in the lobby.' + '\n' +
                                                                    'Use the command viewPlayers to see the lobby.' + '\n' +
                                                                    'Use the command join to add yourself to the lobby.')
                    else:
                        await bot.send_message(message.channel,'Round already in progress.')
                else:
                    await bot.send_message(message.channel, 'Game has not been initiated yet.')

            if command == 'viewPlayers':
                if isGame[whichServer]:
                    sendPlayers = ''
                    for player,money in players[whichServer].items():
                        sendPlayers = sendPlayers + player.display_name + ' ' + str(money) + '\n'
                    await bot.send_message(message.channel,sendPlayers)
                else:
                    await bot.send_message(message.channel,'Game has not been started, use command playPoker to start.')

            #if command == 'nextRound': #TODO make it so that you dont have to type nextRound
                '''if nextRound[whichServer] == 1:
                    if len(board[whichServer]) < 3:
                        await playPokerRound(1, whichServer)
                    elif len(board[whichServer]) < 4:
                        await playPokerRound(2, whichServer)
                    elif len(board[whichServer]) < 5:
                        await playPokerRound(3, whichServer)
                    elif len(board[whichServer]) == 5:
                        await playPokerRound(4, whichServer)
'''
            if re.search(r'setBlind [0-9]+$',command):
                if isGame[whichServer]:
                    if not voteInProgress[whichServer]:
                        bigBlind[whichServer] = int(re.search(r'\d+$',command).group())
                        smallBlind[whichServer] = math.floor(bigBlind[whichServer]/2)
                        voteInProgress[whichServer] = 1
                        voted[whichServer] = []
                        emojis[whichServer] = []
                        voteMessage = await bot.send_message(message.channel, "Set blind to " + str(bigBlind[whichServer]) + "?")
                        await bot.add_reaction(voteMessage, u"\U0001F44D")
                        await bot.add_reaction(voteMessage, u"\U0001F44E")
                    else:
                        await bot.send_message(message.channel, 'A vote is already in progress')

            #Commands that work when betting is in progress
            if re.search(r'raise [0-9]+$',command):
                if bettingInProgress[whichServer]:
                    if message.author == table[whichServer][playerTurn[whichServer]]:
                        raisedAmount = int(re.search(r'\d+$',command).group())
                        if raisedAmount <= players[whichServer][message.author]:
                            if raisedAmount + playerAmount[whichServer][message.author] > max(playerAmount[whichServer].values()):
                                players[whichServer][message.author] -= raisedAmount
                                playerAmount[whichServer][message.author] += raisedAmount
                                pot[whichServer] += raisedAmount
                                if ((playerTurn[whichServer] + 1) % (len(table[whichServer]))) == bigBlindPos[whichServer]:
                                    isTurnTable[whichServer] = 1
                                await showMoney(table[whichServer][playerTurn[whichServer]], players[whichServer][table[whichServer][playerTurn[whichServer]]], playerAmount[whichServer][table[whichServer][playerTurn[whichServer]]], whichServer)
                                if all( value == max(playerAmount[whichServer].values()) for value in playerAmount[whichServer].values()) and isTurnTable[whichServer]:
                                    bettingInProgress[whichServer] = 0
                                    nextRound[whichServer] = 1
                                    playerTurn[whichServer] = bigBlindPos[whichServer]
                                    isTurnTable[whichServer] = 0
                                    await bot.send_message(message.channel, 'Round is over, next one starting now.')
                                    await playNextRound(whichServer)
                                else:
                                    playerTurn[whichServer] = (playerTurn[whichServer] + 1) % (len(table[whichServer]))
                                    await bot.send_message(message.channel, message.author.display_name + ' has raised.')
                                    await bot.send_message(message.channel, "It's now " + table[whichServer][playerTurn[whichServer]].display_name + "'s turn.")
                            else:
                                await bot.send_message(message.channel, 'Not a raise')
                        else:
                            await bot.send_message(message.channel, 'Your too poor for that')
                    else:
                        await bot.send_message(message.channel, "Wait for your turn. Jeez.") 

            if command == 'check':
                if bettingInProgress[whichServer]:
                    if message.author == table[whichServer][playerTurn[whichServer]]:
                        if playerAmount[whichServer][message.author] == max(playerAmount[whichServer].values()):
                            if ((playerTurn[whichServer] + 1) % (len(table[whichServer]))) == bigBlindPos[whichServer]:
                                isTurnTable[whichServer] = 1
                            await showMoney(table[whichServer][playerTurn[whichServer]], players[whichServer][table[whichServer][playerTurn[whichServer]]], playerAmount[whichServer][table[whichServer][playerTurn[whichServer]]], whichServer)
                            if all( value == max(playerAmount[whichServer].values()) for value in playerAmount[whichServer].values()) and isTurnTable[whichServer]:
                                bettingInProgress[whichServer] = 0
                                nextRound[whichServer] = 1
                                playerTurn[whichServer] = bigBlindPos[whichServer]
                                isTurnTable[whichServer] = 0
                                await bot.send_message(message.channel, 'Round is over, next one starting now.')
                                await playNextRound(whichServer)
                            else:
                                playerTurn[whichServer] = (playerTurn[whichServer] + 1) % (len(table[whichServer]))
                                await bot.send_message(message.channel, message.author.display_name + ' has checked.')
                                await bot.send_message(message.channel, "It's now " + table[whichServer][playerTurn[whichServer]].display_name + "'s turn.")
                        else:
                            await bot.send_message(message.channel, "You can't check dummy. Learn how to play the game!")
                    else:
                        await bot.send_message(message.channel, "Wait for your turn. Jeez.")

            if command == 'call':
                if bettingInProgress[whichServer]:
                    if message.author == table[whichServer][playerTurn[whichServer]]:
                        raisedAmount = max(playerAmount[whichServer].values()) - playerAmount[whichServer][message.author]
                        if raisedAmount <= players[whichServer][message.author]:
                            players[whichServer][message.author] -= raisedAmount
                            playerAmount[whichServer][message.author] += raisedAmount
                            pot[whichServer] += raisedAmount
                            if ((playerTurn[whichServer] + 1) % (len(table[whichServer]))) == bigBlindPos[whichServer]:
                                isTurnTable[whichServer] = 1
                            await showMoney(table[whichServer][playerTurn[whichServer]], players[whichServer][table[whichServer][playerTurn[whichServer]]], playerAmount[whichServer][table[whichServer][playerTurn[whichServer]]], whichServer)
                            if all( value == max(playerAmount[whichServer].values()) for value in playerAmount[whichServer].values()) and isTurnTable[whichServer]:
                                bettingInProgress[whichServer] = 0
                                nextRound[whichServer] = 1
                                playerTurn[whichServer] = bigBlindPos[whichServer]
                                isTurnTable[whichServer] = 0
                                await bot.send_message(message.channel, 'Round is over, next one starting now.')
                                await playNextRound(whichServer)
                            else:
                                playerTurn[whichServer] = (playerTurn[whichServer] + 1) % (len(table[whichServer]))
                                await bot.send_message(message.channel, message.author.display_name + ' has called.')
                                await bot.send_message(message.channel, "It's now " + table[whichServer][playerTurn[whichServer]].display_name + "'s turn.")
                        else:
                            await bot.send_message(message.channel, 'Your too poor for that')               
                    else:
                        await bot.send_message(message.channel, "Wait for your turn. Jeez.")

            if command == 'fold':#TODO cehck if only one person table
                if bettingInProgress[whichServer]:
                    if message.author == table[whichServer][playerTurn[whichServer]]:
                        name = table[whichServer][playerTurn[whichServer]].display_name
                        del hands[whichServer][table[whichServer][playerTurn[whichServer]]]
                        del table[whichServer][playerTurn[whichServer]]
                        if ((playerTurn[whichServer] + 1) % (len(table[whichServer]))) == bigBlindPos[whichServer]:
                            isTurnTable[whichServer] = 1
                        if all( value == max(playerAmount[whichServer].values()) for value in playerAmount[whichServer].values()) and isTurnTable:
                            bettingInProgress[whichServer] = 0
                            nextRound[whichServer] = 1
                            playerTurn[whichServer] = bigBlindPos[whichServer]
                            isTurnTable[whichServer] = 0
                            await bot.send_message(message.channel, name + ' has been removed from the table. Next round will start.')
                            await playNextRound(whichServer)
                        else:
                            playerTurn[whichServer] = (playerTurn[whichServer] + 1) % (len(table[whichServer]))
                            await bot.send_message(message.channel, name + " has been removed from the table\nIt's now " + table[whichServer][playerTurn[whichServer]].display_name + "'s turn.")
                    else:
                        await bot.send_message(message.channel, "Wait for your turn. Jeez.")

bot.run(token)
