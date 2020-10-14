# How to win a fun family game
"Pass the Pigs" is a fun family game of chance that involves rolling pig-shaped dice to try to score more points than your opponents. It is an exciting game, in which players have do decide when to risk it all and make their move to seal victory. Here, I explain the probability concepts underlying "Pass the Pigs" and then leverage them to develop a winning strategy. 

#### Data source and structure
All scoring and rules information comes from the "Pass the Pigs" instruction booklet. I collected the raw data on pig landing orientation probabilities, and compiled them in the Excel file "pig_outcomes_per_roll.xlsx". Each row of this file corresponds to a single roll of both pigs. The columns record the positions of each pig:
The column labels in the Excel file are as follows:
+ round
+ spot_side_up
+ spot_side_down
+ trotter
+ razorback
+ snouter
+ leaning_jowler
+ oinker
+ piggy_back

#### Scripts: data analysis and visualization
1) `passing_pigs.py`
uses the rules of "Pass the Pigs" to...
+ calculate the probability of landing each combination of pig orientations
+ calculate the expected score from a single roll
	- with and without factoring in a "pig out"
+ implement two potential winning strategies
	- the first involves rolling a set number of times each turn
	- the second involves rolling until a threshold score on each turn
+ simulate games to evaluate the effectiveness of each strategy
+ plot the number of points a player can expect to score on consecutive rolls without pigging out
+ plot the probability of not pigging out for consecutive rolls
+ plot the expected score from a given number of consecutive rolls
	- takes into account the probability of pigging out
+ plot the expected score from rolling one more time given a current score
	- takes into account the probability of pigging out
+ plot a comparison of the two winning strategies
	- histogram of the number of turns required to win after several thousand simulations

#### Results summary
A full description of the results of these analyses is presented in the *report.pdf* file.