################################################################################
#author: JER
#date of last modification: 201012
#summary of last modification: tweaked some of the figures to make them more informative

################################################################################
##### description #####
#this script determines the probability of scoring different points in each roll of the 'pass the pigs' game

################################################################################
##### import packages #####
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

################################################################################
##### decide whether or not to save the figure that this script produces #####
save_figs = False
out_path_figs = '../../figures/exploratory_figures/'

################################################################################
##### set up dictionary with pig orientation probabilities #####
per_pig_per_roll_probs = {}
per_pig_per_roll_probs['spot_side_up'] = 0.240
per_pig_per_roll_probs['spot_side_down'] = 0.365
per_pig_per_roll_probs['trotter'] = 0.058
per_pig_per_roll_probs['razorback'] = 0.320
per_pig_per_roll_probs['snouter'] = 0.017
per_pig_per_roll_probs['leaning_jowler'] = 0.0
#per_pig_per_roll_probs['oinker'] = 0.0
#per_pig_per_roll_probs['piggy_back'] = 0.0
#print(sum(per_pig_per_roll_probs.values()))

P_pig_out = 2*( per_pig_per_roll_probs['spot_side_up'] * per_pig_per_roll_probs['spot_side_down'] ) #probability of 'pigging out' on one roll
P_not_pig_out = 1-P_pig_out #probability of not 'pigging out' on one roll
print('Pig out odds per role = {:0.3f}'.format( P_pig_out ) )

################################################################################
##### set up dictionary with pig orientation scores #####
per_roll_points = {}
per_roll_points['sider'] = 0.25
per_roll_points['pig_out'] = 0.0
per_roll_points['trotter'] = 5.0
per_roll_points['razorback'] = 5.0
per_roll_points['snouter'] = 10.0
per_roll_points['leaning_jowler'] = 15.0
#per_roll_points['oinker'] = 0.0
#per_roll_points['piggy_back'] = 0.0
per_roll_points['combo_multiplier'] = 2.0

################################################################################
##### use pig orientation probabilities and corresponding scores to determine the expected score for a single roll #####
one_roll_expected_score = 0
all_possible_scores_list = []
all_possible_score_probabilities_list = []
for pig_A in per_pig_per_roll_probs:
    if pig_A[0:9] == 'spot_side': #if pig A landed on its side
        pig_A_sider = True
    else:
        pig_A_sider = False

    for pig_B in per_pig_per_roll_probs:
        if pig_B[0:9] == 'spot_side': #if pig B landed on its side
            pig_B_sider = True
        else:
            pig_B_sider = False

        if pig_A_sider and pig_B_sider: #if both pigs landed on their sides
            if pig_A == pig_B: #pigs landed same side up
                roll_points = ( per_roll_points['sider'] + per_roll_points['sider'] ) * per_roll_points['combo_multiplier']
            else: #pigs landed with different sides up
                roll_points = per_roll_points['pig_out']

        elif pig_A_sider or pig_B_sider: #one pig landed on its side but the other did not
            if pig_A_sider: #pig A was on its side, so it contributes 0 points
                roll_points = per_roll_points[pig_B]
            else: #pig B was on its side, so it contributes 0 points
                roll_points = per_roll_points[pig_A]

        else: #neither pig landed on its side
            if pig_A == pig_B:
                roll_points = ( per_roll_points[pig_A] + per_roll_points[pig_B] ) * per_roll_points['combo_multiplier']
            else:
                roll_points = ( per_roll_points[pig_A] + per_roll_points[pig_B] )

        joint_prob = per_pig_per_roll_probs[pig_A] * per_pig_per_roll_probs[pig_B]
        one_roll_expected_score += roll_points * joint_prob
        all_possible_scores_list.append(roll_points)
        all_possible_score_probabilities_list.append(joint_prob)

################################################################################
##### determine the cumulative probabilities of scoring different amounts in a roll, excluding pig out #####
all_possible_scores_array = np.asarray( all_possible_scores_list ) #convert this list to a numpy array
all_possible_score_probabilities_array = np.asarray( all_possible_score_probabilities_list ) #convert this list to a numpy array
all_possible_score_cumulative_probabilities_array = np.cumsum(all_possible_score_probabilities_array)
#print(all_possible_scores_array)
#print(all_possible_score_cumulative_probabilities_array)

################################################################################
##### calculate the expected score for a single roll assuming the roll did not pig out #####
#this number is useful when evaluating rolling strategies
one_roll_expected_score_no_pig_out = one_roll_expected_score/P_not_pig_out

