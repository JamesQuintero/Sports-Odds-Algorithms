# backtests sports betting algorithms

import os.path                  #script for directory/file handling
import csv                      #script for CSV file handling
import sys
from multiprocessing import Process
from universal_functions import Universal_Functions
from algo import Algo
from odds_calculator import Odds_Calculator


class Backtester:

	odds_calculator=None
	universal=None

	user_agents=[]
	league_teams=[]


	#can be nba, nhl, nfl, mlb
	league="nba"

	num_periods={'nba': 4, 'nhl': 3, 'nfl': 4, 'mlb': 9}
	


	#algo_version = "Algo_V1" or "Algo_V2"
	def __init__(self, league, algo_version):
		self.league=league.lower()
		self.algo_version=algo_version


		self.odds_calculator=  Odds_Calculator(self.league)
		self.universal=        Universal_Functions(self.league)

		self.league_teams=self.universal.load_league_teams()

	#backtests algorithm for games played on certain days
	#goes from start_date to end_date one day at a time during the season, and analyzes games played on those days
	#each day takes about 4 seconds on my desktop
	def backtest_csv_output(self, start_date, end_date):

		#breaks up date
		temp=start_date.split("-")
		month=int(temp[0])
		day=int(temp[1])
		year=int(temp[2])


		cur_date=start_date

		content=[]
		#this is actually a do-while loop
		while True:
			games=self.universal.get_games(cur_date)
			print("date: "+cur_date)

			for game in games:
				print("  Game: "+str(game))


			to_save=[]
			to_save.append([cur_date, "Away", "Home", "Algo points", "Proj winner", "Winner", "", "", "Score"])
			for x in range(0, len(games)):

				#team might not exist anymore, so don't count that game
				if len(games[x]['team1'])!=0 and len(games[x]['team2'])!=0:

					data1=     self.universal.load_data(games[x]['team1'], games[x]['date'])
					data2=     self.universal.load_data(games[x]['team2'], games[x]['date'])
					# print("Teams: "+str(games[x]['team1'])+" | "+str(games[x]['team2']))
					# print("date: "+str(games[x]['date']))
					# print(data1)
					# print(data1[0]['dates'][0])
					# print(data1[0]['dates'][-1])
					returned1= self.odds_calculator.analyze2(games[x]['team1'], games[x]['team2'], data1, "away")
					returned2= self.odds_calculator.analyze2(games[x]['team2'], games[x]['team1'], data2, "home")


					# print(returned1)
					# print()
					# print(returned2)
					# print() 

					algo = Algo(self.league)
					if self.algo_version=="Algo_V1":
						algo_data=algo.calculate(games[x]['date'], returned1, returned2)
					elif self.algo_version=="Algo_V2":
						algo_data=algo.calculate_V2(games[x]['date'], returned1, returned2)
					total=algo_data['total']


					to_add=[]
					to_add.append("")
					to_add.append(games[x]['team1'][0])
					to_add.append(games[x]['team2'][0])
					to_add.append(total)


					if self.algo_version=="Algo_V1":
						#categorizes odds (points)
						levels=[]
						levels.append([0,  3])
						levels.append([3,  6])
						levels.append([6,  9])
						levels.append([9,  12])
						levels.append([12, 15])
						levels.append([15, 18])
						levels.append([18, 21])
						levels.append([21, 24])
						levels.append([24, 27])
						levels.append([27, 100])
					elif self.algo_version=="Algo_V2":
						#categorizes odds (percentage)
						levels=[]
						levels.append([50, 55])
						levels.append([55, 60])
						levels.append([60, 65])
						levels.append([65, 70])
						levels.append([70, 75])
						levels.append([75, 80])
						levels.append([80, 85])
						levels.append([85, 90])
						levels.append([90, 95])
						levels.append([95, 100])


					level=0
					for y in range(0, len(levels)):
						if (total>=levels[y][0] and total<levels[y][1]) or (total*-1>=levels[y][0] and total*-1<levels[y][1]):
							level=y+1



					#appends projected team
					if total>0:
						to_add.append(games[x]['team1'][0])
					elif total<=0:
						to_add.append(games[x]['team2'][0])

					#appends winning team
					if games[x]['game_scores'][0]>games[x]['game_scores'][1]:
						to_add.append(games[x]['team1'][0])
					else:
						to_add.append(games[x]['team2'][0])

					#appends score
					score=str(games[x]['game_scores'][0])+"-"+str(games[x]['game_scores'][1])
					to_add.append(score)

					# #appends algo data
					# if to_add[-2]==to_add[-3]:
					# 	to_add.append("")
					# 	if self.algo_version=="Algo_V1":
					# 		to_add.append(str(level))
					# 	elif self.algo_version=="Algo_V2":
					# 		to_add.append(total)
					# elif to_add[-3]!="":
					# 	if self.algo_version=="Algo_V1":
					# 		to_add.append(str(level))
					# 	elif self.algo_version=="Algo_V2":
					# 		to_add.append(total)
					# 	to_add.append("")
					# else:
					# 	to_add.append("")
					# 	to_add.append("")

					#appends algo data
					if to_add[-2]==to_add[-3]:
						to_add.append("")
						to_add.append(str(level))
					elif to_add[-3]!="":
						to_add.append(str(level))
						to_add.append("")
					else:
						to_add.append("")
						to_add.append("")

					
					#appends betting odds
					if self.algo_version=="Algo_V1":
						odds_calculator=Odds_Calculator(self.league)
						odds=odds_calculator.get_odds(total)
					elif self.algo_version=="Algo_V2":
						odds=abs(total)

					favorable_odds=(100/(100-abs(odds)) - 1)*100
					underdog_odds=(100/(100-abs(odds)) - 1)*100
					if total>0:
						to_add.append("-"+str(favorable_odds))
						to_add.append("+"+str(underdog_odds))
					else:
						to_add.append("+"+str(underdog_odds))
						to_add.append("-"+str(favorable_odds))


					to_save.append(to_add)

			#space between data
			to_save.append(["", "", "", "", "", "", "", "", ""])

			#only saves day's games if there were actually games on that day
			if len(to_save)>2:
				content.append(to_save)

			#breaks loop to act like do-while
			if cur_date==end_date:
				break

			day+=1
			if day>31:
				month+=1
				day=1

			#doesn't increment year since the season's year doesn't change
			if month>12:
				month=1
				day=1

			#increments season at the end of the season to sometime in the middle
			if self.league=="nba":
				if "4-1-" in cur_date:
					year+=1
					month=2
					day=1
			elif self.league=="nhl":
				if "4-1-" in cur_date:
					year+=1
					month=2
					day=1
			elif self.league=="mlb":
				if "10-1-" in cur_date:
					year+=1
					month=7
					day=1

			cur_date=str(month)+"-"+str(day)+"-"+str(year)



		#has most recent games first
		content.reverse()

		to_save=[]
		for x in range(0, len(content)):
			for y in range(0, len(content[x])):
				to_save.append(content[x][y])




		if start_date!=end_date:
			self.universal.save_to_csv("./"+str(self.league)+"/analyze/"+str(self.league)+"_"+str(self.algo_version)+"_"+str(start_date)+"_"+str(end_date)+"_analysis.csv", to_save)
		else:
			self.universal.save_to_csv("./"+str(self.league)+"/analyze/"+str(self.league)+"_"+str(self.algo_version)+"_"+str(end_date)+"_analysis.csv", to_save)


	#backtests algo_V2 for games played on each day
	#goes from start_date to end_date one day at a time during the season, runs algo_V2 on those days, compares projected odds versus oddsportal odds, and simulates betting
	# each day takes about 4 seconds on my desktop
	def backtest_odds(self, start_date, end_date):

		#breaks up date
		temp=start_date.split("-")
		month=int(temp[0])
		day=int(temp[1])
		year=int(temp[2])


		cur_date=start_date

		content=[]
		#this is actually a do-while loop
		while True:
			games=self.universal.get_games(cur_date)
			print("date: "+cur_date)

			for game in games:
				print("  Game: "+str(game))



			# - Strategy 0.0: Bet on algo's projected winner, no matter the odds.
			# - Strategy 0.1: Bet on oddsmaker's projected winner, no matter the odds.
			# All below strategies incorporate placing a bet if the algorithm projects a team to win more often than the oddsmaker projects
			# - Strategy 1: Default strategy.
			# - Strategy 2: Placing a bet if that team is also the algo's favorite.
			# - Strategy 3: Placing a bet if that team is the algo's favorite, and the oddsmaker's underdog.
			# - Strategy 4: Placing a bet if the difference between the algorithm's projected odds and the oddsmaker's odds is also >= 45


			to_save=[]
			strat00={"total_bet": 0, "total_win": 0}
			strat01={"total_bet": 0, "total_win": 0}
			strat1={"total_bet": 0, "total_win": 0}
			strat2={"total_bet": 0, "total_win": 0}
			strat3={"total_bet": 0, "total_win": 0}
			strat4={"total_bet": 0, "total_win": 0}
			for x in range(0, len(games)):

				#team might not exist anymore, so don't count that game
				if len(games[x]['team1'])!=0 and len(games[x]['team2'])!=0:

					data1=     self.universal.load_data(games[x]['team1'], games[x]['date'])
					data2=     self.universal.load_data(games[x]['team2'], games[x]['date'])

					returned1= self.odds_calculator.analyze2(games[x]['team1'], games[x]['team2'], data1, "away")
					returned2= self.odds_calculator.analyze2(games[x]['team2'], games[x]['team1'], data2, "home")


					# print(returned1)
					# print()
					# print(returned2)
					# print()

					algo      = Algo(self.league)
					algo_data = algo.calculate_V2(games[x]['date'], returned1, returned2)
					total     = algo_data['total']


					# to_return={}
					# to_return['record_points']=             odds['records']
					# to_return['home_away_points']=          odds['home_away']
					# to_return['home_away_10_games_points']= odds['home_away_10_games']
					# to_return['last_10_games_points']=      odds['last_10_games']
					# to_return['avg_points']=                odds['avg_points']
					# to_return['avg_points_10_games']=       odds['avg_points_10_games']
					# # to_return['win_streak']=                win_streak
					# to_return['win_streak_home_away']=      odds['win_streak_home_away']
					# to_return['total']=                     self.universal.convert_number(average)

					odds=abs(total)

					favorable_odds = round((100/(100-abs(odds)) - 1)*100)
					underdog_odds  = round((100/(100-abs(odds)) - 1)*100)

					# print(str(year)+" | "+str(games[x]['team1'])+" | "+str(games[x]['team2'])+" | "+str(games[x]['game_scores']))

					oddsportal_odds = self.universal.get_odds_game(year, games[x]['team1'], games[x]['team2'], games[x]['game_scores'] )

					if oddsportal_odds[0]!=0:
						to_add=[]
						#date
						to_add.append(cur_date)
						#away
						to_add.append(games[x]['team1'][1])
						#home
						to_add.append(games[x]['team2'][1])
						#Algo Proj
						to_add.append(str(total)+"%")
						#Away proj
						away_proj=0
						if total<0:
							away_proj=favorable_odds
						else:
							away_proj=underdog_odds*-1
						to_add.append(away_proj)
						#Home proj	
						home_proj=0
						if total>0:
							home_proj=favorable_odds
						else:
							home_proj=underdog_odds*-1
						to_add.append(home_proj)
						#Away odds
						to_add.append(oddsportal_odds[0])
						#Home odds
						to_add.append(oddsportal_odds[1])
						#Diff Away
						away_diff=0
						if abs(away_proj - oddsportal_odds[0])>200:
							away_diff = abs(away_proj - oddsportal_odds[0])-200
						else:
							away_diff = abs(away_proj - oddsportal_odds[0])
						to_add.append(away_diff)
						#Diff Home
						home_diff=0
						if abs(home_proj - oddsportal_odds[1])>200:
							home_diff = abs(home_proj - oddsportal_odds[1])-200
						else:
							home_diff = abs(home_proj - oddsportal_odds[1])
						to_add.append(home_diff)



						## Strategy 0.0 ##
						if away_proj<0:
							#Bet
							to_add.append("$100")
							strat00['total_bet']+=100
							#To Win
							to_win=0
							if(oddsportal_odds[0]>0):
								to_win = 100*(oddsportal_odds[0]/100)
							else:
								to_win = 100/(oddsportal_odds[0]*-1/100)
							to_add.append("$"+str(to_win))
							#Won
							if games[x]['game_scores'][0]>games[x]['game_scores'][1]:
								to_add.append("$"+str(100+to_win))
								strat00['total_win']+=(100+to_win)
							else:
								to_add.append("$0")
						else:
							#Bet
							to_add.append("$100")
							strat00['total_bet']+=100
							#To Win
							to_win=0
							if(oddsportal_odds[1]>0):
								to_win = 100*(oddsportal_odds[1]/100)
							else:
								to_win = 100/(oddsportal_odds[1]*-1/100)
							to_add.append("$"+str(to_win))
							#Won
							if games[x]['game_scores'][1]>games[x]['game_scores'][0]:
								to_add.append("$"+str(100+to_win))
								strat00['total_win']+=(100+to_win)
							else:
								to_add.append("$0")


						## Strategy 0.1 ##
						if oddsportal_odds[0]<0 and oddsportal_odds[0]<oddsportal_odds[1]:
							#Bet
							to_add.append("$100")
							strat01['total_bet']+=100
							#To Win
							to_win=0
							if(oddsportal_odds[0]>0):
								to_win = 100*(oddsportal_odds[0]/100)
							else:
								to_win = 100/(oddsportal_odds[0]*-1/100)
							to_add.append("$"+str(to_win))
							#Won
							if games[x]['game_scores'][0]>games[x]['game_scores'][1]:
								to_add.append("$"+str(100+to_win))
								strat01['total_win']+=(100+to_win)
							else:
								to_add.append("$0")
						else:
							#Bet
							to_add.append("$100")
							strat01['total_bet']+=100
							#To Win
							to_win=0
							if(oddsportal_odds[1]>0):
								to_win = 100*(oddsportal_odds[1]/100)
							else:
								to_win = 100/(oddsportal_odds[1]*-1/100)
							to_add.append("$"+str(to_win))
							#Won
							if games[x]['game_scores'][1]>games[x]['game_scores'][0]:
								to_add.append("$"+str(100+to_win))
								strat01['total_win']+=(100+to_win)
							else:
								to_add.append("$0")



						## Strategy 1 ##
						if oddsportal_odds[0]>away_proj:
							#Bet
							to_add.append("$100")
							strat1['total_bet']+=100
							#To Win
							to_win=0
							if(oddsportal_odds[0]>0):
								to_win = 100*(oddsportal_odds[0]/100)
							else:
								to_win = 100/(oddsportal_odds[0]*-1/100)
							to_add.append("$"+str(to_win))
							#Won
							if games[x]['game_scores'][0]>games[x]['game_scores'][1]:
								to_add.append("$"+str(100+to_win))
								strat1['total_win']+=(100+to_win)
							else:
								to_add.append("$0")
						elif oddsportal_odds[1]>home_proj:
							#Bet
							to_add.append("$100")
							strat1['total_bet']+=100
							#To Win
							to_win=0
							if(oddsportal_odds[1]>0):
								to_win = 100*(oddsportal_odds[1]/100)
							else:
								to_win = 100/(oddsportal_odds[1]*-1/100)
							to_add.append("$"+str(to_win))
							#Won
							if games[x]['game_scores'][1]>games[x]['game_scores'][0]:
								to_add.append("$"+str(100+to_win))
								strat1['total_win']+=(100+to_win)
							else:
								to_add.append("$0")
						else:
							to_add.append("")
							to_add.append("")
							to_add.append("")



						## Strategy 2 ##
						if oddsportal_odds[0]>away_proj and away_proj<0:
							#Bet
							to_add.append("$100")
							strat2['total_bet']+=100
							#To Win
							to_win=0
							if(oddsportal_odds[0]>0):
								to_win = 100*(oddsportal_odds[0]/100)
							else:
								to_win = 100/(oddsportal_odds[0]*-1/100)
							to_add.append("$"+str(to_win))
							#Won
							if games[x]['game_scores'][0]>games[x]['game_scores'][1]:
								to_add.append("$"+str(100+to_win))
								strat2['total_win']+=(100+to_win)
							else:
								to_add.append("$0")
						elif oddsportal_odds[1]>home_proj and home_proj<0:
							#Bet
							to_add.append("$100")
							strat2['total_bet']+=100
							#To Win
							to_win=0
							if(oddsportal_odds[1]>0):
								to_win = 100*(oddsportal_odds[1]/100)
							else:
								to_win = 100/(oddsportal_odds[1]*-1/100)
							to_add.append("$"+str(to_win))
							#Won
							if games[x]['game_scores'][1]>games[x]['game_scores'][0]:
								to_add.append("$"+str(100+to_win))
								strat2['total_win']+=(100+to_win)
							else:
								to_add.append("$0")
						else:
							to_add.append("")
							to_add.append("")
							to_add.append("")


						## Strategy 3 ##
						if oddsportal_odds[0]>away_proj and away_proj<0 and oddsportal_odds[0]>0:
							#Bet
							to_add.append("$100")
							strat3['total_bet']+=100
							#To Win
							to_win=0
							if(oddsportal_odds[0]>0):
								to_win = 100*(oddsportal_odds[0]/100)
							else:
								to_win = 100/(oddsportal_odds[0]*-1/100)
							to_add.append("$"+str(to_win))
							#Won
							if games[x]['game_scores'][0]>games[x]['game_scores'][1]:
								to_add.append("$"+str(100+to_win))
								strat3['total_win']+=(100+to_win)
							else:
								to_add.append("$0")
						elif oddsportal_odds[1]>home_proj and home_proj<0 and oddsportal_odds[1]>0:
							#Bet
							to_add.append("$100")
							strat3['total_bet']+=100
							#To Win
							to_win=0
							if(oddsportal_odds[1]>0):
								to_win = 100*(oddsportal_odds[1]/100)
							else:
								to_win = 100/(oddsportal_odds[1]*-1/100)
							to_add.append("$"+str(to_win))
							#Won
							if games[x]['game_scores'][1]>games[x]['game_scores'][0]:
								to_add.append("$"+str(100+to_win))
								strat3['total_win']+=(100+to_win)
							else:
								to_add.append("$0")
						else:
							to_add.append("")
							to_add.append("")
							to_add.append("")



						## Strategy 4 ##
						if self.league=="mlb":
							diff_amount=45
						elif self.league=="nba":
							diff_amount=100

						if oddsportal_odds[0]>away_proj and away_diff>=diff_amount:
							#Bet
							to_add.append("$100")
							strat4['total_bet']+=100
							#To Win
							to_win=0
							if(oddsportal_odds[0]>0):
								to_win = 100*(oddsportal_odds[0]/100)
							else:
								to_win = 100/(oddsportal_odds[0]*-1/100)
							to_add.append("$"+str(to_win))
							#Won
							if games[x]['game_scores'][0]>games[x]['game_scores'][1]:
								to_add.append("$"+str(100+to_win))
								strat4['total_win']+=(100+to_win)
							else:
								to_add.append("$0")
						elif oddsportal_odds[1]>home_proj and home_diff>=diff_amount:
							#Bet
							to_add.append("$100")
							strat4['total_bet']+=100
							#To Win
							to_win=0
							if(oddsportal_odds[1]>0):
								to_win = 100*(oddsportal_odds[1]/100)
							else:
								to_win = 100/(oddsportal_odds[1]*-1/100)
							to_add.append("$"+str(to_win))
							#Won
							if games[x]['game_scores'][1]>games[x]['game_scores'][0]:
								to_add.append("$"+str(100+to_win))
								strat4['total_win']+=(100+to_win)
							else:
								to_add.append("$0")
						else:
							to_add.append("")
							to_add.append("")
							to_add.append("")




					else:
						to_add=[]



					# #appends winning team
					# if games[x]['game_scores'][0]>games[x]['game_scores'][1]:
					# 	to_add.append(games[x]['team1'][0])
					# else:
					# 	to_add.append(games[x]['team2'][0])

					# #appends score
					# score=str(games[x]['game_scores'][0])+"-"+str(games[x]['game_scores'][1])
					# to_add.append(score)

					if len(to_add)!=0:
						to_save.append(to_add)


			# to_save.append(["Date", "Away", "Home", "Algo proj", "Away proj", "Home proj", "Away odds", "Home odds", "Diff away", "Diff home", "Bet", "To win", "Won"])

			#only saves day's games if there were actually games on that day
			if len(to_save)>2:

				#summary
				strat00_profit=strat00['total_win']-strat00['total_bet']
				strat00_perc=strat00_profit/strat00['total_bet']*100
				strat01_profit=strat01['total_win']-strat01['total_bet']
				strat01_perc=strat01_profit/strat01['total_bet']*100
				strat1_profit=strat1['total_win']-strat1['total_bet']
				strat1_perc=strat1_profit/strat1['total_bet']*100
				strat2_profit=strat2['total_win']-strat2['total_bet']
				if(strat2['total_bet']>0):
					strat2_perc=strat2_profit/strat2['total_bet']*100
				else:
					strat2_perc=0
				strat3_profit=strat3['total_win']-strat3['total_bet']
				if(strat3['total_bet']>0):
					strat3_perc=strat3_profit/strat3['total_bet']*100
				else:
					strat3_perc=0
				strat4_profit=strat4['total_win']-strat4['total_bet']
				if(strat4['total_bet']>0):
					strat4_perc=strat4_profit/strat4['total_bet']*100
				else:
					strat4_perc=0

				#initializes with buffer columns
				summary=["", "", "", "", "", "", "", "", "", ""]
				summary.append("$"+str(strat00['total_bet']))
				summary.append("$"+str(strat00_profit))
				summary.append(str(strat00_perc)+"%")
				summary.append("$"+str(strat01['total_bet']))
				summary.append("$"+str(strat01_profit))
				summary.append(str(strat01_perc)+"%")
				summary.append("$"+str(strat1['total_bet']))
				summary.append("$"+str(strat1_profit))
				summary.append(str(strat1_perc)+"%")
				summary.append("$"+str(strat2['total_bet']))
				summary.append("$"+str(strat2_profit))
				summary.append(str(strat2_perc)+"%")
				summary.append("$"+str(strat3['total_bet']))
				summary.append("$"+str(strat3_profit))
				summary.append(str(strat3_perc)+"%")
				summary.append("$"+str(strat4['total_bet']))
				summary.append("$"+str(strat4_profit))
				summary.append(str(strat4_perc)+"%")
				to_save.append(summary)

				#space between data
				to_save.append(["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])

				content.append(to_save)

			#breaks loop to act like do-while
			if cur_date==end_date:
				break

			day+=1
			if day>31:
				month+=1
				day=1

			#doesn't increment year since the season's year doesn't change
			if month>12:
				month=1
				day=1

			#increments season at the end of the season to sometime in the middle
			if self.league=="nba":
				# if "4-1-" in cur_date:
				# 	year+=1
				# 	month=2
				# 	day=1
				if "4-1-" in cur_date:
					year+=1
					month=1
					day=15
			elif self.league=="nhl":
				if "4-1-" in cur_date:
					year+=1
					month=2
					day=1
			elif self.league=="mlb":
				if "10-1-" in cur_date:
					year+=1
					month=7
					day=1

			cur_date=str(month)+"-"+str(day)+"-"+str(year)



		# #has most recent games first
		# content.reverse()

		to_save=[]
		to_save.append(["Date", "Away", "Home", "Algo proj", "Away proj", "Home proj", "Away odds", "Home odds", "Diff away", "Diff home", "Bet", "To win", "Won", "Bet", "To win", "Won", "Bet", "To win", "Won", "Bet", "To win", "Won"])
		for x in range(0, len(content)):
			for y in range(0, len(content[x])):
				to_save.append(content[x][y])




		if start_date!=end_date:
			self.universal.save_to_csv("./"+str(self.league)+"/analyze/"+str(self.league)+"_Algo_V2_"+str(start_date)+"_"+str(end_date)+"_backtest_odds.csv", to_save)
		else:
			self.universal.save_to_csv("./"+str(self.league)+"/analyze/"+str(self.league)+"_Algo_V2_"+str(end_date)+"_backtest_odds.csv", to_save)

	#backtests algorithm for games played on certain days
	def backtest_algo(self, start_date, end_date, algo):

		#breaks up date
		temp=start_date.split("-")
		month=int(temp[0])
		day=int(temp[1])
		year=int(temp[2])


		cur_date=start_date

		#creates saving path if doesn't exist
		algo_list=str(algo).replace("[", "").replace("]", "").replace(" ", "")

		path="./"+str(self.league)+"/analyze/backtests/"+str(self.algo_version)+"_"+str(algo_list)+"_"+str(start_date)+"_"+str(end_date)+".txt"

		if os.path.exists(path)==True:
			return



		#gets list of dates to backtest
		dates=[]
		while True:
			dates.append(cur_date)

			#breaks loop to act like do-while
			if cur_date==end_date:
				break

			print("Cur date: "+str(cur_date)+" | End date: "+str(end_date))

			day+=1
			if day>31:
				month+=1
				day=1

			#doesn't increment year since the season's year doesn't change
			if month>12:
				month=1
				day=1

			#increments season once April is reached since it's so close to the end of the season
			if self.league=="nhl":
				if "4-1-" in cur_date:
					year+=1
					month=2
					day=1
			elif self.league=="nba":
				if "4-1-" in cur_date:
					year+=1
					month=2
					day=1
			elif self.league=="mlb":
				if "10-1-" in cur_date:
					year+=1
					month=7
					day=1

			cur_date=str(month)+"-"+str(day)+"-"+str(year)

		#6 is hardcoded in self.backtest_algo2
		# 6 processes takes up 75% of my desktop CPU, and backtest takes 20 min to complete
		# c4.4xlarge has 16 logical processors, and takes 4.5 min to complete
		# 6 processes for the c4.4xlarge takes ~10 min to complete
		num_processes=16
		processes=[]
		#creates processes
		for x in range(0, num_processes):
			path="./"+str(self.league)+"/analyze/backtests/"+str(algo_list)+"_temp"+str(x)+".csv"
			if os.path.exists(path)==False:
				process=Process(target=self.backtest_algo2, args=(x, dates,algo, ))
				processes.append(process)

		#starts processes
		for x in range(0, len(processes)):
			processes[x].start()

		#joins them so they don't wait for each other
		for x in range(0, len(processes)):
			processes[x].join()


		# self.backtest_algo2(0, dates, algo)
		

		#loads results from processes since I you can't return anything from processes
		wins=[0]*11
		losses=[0]*11
		for x in range(0, num_processes):
			path="./"+str(self.league)+"/analyze/backtests/"+str(algo_list)+"_temp"+str(x)+".csv"
			contents=self.universal.read_from_csv(path)

			for y in range(0, len(contents)):
				losses[y]+=int(contents[y][0])
				wins[y]+=int(contents[y][1])

			os.remove(path)



		to_output=[]
		to_output.append(str(algo))
		to_output.append("")

		total_wins=0
		total_losses=0

		#starts at 1 since levels start at 1
		for x in range(1, len(wins)):
			total_wins+=wins[x]
			total_losses+=losses[x]
			if wins[x]+losses[x]!=0:
				perc_won=wins[x]/(wins[x]+losses[x])*100
			else:
				perc_won="N/A"
			to_output.append(str(x)+": "+str(losses[x])+" - "+str(wins[x])+": "+str(perc_won))
		to_output.append("")
		to_output.append(str(total_losses)+" - "+str(total_wins))

		
		path="./"+str(self.league)+"/analyze/backtests/"+str(self.algo_version)+"_"+str(algo_list)+"_"+str(start_date)+"_"+str(end_date)+".txt"
		self.universal.save_to_txt(path, to_output)

	#used in backtest_algo()
	def backtest_algo2(self, number, dates, algo):
		#level number corresponds to an index
		wins=[0]*11
		losses=[0]*11


		#creates processes
		num_processes=16
		start=int(number*(len(dates)/num_processes))
		end=int((number+1)*(len(dates)/num_processes))

		print()
		print(number)
		print(start)
		print(end)
		print()

		#this is actually a do-while loop
		for x in range(start, end):
			print("At "+str(dates[x])+" END: "+str(dates[end-1]))

			games=self.universal.get_games(dates[x])


			for y in range(0, len(games)):

				#team might not exist anymore, so don't count that game
				if len(games[y]['team1'])!=0 and len(games[y]['team2'])!=0:

					data1=     self.universal.load_data(games[y]['team1'], games[y]['date'])
					data2=     self.universal.load_data(games[y]['team2'], games[y]['date'])
					returned1= self.odds_calculator.analyze2(games[y]['team1'], games[y]['team2'], data1, "away")
					returned2= self.odds_calculator.analyze2(games[y]['team2'], games[y]['team1'], data2, "home")


					algorithm=Algo(self.league)
					#sets algo to backtest
					algorithm.algorithm[self.league]=algo
					if self.algo_version=="Algo_V1":
						algo_data=algorithm.calculate(games[y]['date'], returned1, returned2)
					elif self.algo_version=="Algo_V2":
						algo_data=algorithm.calculate_V2(games[y]['date'], returned1, returned2)
					total=algo_data['total']




					if self.algo_version=="Algo_V1":
						#categorizes odds
						levels=[]
						levels.append([0,  3])
						levels.append([3,  6])
						levels.append([6,  9])
						levels.append([9,  12])
						levels.append([12, 15])
						levels.append([15, 18])
						levels.append([18, 21])
						levels.append([21, 24])
						levels.append([24, 27])
						levels.append([27, 100])
					elif self.algo_version=="Algo_V2":
						#categorizes odds
						levels=[]
						levels.append([50, 55])
						levels.append([55, 60])
						levels.append([60, 65])
						levels.append([65, 70])
						levels.append([70, 75])
						levels.append([75, 80])
						levels.append([80, 85])
						levels.append([85, 90])
						levels.append([90, 95])
						levels.append([95, 100])

					level=0
					for z in range(0, len(levels)):
						if (total>=levels[z][0] and total<levels[z][1]) or (total*-1>=levels[z][0] and total*-1<levels[z][1]):
							level=z+1


					# #0 is team1, and 1 is team2
					# projected_team=0
					# if self.league=="nba":
					# 	#if team1 is projected to win
					# 	if total>0:
					# 		projected_team=0
					# 	#go with home team
					# 	elif total<=0:
					# 		projected_team=1
					# else:
					# 	#if team1 is projected to win
					# 	if total>0:
					# 		projected_team=0
					# 	#go with home team
					# 	elif total<=0:
					# 		projected_team=1

					#0 is team1, and 1 is team2
					#if team1 is projected to win
					if total>0:
						projected_team=0
					#go with home team
					elif total<=0:
						projected_team=1

					#0 is team1, and 1 is team2
					winning_team=0
					if games[y]['game_scores'][0]>games[y]['game_scores'][1]:
						winning_team=0
					else:
						winning_team=1

					#if algo was right
					if projected_team==winning_team:
						wins[level]+=1
					else:
						losses[level]+=1

		temp=[]

		for x in range(0, len(wins)):
			temp.append([losses[x], wins[x]])

		algo_list=str(algo).replace("[", "").replace("]", "").replace(" ", "")
		path="./"+str(self.league)+"/analyze/backtests/"+str(algo_list)+"_temp"+str(number)+".csv"
		self.universal.save_to_csv(path, temp)
