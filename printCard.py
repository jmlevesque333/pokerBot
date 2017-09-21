import sys

def printCard(suit, rank):
    print(suit)
    print(rank)
    suits_names = ['Spades', 'Diamonds', 'Hearts', 'Clubs']
    suits_symbols = ['♠', '♦', '♥', '♣']

    lines = [[] for i in range(9)]

    if rank =='10':
        space = ''
    else:
        space = ' '
        rank = rank[0]

    suit = suits_names.index(suit)
    suit = suits_symbols[suit]

    lines[0] = '┌─────────┐'.encode('utf-8')
    lines[1] = '│{}{}       │'.format(rank, space).encode('utf-8')
    lines[2] = '│         │'.encode('utf-8')
    lines[3] = '│         │'.encode('utf-8')
    lines[4] = '│    {}    │'.format(suit).encode('utf-8')
    lines[5] = '│         │'.encode('utf-8')
    lines[6] = '│         │'.encode('utf-8')
    lines[7] = '│       {}{}│'.format(space, rank).encode('utf-8')
    lines[8] = '└─────────┘'.encode('utf-8')

    #for i in lines:
    #    sys.stdout.buffer.write(i)
    #    print()
    
    return lines

def printHand(hand):
   
    newHand = [[] for i in range(9)]

    printedCards = [[] for i in range(len(hand))]
    index = 0
    for cards in hand:
        printedCards[index] = printCard(cards[0],cards[1])
        index += 1


    for i in range(9):
        for j in range(len(printedCards)):
            if j == 0:
                newHand[i] = printedCards[j][i]
            else:
                newHand[i] = newHand[i] + printedCards[j][i]


    for i in range(9):
        sys.stdout.buffer.write(newHand[i])
        print()

    


printHand((('Hearts', '7'),('Clubs', 'King'), ('Spades', 'Queen'), ('Hearts', '8')))
