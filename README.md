# tennis_hierarchy_inference
We use the [SpringRank algorithm](https://arxiv.org/abs/1709.09002) to infer
hierarchies in ATP Men's tennis tournament data. Using the SpringRank rankings,
we can infer the "real" probability of one player beating some other player.
If the implied probability of the money-line odds being offered for a particular
match differ significantly from our real probabilities, it would make sense to
lay a bet on the "undervalued" player (assuming our generated rankings are
accurate).

Our program (atp_mens_testing.py in SpringRank/python dir) expects a set of
historical data from which it can infer a SpringRank hierarchy. It also expects
a test set of data. This could be a future match(es)
in the form of an adjacency matrix:

player_i player_j 1
player_i2 player_j2 1
.
.
.

Tests of our program were run where the set of historical data was all ATP
Men's Tennis Data from the year 2000 to the year being tested (exclusive) and
the set of test data was the ATP Men's Tennis tournament results for the year
being tested.

The data processing tool get_data.py in the tennis_prep dir was used to process
the raw data into an adjacency matrix. It can be run like so:

python3 get_data.py [startYear] [endYear(exclusive)]

and with the optional arguments:

--surface | to include the type of surface played on in adjacency matrix
--odds    | to include the odds in the output data (only useful for the year being tested)

Our program is currently designed as a "testing environment." So, it decides
whether or not to lay a bet based on a predefined divergence in our SpringRank
calculated odds and the inferred money-line odds. The program has a predefined
bankroll to simulate concrete real world results of using the SpringRank algorithm
to calculate the "real" probabilities of players and sizing bets using the
Kelly Criterion.

A write up of the program and the tests that were run can be found here:

[davidwimmel.com](http://davidwimmel.com/other-works.html)

Alternatively, you can look at the ATP_Mens_Tennis_Prediction.html file in the
root of our project.

I plan on at the very least testing this on different data, like ATP women's
tennis tournament data. I would also like to devise some better way of deciding
whether or not to lay a bet. Currently, we bet if our "real" probability is
.45 greater than the inferred money-line probability. For obvious reasons, this
isn't a great solution. It's static and uncreative.