print( 'Expected score from one role (including pig out) = {:0.2f}'.format(one_roll_expected_score) )
print( 'Expected score from one role (assuming no pig out) = {:0.2f}'.format(one_roll_expected_score_no_pig_out) )

n_rolls = np.arange(0, 21)
P_no_pig_out_n_rolls = np.power(P_not_pig_out, n_rolls)
n_rolls_expected_score_no_pig_out = n_rolls * one_roll_expected_score_no_pig_out
#print( P_no_pig_out_n_rolls )

################################################################################
##### strategy 1: how many points can you expect by rolling for a set number of times each turn? #####
def strategy_1_score(num_rolls, expected_score_no_pig_out, prob_no_pig_out_one_roll):
    score = expected_score_no_pig_out * num_rolls * (prob_no_pig_out_one_roll**num_rolls)
    return score

strategy_1_scores_list = np.zeros(len(n_rolls))
i = 0
while i < len(n_rolls):
    strategy_1_scores_list[i] = strategy_1_score(n_rolls[i], one_roll_expected_score_no_pig_out, P_not_pig_out)
    i+=1
#print(strategy_1_scores_list)

strategy_1_target_rolls = P_not_pig_out / P_pig_out
strategy_1_avg_score = strategy_1_target_rolls * one_roll_expected_score_no_pig_out
print( '  strategy 1: stop rolling pigs after {:0.2f} rolls'.format(strategy_1_target_rolls) )
print( '  strategy 1: expect to score {:0.2f} points per turn, on average'.format(strategy_1_avg_score) )

################################################################################
##### strategy 2:  how many points can I expect by rolling until I get to a set score each turn? #####
#there is a lot of variability in the score I could get after one roll, so maybe rolling a set number of times is less ideal than rolling for a set score each time
def strategy_2_score(current_score, expected_score_no_pig_out, prob_no_pig_out_one_roll):
    score = (current_score + expected_score_no_pig_out) * prob_no_pig_out_one_roll
    return score
#print( strategy_2_score(25, one_roll_expected_score_no_pig_out, P_not_pig_out ) )

strategy_2_current_scores_list = np.arange(0, 101) #examples of the current score I could have while considering whether or not to roll again
strategy_2_expected_scores_list = np.zeros(len(strategy_2_current_scores_list))
i = 0
while i < len(strategy_2_current_scores_list):
    strategy_2_expected_scores_list[i] = strategy_2_score(strategy_2_current_scores_list[i], one_roll_expected_score_no_pig_out, P_not_pig_out)
    i+=1
#print(strategy_2_expected_scores_list)

strategy_2_target_score = (one_roll_expected_score_no_pig_out * P_not_pig_out) / P_pig_out
strategy_2_avg_rolls = strategy_2_target_score / one_roll_expected_score_no_pig_out
print( '  strategy 2: stop rolling pigs after obtaining a target score >= {:0.2f} points'.format(strategy_2_target_score) )
print( '  strategy 2: expect to roll {:0.2f} times, on average'.format(strategy_2_avg_rolls) )

################################################################################
##### function that implements strategy 1 for a single game #####
#EDIT THIS STRATEGY SO THAT A TURN STOPS AS SOON AS THE TARGET GAME SCORE IS REACHED?
def strategy_1_game_simulation(target_turn_rolls, target_game_score, compensate_target_rolls_decimal):
    game_score = 0
    total_turns_to_target_game_score = 0
    rolls_per_turn_list = []
    points_per_turn_list = []
    while game_score < target_game_score: #keep taking turns until you get to the target points for a game (usually 100)
        n_rolls_this_turn = 0 #have rolled 0 times so far this turn
        turn_score = 0 #no points yet for this turn
        pigged_out = False #have not pigged out yet this turn
        while (n_rolls_this_turn < target_turn_rolls) and (not pigged_out): #take one turn, which consists of several rolls
            roll_test_val = np.random.random() #generate a random cumulative probability
            roll_score = all_possible_scores_array[all_possible_score_cumulative_probabilities_array > roll_test_val][0] #determine the score for this roll
            if roll_score > 0: #did NOT pig out on this roll
                turn_score += roll_score #add the score from this roll to the total score for this turn
            else: #pigged out on this roll
                turn_score = 0 #lose all points for this turn
                pigged_out = True #no more rolls allowed for this turn
            n_rolls_this_turn+=1 #have rolled one more time now for this turn
        game_score+=turn_score #total game score increases by the score accrued during all of the rolls for each turn
        total_turns_to_target_game_score+=1 #keep track of the number of turns it took to reach the target points for the game. getting that points total more quickly than the opponents should increase your chances of winning
        rolls_per_turn_list.append( n_rolls_this_turn ) #keep track of the number of rolls that correspond to each turn
        points_per_turn_list.append( turn_score ) #keep track of the number of points that correspond to each turn
    return game_score, total_turns_to_target_game_score, rolls_per_turn_list, points_per_turn_list #return some useful parameters for downstream analysis

