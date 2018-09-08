# Python 3
import sys
import csv
import argparse
#====
names = [] # where we store the names of all the players
#====
def getLastName(full_name):
    last_name = ""
    for i in full_name:
        if (i == "_" and last_name != "de" and last_name != "van" and last_name != "al"): # != intends to fix pre-fix issue
            break
        else:
            last_name += i
    return last_name

def checkForAlternate(full_name):
    last_name = getLastName(full_name)
    for name in names:
        if last_name == name[:len(last_name)]:
            if name[-2] == full_name[-2]:
                return name
    names.append(full_name)
    return False

def formatName(name):
    name = name.replace(" ", "_")
    if (name[len(name)-1] == "_"):
        name = name[:len(name)-1]
    name = name.lower()
    return name

def genNameList():
    print('''
    =====
    Generating name list...''')
    for date in range(2000, 2019):
        with open('data/' + str(date) + '.csv') as csvfile:
            csv_in = csv.reader(csvfile, delimiter=',')
            flag = False
            for row in csv_in:
                if (flag):
                    name1 = row[9]
                    name2 = row[10]
                    # clean name format
                    name1 = formatName(name1)
                    name2 = formatName(name2)
                    # check if alternative name format already exists
                    name1_alt = checkForAlternate(name1)
                    name2_alt = checkForAlternate(name2)
                    # make swap if alternate is found
                    if (name1_alt):
                        name1 = name1_alt
                    if (name2_alt):
                        name2 = name2_alt
                    # save names if not in names[]
                    if name1 not in names:
                        names.append(name1)
                    if name2 not in names:
                        names.append(name2)
                flag = True

'''
by default (when incl_odds is not specified) generates output in form ready
for spring rank algorithm. When incl_odds IS specified, generates output in
form: winner, loser, winner_odds, loser_odds\n'''
def genMatchHistory(young_date, old_date, incl_odds, incl_surface, output):
    print('''
    =====
    Generating match history...''')
    for date in range(young_date, old_date):
        with open('data/' + str(date) + '.csv') as csvfile:
            csv_in = csv.reader(csvfile, delimiter=',')
            flag = False
            for row in csv_in:
                if (flag):
                    winner = row[9]
                    loser = row[10]
                    # odds represent the average of all bookmakers included
                    if (incl_odds):
                        winner_odds = row[38]
                        loser_odds = row[39]
                    winner = formatName(winner)
                    loser = formatName(loser)
                    winner_alt = checkForAlternate(winner)
                    loser_alt = checkForAlternate(loser)
                    if (winner_alt):
                        winner = winner_alt
                    if (loser_alt):
                        loser = loser_alt
                    #incorporate surface played on
                    if (incl_surface):
                        winner += "_"+row[6].lower()
                        loser += "_"+row[6].lower()
                    out = str(winner + " " + loser + " " + "1")
                    if (incl_odds):
                        if(winner_odds == " " or loser_odds == " " or winner_odds == "" or loser_odds == ""):
                            continue
                        else:
                            out = str(winner + " " + loser + " " + str(winner_odds) + " " + str(loser_odds))
                            output.write(out)
                            output.write('\n')
                    else:
                        output.write(out)
                        output.write('\n')
                flag = True

# gets user arguments
parser = argparse.ArgumentParser()
parser.add_argument("--surface", action="store_true")
parser.add_argument("--odds", action="store_true")
parser.add_argument("years", nargs='+')

args = parser.parse_args()

if (args.surface and args.odds):
    output = open(args.years[0] + '-' + args.years[1] + '_output_odds_surface.dat', 'w')
elif (args.surface):
    output = open(args.years[0] + '-' + args.years[1] + '_output_Nodds_surface.dat', 'w')
elif (args.odds):
    output = open(args.years[0] + '-' + args.years[1] + '_output_odds_Nsurface.dat', 'w')
else:
    output = open(args.years[0] + '-' + args.years[1] + '_output_Nodds_Nsurface.dat', 'w')

genNameList()

genMatchHistory(int(args.years[0]), int(args.years[1]), args.odds, args.surface, output)

output.close()
