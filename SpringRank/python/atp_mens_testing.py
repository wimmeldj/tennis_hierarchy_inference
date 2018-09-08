# Python 3
import csv
import sys
import math
from matplotlib import pyplot as plt
from matplotlib import style
import sRank_gen
import copy
import statistics as stat
import os
import pickle
import argparse

style.use('grayscale')

# global vars
players = [] # where names of players are stored until new sRank is generated
matches = []
winners = []
losers = []
winner_odds = []
loser_odds = []
# stores the players where sRank was "right" i.e. the sRank of the winner was > the loser's sRank
winner_right = []

x = [0,]
counter = 1
# used to store the divergences in the real probabilities and inferred probabilities of each player
win_div = []
loss_div = []

win_game_count = []
loss_game_count = []
#=======
bank = 1000000
principal = copy.deepcopy(bank)
y = [copy.deepcopy(bank),]
plt.plot(x, bank)

# returns the SpringRank of player based on the sRank.dat file
def lookUpSpringRank(player, path = os.getcwd() + "/../data/sRank.dat"):
    with open(path) as csvfile:
        inFile = csv.reader(csvfile, delimiter=' ')
        for row in inFile:
            if (row[0] == player):
                return float(row[1])
        # if no spring_rank is found we return 0 because player has no interactions
        return 0

# function could potentially be used as a filter to only bet on matches between
# players that have has some number of interactions
def getNumberOfInteraction(player_i, player_j):
    count = 0
    with open(os.getcwd() + "/../data/historical_matches.dat") as csvfile:
        inFile = csv.reader(csvfile, delimiter=' ')
        for row in inFile:
            if (row[0] == player_i and row[1] == player_j):
                count += 1
    return count

# expects the sRank of i and j and the level of noise
def edgeDirectionProbability(i, j, beta = 1.077):
    return 1 / (1 + math.exp(-2*beta*(i-j)))

# basic kelly criterion returns percentage of bank that should be bet
def kelly(odds, p):
    b = odds - 1
    frac = (b * p - (1-p)) / b
    if (args.verbose):
        print("k:",frac)
    return (frac * .25) # quarter kelly

#===Begin===============

# for suppressing all console output other than the final results
parser = argparse.ArgumentParser()
parser.add_argument("--verbose", action="store_true")
parser.add_argument("year", nargs='+')

args = parser.parse_args()

# reads unplayed_matches.dat (the data that we are testing our bettting method on)
# into the lists: matches, winners, losers, winner_odds, loser_odds
with open(os.getcwd() + "/../data/unplayed_matches.dat") as csvfile:
    inFile = csv.reader(csvfile, delimiter=' ')
    for row in inFile:
        matches.append(row)
        winners.append(row[0])
        losers.append(row[1])
        winner_odds.append(row[2])
        loser_odds.append(row[3])

# generate first sRank from historical data
sRank_gen.generate()