################################################################################
##### function that implements strategy 2 for a single game #####
#EDIT THIS STRATEGY SO THAT A TURN STOPS AS SOON AS THE TARGET GAME SCORE IS REACHED?
def strategy_2_game_simulation(target_turn_score, target_game_score):
    game_score = 0
    total_turns_to_target_game_score = 0
    rolls_per_turn_list = []
    points_per_turn_list = []
    while game_score < target_game_score: #keep taking turns until you get to the target points for a game (usually 100)
        n_rolls_this_turn = 0 #have rolled 0 times so far this turn
        turn_score = 0 #no points yet for this turn
        pigged_out = False #have not pigged out yet this turn
        while (turn_score < target_turn_score) and (not pigged_out): #take one turn, which consists of several rolls
            roll_test_val = np.random.random() #generate a random cumulative probability
            roll_score = all_possible_scores_array[all_possible_score_cumulative_probabilities_array > roll_test_val][0] #determine the score for this roll
            if roll_score > 0: #did NOT pig out on this roll
                turn_score += roll_score #add the score from this roll to the total score for this turn
            else: #pigged out on this roll
                turn_score = 0 #lose all points for this turn
                pigged_out = True #no more rolls allowed for this turn
            n_rolls_this_turn+=1 #have rolled one more time now for this turn
        game_score+=turn_score #total game score increases by the score accrued during all of the rolls for each turn
        total_turns_to_target_game_score+=1 #keep track of the number of turns it took to reach the target points for the game. getting that points total more quickly than the opponents should increase your chances of winning
        rolls_per_turn_list.append( n_rolls_this_turn ) #keep track of the number of rolls that correspond to each turn
        points_per_turn_list.append( turn_score ) #keep track of the number of points that correspond to each turn
    return game_score, total_turns_to_target_game_score, rolls_per_turn_list, points_per_turn_list #return some useful parameters for downstream analysis

################################################################################
##### simulate games to find out the number of turns required to get to 100 points for each strategy #####
#these strategies require the same number of rolls, on average
#is there a slight difference, based on the flexibility in score, that manifest in a significant advantage in performance for strategy 2 over the course of 1,000 games or so?
np.random.seed(1) #seed the random number generator for reproducibility
target_simulated_games = 10000
target_game_score = 100
n_turns_to_target_score_strat1 = np.empty(target_simulated_games) #initialize an array to record the number of turns it took to achieve the target game score with strategy 1
n_turns_to_target_score_strat2 = np.empty(target_simulated_games) #initialize an array to record the number of turns it took to achieve the target game score with strategy 2
n_simulated_games = 0
while n_simulated_games < target_simulated_games:
    outcome_strat_1 = strategy_1_game_simulation(strategy_1_target_rolls, target_game_score, False)
    outcome_strat_2 = strategy_2_game_simulation(strategy_2_target_score, target_game_score)
    n_turns_to_target_score_strat1[n_simulated_games] = outcome_strat_1[1]
    n_turns_to_target_score_strat2[n_simulated_games] = outcome_strat_2[1]
    n_simulated_games+=1
mean_turns_to_win_strategy_1 = np.mean(n_turns_to_target_score_strat1)
mean_turns_to_win_strategy_2 = np.mean(n_turns_to_target_score_strat2)
print( 'The mean number of turns required to achieve the target game score for WS1 is: {:0.2f}'.format( mean_turns_to_win_strategy_1 ) )
print( 'The mean number of turns required to achieve the target game score for WS2 is: {:0.2f}'.format( mean_turns_to_win_strategy_2 ) )

################################################################################
##### perform a t-test to determine whether the mean number of turns to win is smaller with strategy 2 #####
alpha_value = 0.05
[t_stat, two_side_p_val] = stats.ttest_ind( n_turns_to_target_score_strat2, n_turns_to_target_score_strat1, equal_var=False ) #two-sided t-test, do not assume the distributions have equal variance
one_side_p_val = two_side_p_val/2
print( 'p-value = ', two_side_p_val )
if (t_stat < 0) & (one_side_p_val < alpha_value):
    print( 'The mean number of turns using strategy 2 is less than that of strategy 1' )

