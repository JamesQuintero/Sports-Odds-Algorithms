# Sports-Odds-Algorithms
System that calculates and uses algorithms to predict the outcome of NBA, NHL, and MLB games. Each league has its own unique algorithm to predict winners, with NBA having the most accurate algorithm. The system was originally intended to be used for sports betting. The algorithms are pretty good at predicting winners. With sports betting, it also has to be better at predicting winners than other betters, and the oddsmakers. 




[The NHL algorithm predicted the 2016 Stanley Cup Champion team, and its NHL playoff bracket was in the 99th percentile](http://smartsoftware.technology/sports.php?view=nhl&season=2016)

[Backtest results of betting strategies utilizing the algorithms' predictions](http://smartsoftware.technology/sports.php)


-----

Algorithms to predict NBA, NHL, and MLB games are included. To utilize, run sports_bettor.py

*sports_bettor.py*  

```
League
1) NBA
2) NHL
3) NFL
4) MLB
Choice:
```

If you want to find the winner for an NBA game, pick 1. 

```
League: nba
Menu:
1) Single team analysis
2) Calculate game odds (Single Game)
3) Calculate game odds (ALL Games Today)
4) Backtest algorithm
5) Test schedule scraper
Choice: 
```

If you want to find the winner for a single game, choose 2. 

```
Backtest menu: Algorithm version:
1) Algo_V1 - Uses a point system
2) Algo_V2 - Uses a probability system
Choice:
```

Algo_V2 tends to be more accurate. It gives a percentage of a team to win a game, while Algo_V1 gives an absolute number of points where the higher number of points for a team, the higher chance of them winning. 

```
nba teams:
0: atlanta-hawks
1: boston-celtics
2: brooklyn-nets
3: charlotte-hornets
4: chicago-bulls
5: cleveland-cavaliers
6: dallas-mavericks
7: denver-nuggets
8: detroit-pistons
9: golden-state-warriors
10: houston-rockets
11: indiana-pacers
12: los-angeles-clippers
13: los-angeles-lakers
14: memphis-grizzlies
15: miami-heat
16: milwaukee-bucks
17: minnesota-timberwolves
18: new-orleans-pelicans
19: new-york-knicks
20: oklahoma-city-thunder
21: orlando-magic
22: philadelphia-76ers
23: phoenix-suns
24: portland-trail-blazers
25: sacramento-kings
26: san-antonio-spurs
27: toronto-raptors
28: utah-jazz
29: washington-wizards
Away Team #:
Home Team #: 
```

Choose the number corresponding to the away team and home team for the NBA game. The system was scrape the latest game data for the 2 teams, run the algorithm, and then output the data (and save to a file in nba\analyze\team_comparison). 


```
Date to test (M-D-YYY): 4-16-2017
Current season year: 2017
```

"Date to test" means that all games played before that date will be included in the calculation. Typically, this would just be the current date if you want to include all games. 
The current season year will need to be provided. 


Using an example game Portland Trail Blazers @ Golden State Warriors in the 2017 NBA playoffs, the output is 

```
Away: portland-trail-blazers | Home: golden-state-warriors
Seasonal Record:      -81.53%
Home Away:            -91.33%
Home away 10:         -59.94%
Last 10 games:        -56.04%
Avg points:           -78.74%
Avg points 10:        -60.38%
--------
Total: -71.32%
--------
Perc chance to win: 71.32%
Favorable team odds: -248.6750348675034
Underdog team odds: +248.6750348675034
```

A positive total gives favorability to the away team, and a negative Total gives favorability to the home team. The total in this example is -71.32%, so the Golden State Warriors have a supposed 71.32% chance of winning the game. 

Favorable odds are given that are based off the percentage chance to win. In order for a bet to be +Expected Value, whether on the favorite orunderdog team, the odds would have to be higher than the given odds in the output. The favorite team is expected to win 71.23% of the time, so a bet on them should be no less than -248.67. Good bets include -240, -150, +150, etc. Bad bets include -250, -500, etc. Same for the underdog team where good bets would be higher than +248.67, like +250 and +550, while bad bets would be lower, like +200, +150, etc. 



-----

### Bare-bones algorithm information:

**Variables:** 
1) Record_points = ( wins - losses ) - ( other_wins - other_losses)
2) Home_away = (away_record - home_record) - (other tema's away record - other team's home record)
3) Home_away_10_games = Home_away for last 10 games
4) Last_10_games_points = Record_points for last 10 games
5) Avg_points = (total_points/num_games) - (other_total_points/num_games)
6) Avg_points_10_games = Avg_points for last 10 games
7) Win_streak = num consecutive wins
8) Win_streak_home_away = num consecutive wins home or away