count = 1
for match in matches[:]:
    # just a simple console read out if you're bored and want to watch
    if (args.verbose):
        if (count % 100 == 0):
            print("MATCH:", count)
        print(count)
        if (count % 10 == 0):
            print("BANK:", bank)

    # the winner and loser of the current match will be at the top of their respective lists
    winner = winners[0]
    loser = losers[0]

    # check if need to re-calc sRank (we don't unless some player played after
    # last sRank calculation)
    if winner in players or loser in players:
        if (args.verbose):
            print("<<Re-Calculating SprintRank>>")
        players = [] # reset players[]
        sRank_gen.generate() # re-calc srank
    else:
        players.append(winner)
        players.append(loser)

    #look up prediction from spring rank hierarchy
    winner_rank = lookUpSpringRank(winner)
    loser_rank = lookUpSpringRank(loser)

    if winner_rank > loser_rank:
        winner_right.append(winner)

    # the inferred probabilities based on bookmaker average odds
    inf_w = (1/float(winner_odds[0]))
    inf_l = (1/float(loser_odds[0]))

    # our "real" probabilities
    p1 = edgeDirectionProbability(winner_rank, loser_rank)
    p2 = edgeDirectionProbability(loser_rank, winner_rank)

    # percentage of bankroll to bet given the inferred probabiliteis and our probabilites
    k1 = kelly(float(winner_odds[0]), p1)
    k2 = kelly(float(loser_odds[0]), p2)

    # the number of games in which the current players have played each other
    num_games = getNumberOfInteraction(winner, loser) + getNumberOfInteraction(loser, winner)

    # if the percentage of our bankroll to bet is positive and our real probability
    # is .45 greater than the inferred probability
    if (k1 > 0 and p1 > inf_w + .45):
        win_div.append(p1-inf_w)
        win_game_count.append(getNumberOfInteraction(winner,loser) + getNumberOfInteraction(loser, winner))

        # if recommended bet amount < $1
        if (k1*bank < 1):
            continue # we don't bet anything

        else:
            # we win k1 * winner_odds * bank
            if (args.verbose):
                print("===WIN", "bet:", bank*k1, "on", winner, "in", match)
                print("Odds:", inf_w, "rProb:", p1)
                print("Bank:", bank)
            bank = bank + (bank * k1 * (float(winner_odds[0])-1))
        # for plot
        counter += 1
        x.append(copy.deepcopy(counter))
        y.append(copy.deepcopy(bank))

    #same logic as above (if it wasn't, this wouldn't count as a simulation)
    if (k2 > 0 and p2 > inf_l + .45):
        loss_div.append(p2-inf_l)
        loss_game_count.append(getNumberOfInteraction(winner, loser) + getNumberOfInteraction(loser, winner))
        if (k2*bank < 1):
            continue
        else:
            if (args.verbose):
                print("===LOSS", "bet:", bank*k2, "on", loser, "in", match)
                print("Odds:", inf_l, "rProb:", p2)
                print("Bank:", bank)
            bank = bank - (bank * k2) # we only spent k2 of our bank
        counter += 1
        x.append(copy.deepcopy(counter))
        y.append(copy.deepcopy(bank))

    count += 1

    # incorporate current match results into historical matches so that we can
    # re-calc sRank
    with open(os.getcwd() + "/../data/historical_matches.dat", 'a') as oFile:
        oFile.write(winner + " " + loser + " 1" + "\n")
    # pop top of each list because match is over
    del(winners[0])
    del(losers[0])
    del(winner_odds[0])
    del(loser_odds[0])

    # we can pretty safely say that if our bankroll is a thousandth of its original
    # amount, we have bust
    if (bank < principal/1000):
        avg_win_div = 0
        avg_loss_div = 0
        avg_win_game_count = 0
        avg_loss_game_count = 0
        for i in win_div:
            avg_win_div += i
        for i in loss_div:
            avg_loss_div += i
        for i in win_game_count:
            avg_win_game_count += i
        for i in loss_game_count:
            avg_loss_game_count += i
        avg_win_div = avg_win_div / len(win_div)
        avg_loss_div = avg_loss_div / len(loss_div)
        avg_win_game_count = avg_win_game_count / len(win_game_count)
        avg_loss_game_count = avg_loss_game_count / len(loss_game_count)
        print("FINAL BAL:", bank)
        print("avg win gc:", avg_win_game_count)
        print("avg los gc:", avg_loss_game_count)
        print("med win gc:", stat.median(win_game_count))
        print("med los gc:", stat.median(loss_game_count))
        print("avg win div:", avg_win_div)
        print("avg los div:", avg_loss_div)
        print("winners correct:", len(winner_right), "/", count, "=", len(winner_right)/count)
        print("Principal:", principal)
        print("Halting! Bankroll is less than a thousandth of its original value.")

        with open(os.getcwd() + '/../data/results/' + args.year[0] + '/' + 'outX', 'wb') as fp:
            pickle.dump(x, fp)
        with open(os.getcwd() + '/../data/results/' + args.year[0] + '/' + 'outY', 'wb') as fp:
            pickle.dump(y, fp)

        plt.plot(x,y)
        plt.show()
        raise ValueError("Out of money")


sRank_gen.generate()
avg_win_div = 0
avg_loss_div = 0
avg_win_game_count = 0
avg_loss_game_count = 0
for i in win_div:
    avg_win_div += i
for i in loss_div:
    avg_loss_div += i
for i in win_game_count:
    avg_win_game_count += i
for i in loss_game_count:
    avg_loss_game_count += i
avg_win_div = avg_win_div / len(win_div)
avg_loss_div = avg_loss_div / len(loss_div)
avg_win_game_count = avg_win_game_count / len(win_game_count)
avg_loss_game_count = avg_loss_game_count / len(loss_game_count)
print("FINAL BAL:", bank)
print("avg win div:", avg_win_div)
print("avg los div:", avg_loss_div)
print("avg win gc:", avg_win_game_count)
print("avg los gc:", avg_loss_game_count)
print("med win gc:", stat.median(win_game_count))
print("med los gc:", stat.median(loss_game_count))
print("winners correct:", len(winner_right), "/", count, "=", len(winner_right)/count)
print("Principal:", principal)

with open(os.getcwd() + '/../data/results/' + args.year[0] + '/' + 'outX', 'wb') as fp:
    pickle.dump(x, fp)
with open(os.getcwd() + '/../data/results/' + args.year[0] + '/' + 'outY', 'wb') as fp:
    pickle.dump(y, fp)

plt.plot(x,y)
plt.show()