################################################################################
##### some color options #####
#blue color=(0.42, 0.78, 0.90)
#orange color=(0.96, 0.69, 0.36)
#yellow color=(0.98, 0.82, 0.33)
#hot pink color=(0.91, 0.32, 0.51)
#light pink color=(0.96, 0.76, 0.78)

################################################################################
##### common plot settings #####
common_line_plot_settings = dict( linewidth=2.0, marker='h', markerfacecolor=(1.0, 1.0, 1.0), markeredgewidth=2)
common_text_annotation_settings = dict( size=12, color='black' )

################################################################################
##### plot the number of points a player can expect by stringing together successive rolls without pigging out #####
fig_01 = plt.figure(figsize=(10,5))
grid_01 = plt.GridSpec(2,2)
axes_01 = []
axes_01.append( fig_01.add_subplot(grid_01[:, 0]) )
axes_01.append( fig_01.add_subplot(grid_01[:, 1]) )

axes_01[0].set_title('expected score: never pig out')
axes_01[0].set_xlabel('consecutive rolls')
axes_01[0].set_ylabel('expected points accrued')
axes_01[0].set_xlim(0, len(n_rolls)-1)
axes_01[0].set_ylim(0, 100)
axes_01[0].set_xticks( n_rolls )
axes_01[0].plot( n_rolls, n_rolls_expected_score_no_pig_out, color=(0.91, 0.32, 0.51), **common_line_plot_settings, markersize=10 )

axes_01[1].set_title('odds of avoiding a pig out')
axes_01[1].set_xlabel('consecutive rolls')
axes_01[1].set_ylabel('probability not pigged out')
axes_01[1].set_xlim(0, len(n_rolls)-1)
axes_01[1].set_ylim(0, 1)
axes_01[1].set_xticks( n_rolls )
axes_01[1].plot( n_rolls, P_no_pig_out_n_rolls, color=(0.91, 0.32, 0.51), **common_line_plot_settings, markersize=10 )

fig_01.tight_layout()

if save_figs: #save the figure if you like
    figure_01_name = 'expected_score__and_pig_out_odds_by_roll.pdf'
    plt.savefig( out_path_figs + figure_01_name, dpi=150, format=None, transparent=True ) #facecolor='w', edgecolor='w')
    print( 'Saved figure ' + figure_01_name )

################################################################################
##### plot the score a player can expect from implementing strategy #1 using different set numbers of rolls #####
fig_02 = plt.figure(figsize=(5,5))
grid_02 = plt.GridSpec(3,3)
axes_02 = []
axes_02.append( fig_02.add_subplot(grid_02[:, :]) )

axes_02[0].set_title('strategy 1: always roll n times in a row')
axes_02[0].set_xlabel('consecutive rolls')
axes_02[0].set_ylabel('expected score')
axes_02[0].set_xlim(0, len(n_rolls)-1)
axes_02[0].set_ylim(0, 20)
axes_02[0].set_xticks( n_rolls )
axes_02[0].plot( [strategy_1_target_rolls, strategy_1_target_rolls], [0, 20], ':', color=(0,0,0), linewidth=1.0 )
axes_02[0].plot( [0, len(n_rolls)-1], [one_roll_expected_score, one_roll_expected_score], '--', color=(0.50, 0.50, 0.50), linewidth=2.0 )
axes_02[0].plot( n_rolls, strategy_1_scores_list, color=(0.42, 0.78, 0.90), **common_line_plot_settings, markersize=10 )
axes_02[0].annotate('inflection point', xy=(strategy_1_target_rolls, 13), xytext=(7, 15), arrowprops=dict(arrowstyle="->", connectionstyle="angle3,angleA=0,angleB=-90") )

axes_02[0].text( strategy_1_target_rolls - 0.5, 17.5, 'roll more', ha='right', **common_text_annotation_settings, bbox=dict(boxstyle='round', facecolor='green', edgecolor='green', alpha=0.1) )
axes_02[0].text( strategy_1_target_rolls + 0.5, 17.5, 'roll less', ha='left', **common_text_annotation_settings, bbox=dict(boxstyle='round', facecolor='red', edgecolor='red', alpha=0.1) )

fig_02.tight_layout()

if save_figs: #save the figure if you like
    figure_02_name = 'game_strategy_1_expected_outcome.pdf'
    plt.savefig( out_path_figs + figure_02_name, dpi=150, format=None, transparent=True ) #facecolor='w', edgecolor='w')
    print( 'Saved figure ' + figure_02_name )