*Example:* 
NBA's algo_V2 includes 1, 2, 3, 4, 5, 6
NHL's algo_V2 includes 1, 2, 3, 4, 5, 6, 8
MLB's algo_V2 includes 1, 2, 3, 4, 5, 6

**Backtests:** 

*CSV_output* = Backtest all games for 2nd half of seasons in specified timespan. The supplied algorithm will output a point system or percentage system accompanying its prediction. The results are returned in a csv file.

*Stats* = Backtest all games for 2nd half of seasons in specified timespan. The parameter algorithm will solely calculate wins vs losses for a 1-10 ranking system. The ranking sytem can be points or percentage based. The results are returned in a txt file. 

*Running sports_bettor.py:* Choose league, Backtest algorithm, Algo_V1, output to csv.
This will run a CSV_output backtest using a hardcoded algo_V1. EX: NBA = [10, 10, 5, 5,  8,  8,   3, 3];

*Running sports_bettor.py:* Choose league, Backtest algorith, Algo_V1, stats.
This will run a stats backtest for passed in algo_v1s that test each variable at a time. 


-----

### Creating an algorithm: 
**1)** Test each variable individually to create algo_V1

Menu choices: 4) Backtest algorithm -> 1) Algo_V1 - Uses a point system -> 2) Backtest Algo_V1 stats -> INPUT) Start Date: (middle of first season), End Date: (cur date if end 2nd half of current season, or end date of last season if in 1st half of current season)

* Default: algo_V1 = [-1, -1, -1, -1, -1, -1, -1, -1]
* Each parameter is respective to the variables.
	test each param like [1, -1, -1, -1, -1, -1, -1, -1]
	test each param like [2, -1, -1, -1, -1, -1, -1, -1]
* The results will be output to a txt file "./analyze/backtests/Algo_V1_-1,-1,0.5,-1,-1,-1,-1,-1_7-1-2003_10-1-2015.txt"
	EX output: 

	[1, -1, -1, -1, -1, -1, -1, -1]

	1: 537 - 536: 49.95%
	2: 615 - 716: 53.79%
	3: 640 - 683: 51.62%
	4: 572 - 696: 54.89%
	5: 553 - 654: 54.18%
	6: 506 - 631: 55.50%
	7: 477 - 590: 55.30%
	8: 369 - 586: 61.36%
	9: 369 - 497: 57.39%
	10: 1597 - 2351: 59.55%

	6235 - 7940

* 1-10 in the output file correspond to 1-10 levels in the program. Ideal to have a bell curve type distribution of total games from 1 (most games) to 10 (least games). 
* Also ideal if the percentage of games won start at 50 in level 1, and go to 100% by level 10. Level 10 should not have more games won than level 9. 
* The number used to create the ideal backtest output will be used in Algo_V1
*EX:* NHL = [3, 3, 3, 3, 0.3, 0.6, -1, 6]
* These will be the denominators for the variables. The maximum 1-10 level reached in the output will be the max_points. If level 10 isn't rached, the max level will be adjusted.

	
-----
	
	
**2)** Create algo_V2
	
* The games won percentage for each level in each output for each variable will create a polynomial equation for each variable. 
* Create a best-fit line for all perc_won numbers in the ideal output file. 
* The best-fit line will calculate the odds to win for that variable. 
* Best-fit line should start above 50%, and end below 100%
* 

	
**...(More information to be appended later)**


* The new algorithm should be hardcoded into algo.py to be utilized for odds calculation. 