################################################################################
##### plot the score a player can expect from implementing strategy #2 when they have different current scores #####
fig_03 = plt.figure(figsize=(5,5))
grid_03 = plt.GridSpec(3,3)
axes_03 = []
axes_03.append( fig_03.add_subplot(grid_03[:, :]) )

axes_03[0].set_title('strategy 2: stop rolling at threshold score')
axes_03[0].set_xlabel('current score')
axes_03[0].set_ylabel('expected score after next roll')
axes_03[0].set_xlim(0, 100)
axes_03[0].set_ylim(0, 100)
axes_03[0].plot( [strategy_2_target_score, strategy_2_target_score], [0, 100], ':', color=(0,0,0), linewidth=1.0 )
axes_03[0].plot( strategy_2_current_scores_list, strategy_2_current_scores_list, '--', color=(0.50, 0.50, 0.50), linewidth=2.0 )
axes_03[0].plot( strategy_2_current_scores_list, strategy_2_expected_scores_list, color=(0.96, 0.69, 0.36), **common_line_plot_settings, markersize=0 )
axes_03[0].annotate('intersection', xy=(30.67, 30.67), xytext=(40, 20), arrowprops=dict(arrowstyle="->", connectionstyle="angle3,angleA=0,angleB=-90") )

axes_03[0].text( strategy_2_target_score - 5, 80, 'roll again', ha='right', **common_text_annotation_settings, bbox=dict(boxstyle='round', facecolor='green', edgecolor='green', alpha=0.1) )
axes_03[0].text( strategy_2_target_score + 5, 80, 'stop rolling', ha='left', **common_text_annotation_settings, bbox=dict(boxstyle='round', facecolor='red', edgecolor='red', alpha=0.1) )

fig_03.tight_layout()

if save_figs: #save the figure if you like
    figure_03_name = 'game_strategy_2_expected_outcome.pdf'
    plt.savefig( out_path_figs + figure_03_name, dpi=150, format=None, transparent=True ) #facecolor='w', edgecolor='w')
    print( 'Saved figure ' + figure_03_name )

################################################################################
##### plot a comparison of the two game strategies #####
turns_to_target_score_bin_settings = range(0,25)
turns_to_target_score_bin_settings = [edge - 0.5 for edge in turns_to_target_score_bin_settings ] #slide the edges back by 0.5 so that bins are centered on integer values
turns_to_target_hist_settings = dict(density=False, bins=turns_to_target_score_bin_settings, histtype='stepfilled', alpha=0.6 )

#two histograms. show the distribution of the number of turns required to score 100 points using each strategy
fig_04 = plt.figure(figsize=(5,5))
grid_04 = plt.GridSpec(3,3)
axes_04 = []
axes_04.append( fig_04.add_subplot(grid_04[:, :]) )

axes_04[0].set_title('comparing game strategies')
axes_04[0].set_xlabel('number of turns')
axes_04[0].set_ylabel('number of games')
axes_04[0].set_xlim(0,25)
axes_04[0].set_ylim(0,target_simulated_games/5)

axes_04[0].hist( n_turns_to_target_score_strat1, **turns_to_target_hist_settings, color=(0.42, 0.78, 0.90) )
axes_04[0].hist( n_turns_to_target_score_strat2, **turns_to_target_hist_settings, color=(0.96, 0.69, 0.36) )

axes_04[0].plot( [mean_turns_to_win_strategy_1, mean_turns_to_win_strategy_1], [0, target_simulated_games/5], '--', linewidth=2.0 )
axes_04[0].plot( [mean_turns_to_win_strategy_2, mean_turns_to_win_strategy_2], [0, target_simulated_games/5], '--', linewidth=2.0 )

axes_04[0].text( 20, 1800, 'WS #1', ha='left', **common_text_annotation_settings, bbox=dict(boxstyle='round', facecolor=(0.42, 0.78, 0.90), edgecolor=(0.42, 0.78, 0.90), alpha=0.5) )
axes_04[0].text( 20, 1600, 'WS #2', ha='left', **common_text_annotation_settings, bbox=dict(boxstyle='round', facecolor=(0.96, 0.69, 0.36), edgecolor=(0.96, 0.69, 0.36), alpha=0.5) )

fig_04.tight_layout()

if save_figs: #save the figure if you like
    figure_04_name = 'game_strategy_turns_to_target_histograms.pdf'
    plt.savefig( out_path_figs + figure_04_name, dpi=150, format=None, transparent=True ) #facecolor='w', edgecolor='w')
    print( 'Saved figure ' + figure_04_name )

################################################################################
##### show plots #####
plt.show()
