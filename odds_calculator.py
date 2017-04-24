# gathers sports game data for odds calculation by an algorithm


import urllib.request           #script for URL request handling
import urllib.parse             #script for URL handling
from urllib import request
import html.parser              #script for HTML handling
import os.path                  #script for directory/file handling
import csv                      #script for CSV file handling
import time                     #scripting timing handling
import datetime                   #data and time handling
from datetime import date
import json
import sys
import random
from threading import Thread
from espn_scraper import ESPN_Scraper
from universal_functions import Universal_Functions
from algo import Algo


class Odds_Calculator:

	opener = None
	scraper=None
	algo=None
	universal=None

	user_agents=[]


	#can be nba, nhl, nfl, mlb
	league="nba"

	num_periods={'nba': 4, 'nhl': 3, 'nfl': 4, 'mlb': 9}
	



	def __init__(self, league):
		self.league=league.lower()
		self.universal=Universal_Functions(self.league)
		self.espn_scraper = ESPN_Scraper(self.league)

	#analyzes a single team
	def single_team_analysis(self, team):
		cur_year=input("Current season year: ")
		self.espn_scraper.update_data(team, cur_year)
		data=self.universal.load_data(team, "", cur_year)
		self.analyze(team, data, cur_year)

	#analyzes 2 teams and compares to determine which has best chance of winning
	def team_comparison(self, algo_version, team1, team2, date, cur_year):

		self.algo=Algo(self.league)

		self.espn_scraper.update_data(team1, cur_year)
		self.espn_scraper.update_data(team2, cur_year)

		data1=self.universal.load_data(team1, date, cur_year)
		data2=self.universal.load_data(team2, date, cur_year)


		returned1=self.analyze2(team1, team2, data1, "away")
		returned2=self.analyze2(team2, team1, data2, "home")

		# print(str(team1)+" | "+str(team2))
		# print(returned1)
		# print(returned2)
		# print()

		if algo_version=="Algo_V1":
			algo_data=self.algo.calculate(date, returned1, returned2)
		elif algo_version=="Algo_V2":
			algo_data=self.algo.calculate_V2(date, returned1, returned2)


		record_points=             algo_data['record_points']
		home_away_points=          algo_data['home_away_points']
		home_away_10_games_points= algo_data['home_away_10_games_points']
		last_10_games_points=      algo_data['last_10_games_points']
		avg_points=                algo_data['avg_points']
		avg_points_10_games=       algo_data['avg_points_10_games']
		# win_streak_10_games=       algo_data['win_streak_10_games']
		if self.league=="nhl":
			win_streak_home_away=       algo_data['win_streak_home_away']
		total=                     algo_data['total']

		to_output=[]
		to_output.append("")
		to_output.append("Date: "+str(date))
		to_output.append("Away: "+str(team1[1])+" | Home: "+str(team2[1]))

		if algo_version=="Algo_V1":
			win_streak=              algo_data['win_streak']
			win_streak_home_away=    algo_data['win_streak_home_away']
			if self.league=="nba":
				to_output.append("Seasonal Record:      "+str(record_points*10)+"/10 = "+str(record_points))
				to_output.append("Home Away:            "+str(home_away_points*10)+"/10 = "+str(home_away_points))
				to_output.append("Home away 10:         "+str(home_away_10_games_points*5)+"/5 = "+str(home_away_10_games_points))
				to_output.append("Last 10 games:        "+str(last_10_games_points*5)+"/5 = "+str(last_10_games_points))
				to_output.append("Avg points:           "+str(avg_points*8)+"/8 = "+str(avg_points))
				to_output.append("Avg points 10:        "+str(avg_points_10_games*8)+"/8 = "+str(avg_points_10_games))
				to_output.append("Win streak:           "+str(win_streak*3)+"/3 = "+str(win_streak))
				to_output.append("Win streak home away: "+str(win_streak_home_away*3)+"/3 = "+str(win_streak_home_away))
			else:
				to_output.append("Seasonal Record:      "+str(record_points*5)+"/5 = "+str(record_points))
				to_output.append("Home Away:            "+str(home_away_points*5)+"/5 = "+str(home_away_points))
				to_output.append("Home away 10:         "+str(home_away_10_games_points*5)+"/5 = "+str(home_away_10_games_points))
				to_output.append("Last 10 games:        "+str(last_10_games_points*5)+"/5 = "+str(last_10_games_points))
				to_output.append("Avg points:           "+str(avg_points/2)+"*2 = "+str(avg_points))
				to_output.append("Avg points 10:        "+str(avg_points_10_games/2)+"*2 = "+str(avg_points_10_games))
				to_output.append("Win streak:           "+str(win_streak*3)+"/3 = "+str(win_streak))
				to_output.append("Win streak home away: "+str(win_streak_home_away*3)+"/3 = "+str(win_streak_home_away))
			to_output.append("--------")
			to_output.append("Total: "+str(total))
			to_output.append("--------")

		elif algo_version=="Algo_V2":
			to_output.append("Seasonal Record:      "+str(record_points)+"%")
			to_output.append("Home Away:            "+str(home_away_points)+"%")
			to_output.append("Home away 10:         "+str(home_away_10_games_points)+"%")
			to_output.append("Last 10 games:        "+str(last_10_games_points)+"%")
			to_output.append("Avg points:           "+str(avg_points)+"%")
			to_output.append("Avg points 10:        "+str(avg_points_10_games)+"%")
			# to_output.append("Win streak:           "+str(win_streak)+"%")
			if self.league=="nhl":
				to_output.append("Win streak home away: "+str(win_streak_home_away)+"%")
			to_output.append("--------")
			to_output.append("Total: "+str(total)+"%")
			to_output.append("--------")



		
	


		#chance of favorable team winning
		if algo_version=="Algo_V1":
			winning_odds=self.get_odds(total)
		elif algo_version=="Algo_V2":
			winning_odds=abs(total)

		to_output.append("Perc chance to win: "+str(winning_odds)+"%")

		favorable_odds=(100/(100-winning_odds) - 1)*100
		underdog_odds=(100/(100-winning_odds) - 1)*100
		to_output.append("Favorable team odds: -"+str(favorable_odds))
		to_output.append("Underdog team odds: +"+str(underdog_odds))


		return to_output

	#gets odds of winning for algo_V1
	def get_odds(self, total_points):

		#puts total points at a max of 27
		max_points=27
		if abs(total_points)>max_points:
			total_points=max_points
		


		x=abs(total_points)/max_points*10

		#2D polynomial that follows the percentage chance of winning per level of ranking 1-10
		if self.league=="nba":
			y=-0.23*(x**2) + 7.25*x + 47.9
		else:
			y=-0.23*(x**2) + 7.25*x + 47.9

		if y<50:
			y=50
		

		return y






	#analyzes current team
	def analyze(self, team, data, end_year):

		if os.path.isdir("./"+str(self.league)+"/analyze/single_analysis/"+str(team[1]))==False:
			os.mkdir("./"+str(self.league)+"/analyze/single_analysis/"+str(team[1]))

		home_away=input("Are they home or away: ").lower()
		other_team=input("Playing against (letter abbreviation): ")


		returned=self.analyze2(team, other_team, data, home_away)
		self.save_analysis(team, data, returned, home_away)
		

		returned['output']=self.get_output_analysis("", team, returned, home_away)


		more_output=self.analyze_wins_ranked_teams(team, data, end_year)
		# more_output=[]

		for line in more_output:
			returned['output'].append(line)


		self.universal.save_to_txt("./"+str(self.league)+"/analyze/single_analysis/"+str(team[1])+"/"+str(team[1])+"_analysis.txt", returned['output'])


	#analyzes whatever team needed for self.analyze()
	def analyze2(self, team, other_team, data, home_away):

		print("Analyzing "+str(team))

		to_return={}

		season_record=self.get_seasonal_records(data)

		# print("Season record: "+str(season_record))

		# input("waiting...")

		#seasonal win-loss ratio
		to_return['seasonal_records']=self.get_seasonal_records(data)
		#average point stats
		to_return['avg_game_points']=self.get_avg_points(data)
		#stats in home vs away games
		to_return['home_away_record']=self.get_home_away_record(data)
		#seasonal win-loss ratio
		to_return['current_win_ratio']=self.get_current_win_ratio(data)
		#last 10 games win ratio
		to_return['10_game_win_ratio']=self.analyze_10_games_win_ratio(data)
		#winning or losing streaks against specified team
		#definition only accepts "lal" and not ["lal", "los-angeles-lakers"], so check
		if isinstance(other_team, list):
			to_return['win_loss_streaks_against']=self.get_win_streaks_against(other_team[0], data)
		else:
			to_return['win_loss_streaks_against']=self.get_win_streaks_against(other_team, data)

		return to_return




	def save_analysis(self, team, data, returned, home_away):

		#seasonal win-loss ratio
		records=returned['seasonal_records']
		to_save=[]
		for x in range(0, len(records)):
			to_save.append(["1-1-"+str(data[x]['year']), records[x][0]-records[x][1]])
		path="./"+str(self.league)+"/analyze/single_analysis/"+str(team[1])+"/"+str(team[1])+"_seasonal_records.csv"
		self.universal.save_to_csv(path, to_save)
		print("Saved to "+str(path))
		

		
		#average point stats
		avg_points=returned['avg_game_points']
		to_save=[]
		for x in range(0, len(avg_points['avg_game_points'])):
			to_add=[]
			to_add.append("1-1-"+str(data[x]['year']))
			to_add.append(avg_points['avg_game_points'][x])
			to_add.append(avg_points['avg_other_game_points'][x])
			to_add.append(avg_points['avg_game_points'][x]+avg_points['avg_other_game_points'][x])
			for y in range(0, len(avg_points['avg_quarter_points'][x])):
				to_add.append(avg_points['avg_quarter_points'][x][y])
			to_save.append(to_add)
		path="./"+str(self.league)+"/analyze/single_analysis/"+str(team[1])+"/"+str(team[1])+"_avg_game_points.csv"
		self.universal.save_to_csv(path, to_save)
		print("Saved to "+str(path))



		#stats in home vs away games
		home_away_records=returned['home_away_record']
		to_save=[]
		for x in range(0, len(home_away_records['home_record'])):
			to_add=[]
			to_add.append("1-1-"+str(data[x]['year']))
			to_add.append(home_away_records['home_record'][x][0])
			to_add.append(home_away_records['home_record'][x][1])
			to_save.append(to_add)
		to_save.append(["","",""])
		to_save.append(["","",""])
		to_save.append(["","",""])
		for x in range(0, len(home_away_records['away_record'])):
			to_add=[]
			to_add.append("1-1-"+str(data[x]['year']))
			to_add.append(home_away_records['away_record'][x][0])
			to_add.append(home_away_records['away_record'][x][1])
			to_save.append(to_add)
		path="./"+str(self.league)+"/analyze/single_analysis/"+str(team[1])+"/"+str(team[1])+"_home_away_record.csv"
		self.universal.save_to_csv(path, to_save)
		print("Saved to "+str(path))



		#seasonal win-loss ratio
		win_loss=returned['current_win_ratio']
		path="./"+str(self.league)+"/analyze/single_analysis/"+str(team[1])+"/"+str(team[1])+"_current_win_ratio.csv"
		self.universal.save_to_csv(path, win_loss)
		print(path)
		


		#last 10 games win ratio
		last_10_games=returned['10_game_win_ratio']
		to_save=[]
		to_save.append(["Year", "win-loss", "num wins", "num games"])
		for x in range(0, len(last_10_games)):
			for y in range(-10, 11, 2):
				to_add=[]
				#only has year at beginning of listing
				if y==-10:
					to_add.append(data[x]['year'])
				else:
					to_add.append("")

				# to_add.append(str(y))
				temp={'-10': '"0-10"', '-8': '"1-9"', '-6': '"2-8"', '-4': '"3-7"', '-2': '"4-6"', '0': '"5-5"', '2': '"6-4"', '4': '"7-3"', '6': '"8-2"', '8': '"9-1"', '10': '"10-0"'}
				#turns -4 into "3-7"
				to_add.append(temp[str(y)])
				to_add.append(last_10_games[x][str(y)][0])
				to_add.append(last_10_games[x][str(y)][1])
				#gets win percentage
				if last_10_games[x][str(y)][1]!=0:
					to_add.append("=C"+str(len(to_save)+1)+"/D"+str(len(to_save)+1)+"*100")
				else:
					to_add.append(0)

				to_save.append(to_add)
			to_save.append(["", "", "", ""])
		path="./"+str(self.league)+"/analyze/single_analysis/"+str(team[1])+"/"+str(team[1])+"_10_game_win_ratio.csv"
		self.universal.save_to_csv(path, to_save)
		print(path)





		#winning or losing streaks against specified team
		to_save=[]
		wins_against=returned['win_loss_streaks_against']
		to_save.append(["Losing streak", wins_against['games_since_last_win']])
		to_save.append(["Winning streak", wins_against['games_since_last_loss']])
		if home_away=="away":
			to_save.append(["Losing streak away", wins_against['games_since_last_win_away']])
			to_save.append(["Winning streak away", wins_against['games_since_last_loss_away']])
		elif home_away=="home":
			to_save.append(["Losing streak home", wins_against['games_since_last_win_home']])
			to_save.append(["Winning streak home", wins_against['games_since_last_loss_home']])
		path="./"+str(self.league)+"/analyze/single_analysis/"+str(team[1])+"/"+str(team[1])+"_win_loss_streaks_against.csv"
		self.universal.save_to_csv(path, to_save)
		print(path)


	def get_output_analysis(self, indent, team, returned, home_away):

		records=returned['seasonal_records']
		avg_points=returned['avg_game_points']
		home_away_records=returned['home_away_record']
		win_loss=returned['current_win_ratio']
		last_10_games=returned['10_game_win_ratio']
		wins_against=returned['win_loss_streaks_against']

		#### output ####
		to_output=[]
		to_output.append("")
		to_output.append("")
		to_output.append(indent+team[1])

		if (records[-1][0]-records[-1][1])>(records[-2][0]-records[-2][1]):
			temp="uptrend"
		else:
			temp="downtrend"
		to_output.append(indent+"Season: "+str(records[-1][0]-records[-1][1])+" on "+str(temp))

		if home_away=="away":
			to_output.append(indent+"Home-Away: "+str(home_away_records['away_record'][-1][0])+"-"+str(home_away_records['away_record'][-1][1])+" away")
			to_output.append(indent+"   Last 10 away games: "+str(home_away_records['away_10_games'][-1][0])+"-"+str(home_away_records['away_10_games'][-1][1]))
		elif home_away=="home":
			to_output.append(indent+"Home-Away: "+str(home_away_records['home_record'][-1][0])+"-"+str(home_away_records['home_record'][-1][1])+" home")
			to_output.append(indent+"   Last 10 home games: "+str(home_away_records['home_10_games'][-1][0])+"-"+str(home_away_records['home_10_games'][-1][1]))
		

		win_10_games=0
		for x in range(len(win_loss)-1, len(win_loss)-11, -1):
			win_10_games+=win_loss[x][2]

		temp={'-10': '0-10', '-8': '1-9', '-6': '2-8', '-4': '3-7', '-2': '4-6', '0': '5-5', '2': '6-4', '4': '7-3', '6': '8-2', '8': '9-1', '10': '10-0'}
		to_output.append(indent+"10 Games: "+temp[str(win_10_games)])
		won=last_10_games[-1][str(win_10_games)][0]
		num_games=last_10_games[-1][str(win_10_games)][1]
		if num_games!=0:
			to_output.append(indent+"   "+str(won)+" won out of "+str(num_games)+" games | "+str(won/num_games*100)+"%")
		else:
			to_output.append(indent+"   "+str(won)+" won out of "+str(num_games)+" games | N/A%")


		to_output.append(indent+"Avg points: "+str(avg_points['avg_game_points'][-1])+" - "+str(avg_points['avg_other_game_points'][-1]))
		to_output.append(indent+"   Last 10 games: "+str(avg_points['avg_10_games'][-1])+" - "+str(avg_points['avg_other_10_games'][-1]))

		#on winning streak
		if wins_against['games_since_last_loss']>0:
			to_output.append(indent+"Winning streak against "+str(wins_against['other_team'])+": "+str(wins_against['games_since_last_loss']))
			to_output.append(indent+"   Winning streak "+home_away+": "+str(wins_against['games_since_last_loss_'+str(home_away)]))
		elif wins_against['games_since_last_win']>0:
			to_output.append(indent+"Losing streak against "+str(wins_against['other_team'])+": "+str(wins_against['games_since_last_win']))
			to_output.append(indent+"   Losing streak "+home_away+": "+str(wins_against['games_since_last_win_'+str(home_away)]))

		return to_output















	#analyzes number of wins against teams of certain rankings. Like # wins against even teams (23-25 to 27-25) or against good teams (30-15) or bad teams (15-30)... etc
	def analyze_wins_ranked_teams(self, team, data, end_year):

		total_output=[]
		for x in range(len(data[-1]['other_team'])-1, len(data[-1]['other_team'])-11, -1):
			other_team=[]
			other_team.append(data[-1]['other_team'][x])
			other_team.append("")

			date=data[-1]['dates'][x]
			# print("Date: "+str(date))

			home_away=data[-1]['home_away'][x]
			if home_away=="home":
				other_home_away="away"
			elif home_away=="away":
				other_home_away="home"

			temp=[]
			temp.append(date)
			temp.append(other_team)
			# temp.append()

			league_teams=self.universal.load_league_teams()

			#gets "los-angeles-lakers" if given "lal"
			for y in range(0, len(league_teams)):
				name=league_teams[y]
				if name[0]==other_team[0]:
					other_team[1]=name[1]




			indent="   "


			cur_data=self.universal.load_data(team, date, end_year)
			print(cur_data[-1]['other_team'][-1])
			returned=self.analyze2(team, other_team[0], cur_data, data[-1]['home_away'][x])
			output=self.get_output_analysis(indent, team, returned, data[-1]['home_away'][x])

			for line in output:
				total_output.append(line)

			other_data=self.universal.load_data(other_team, date, end_year)
			print(str(other_data[-1]['other_team'][-1])+" | "+str(date)+" | "+str(other_data[-1]['dates'][-5]))
			returned=self.analyze2(other_team, team[0], other_data, other_home_away)
			output=self.get_output_analysis(indent, other_team, returned, other_home_away)

			print()
			for line in output:
				print(line)
				total_output.append(line)
			total_output.append("")

			#adds winner and scores
			cur_team_score=data[-1]['game_scores'][x][0]
			other_team_score=data[-1]['game_scores'][x][1]
			if cur_team_score>other_team_score:
				total_output.append(indent+"Winner: "+team[1]+" | "+str(cur_team_score)+"-"+str(other_team_score))
			else:
				total_output.append(indent+"Winner: "+other_team[1]+" | "+str(other_team_score)+"-"+str(cur_team_score))


			total_output.append(indent+"----------------------------------------")
			print()


		return total_output



	#returns wins/loss streaks against other_team
	def get_win_streaks_against(self, other_team, original_data):

		to_return={}
		to_return['other_team']=other_team
		to_return['games_since_last_win']=0
		to_return['games_since_last_loss']=0
		to_return['games_since_last_win_away']=0
		to_return['games_since_last_win_home']=0
		to_return['games_since_last_loss_away']=0
		to_return['games_since_last_loss_home']=0
		for x in range(0, len(original_data)):
			data=original_data[x]

			year=data['year']

		
			for y in range(0, len(data['other_team'])):
				if data['other_team'][y]==other_team:

					# if x==len(original_data)-1:
					# 	print(str(year)+" | "+str(other_team)+" | "+str(data['game_scores'][y][0])+"-"+str(data['game_scores'][y][1]))

					#if won
					if data['game_scores'][y][0]>data['game_scores'][y][1]:
						to_return['games_since_last_win']=0
						to_return['games_since_last_loss']+=1


						if data['home_away'][y]=="away":
							to_return['games_since_last_win_away']=0
							to_return['games_since_last_loss_away']+=1
						else:
							to_return['games_since_last_win_home']=0
							to_return['games_since_last_loss_home']+=1
					#if lost
					else:
						to_return['games_since_last_win']+=1
						to_return['games_since_last_loss']=0


						if data['home_away'][y]=="away":
							to_return['games_since_last_win_away']+=1
							to_return['games_since_last_loss_away']=0
						else:
							to_return['games_since_last_win_home']+=1
							to_return['games_since_last_loss_home']=0

		return to_return





	# #gets percentage of games won if ahead after 1st quarter, 2nd quarter, etc.
	# def get_perc_win_quarters_ahead(self, data):

	# #gets total goals for and goals against
	# def get_goals_for_against(self, data):



	#determines whether teams win or lose more often if they have a good or bad last 10 games
	def analyze_10_games_win_ratio(self, original_data):

		to_return=[]
		for x in range(0, len(original_data)):
			data=original_data[x]


			year=data['year']

			#win_data['4'] will hold data for last 10 games with ratio 7-3
			#increments by 2 since subtracting losses from wins of last 10 games will never have odd number
			win_data={}
			for y in range(-10, 11, 2):
				win_data[str(y)]=[0,0]

			last_10_record=[]
			for y in range(0, len(data['other_team'])):

				#only gets win ratio if 10 records present

				if len(last_10_record)==10:
					temp=sum(last_10_record)

				#adding 1 or -1 is same as subtracting num losses from num wins
				if data['game_scores'][y][0]>data['game_scores'][y][1]:
					#only counts this win if 10 records already present
					if len(last_10_record)==10:
						win_data[str(sum(last_10_record))][0]+=1
						win_data[str(sum(last_10_record))][1]+=1

					last_10_record.append(1)
				else:
					if len(last_10_record)==10:
						win_data[str(sum(last_10_record))][1]+=1

					last_10_record.append(-1)


				if len(last_10_record)>10:
					last_10_record.pop(0)

			to_return.append(win_data)

		return to_return


	#gets win-loss ratio during each game during the current season
	def get_current_win_ratio(self, original_data):

		data=original_data[-1]


		to_return=[]
		cur_score=0
		for x in range(0, len(data['game_scores'])):
			to_add=[]
			to_add.append(data['game_scores'][x][0])
			to_add.append(data['game_scores'][x][1])
			# print(data['other_team'][x]+" | "+str(to_add))
			if data['game_scores'][x][0]>data['game_scores'][x][1]:
				temp=1
			else:
				temp=-1

			to_add.append(temp)
			cur_score+=temp
			to_add.append(cur_score)
			to_return.append(to_add)
		return to_return


	#gets wins-losses while at home or away
	def get_home_away_record(self, original_data):

		to_return={}
		to_return['home_record']=[]
		to_return['away_record']=[]
		to_return['home_10_games']=[]
		to_return['away_10_games']=[]
		for x in range(0, len(original_data)):
			data=original_data[x]


			home_away=data['home_away']
			game_scores=data['game_scores']

			home_record=[]
			away_record=[]
			for y in range(0, len(home_away)):

				if home_away[y]=="home":
					if game_scores[y][0]>game_scores[y][1]:
						home_record.append(1)
					else:
						home_record.append(-1)
				elif home_away[y]=="away":
					if game_scores[y][0]>game_scores[y][1]:
						away_record.append(1)
					else:
						away_record.append(-1)


			to_return['home_record'].append([home_record.count(1), home_record.count(-1)])
			to_return['away_record'].append([away_record.count(1), away_record.count(-1)])

			#gets stats on last 10 games
			home_10_games=[ home_record[-10:].count(1), home_record[-10:].count(-1) ]
			away_10_games=[ away_record[-10:].count(1), away_record[-10:].count(-1) ]


			to_return['home_10_games'].append(home_10_games)
			to_return['away_10_games'].append(away_10_games)

		return to_return



	#calculates a bunch of average points stats
	def get_avg_points(self, original_data):

		to_return={}


		avg_game_points=[]
		avg_other_game_points=[]
		avg_10_games=[]
		avg_other_10_games=[]
		avg_quarters=[]
		for x in range(0, len(original_data)):
			
			data=original_data[x]

			if len(data['other_team'])!=0:
				# print("Year: "+str(original_data[x]['year']))

				#gets avg_game_points
				total_points=0
				other_total_points=0
				for y in range(0, len(data['other_team'])):
					total_points+=data['game_scores'][y][0]
					other_total_points+=data['game_scores'][y][1]

				average=total_points/len(data['other_team'])
				average_other=other_total_points/len(data['other_team'])

				avg_game_points.append(self.universal.convert_number(average))
				avg_other_game_points.append(self.universal.convert_number(average_other))


				#gets average points for last 10 games
				total_points=0
				other_total_points=0
				for y in range(len(data['other_team'])-1, len(data['other_team'])-11, -1):
					total_points+=data['game_scores'][y][0]
					other_total_points+=data['game_scores'][y][1]
				average=total_points/10
				avg_10_games.append(self.universal.convert_number(average))
				average=other_total_points/10
				avg_other_10_games.append(self.universal.convert_number(average))



				#gets avg_game_points
				num_periods=self.num_periods[self.league]
				total_quarters=[0]*num_periods*2
				for y in range(0, len(data['other_team'])):
					# print(data['period_scores'][y])
					# print("Num periods: "+str(num_periods))

					#adds current team's 4 quarters
					try:
						for z in range(0, num_periods):
							total_quarters[z]+=int(data['period_scores'][y][0][z])
					except Exception as error:
						pass

					#adds other team's 4 quarters
					try:
						for z in range(0, len(data['period_scores'][y][1])):
							total_quarters[z+num_periods]+=int(data['period_scores'][y][1][z])
					except Exception as error:
						pass

				#gets average quarter scores
				for y in range(0, len(total_quarters)):
					total_quarters[y]=total_quarters[y]/len(data['other_team'])

				avg_quarters.append(total_quarters)



		to_return['avg_game_points']=avg_game_points
		to_return['avg_other_game_points']=avg_other_game_points
		to_return['avg_10_games']=avg_10_games
		to_return['avg_other_10_games']=avg_other_10_games
		to_return['avg_quarter_points']=avg_quarters
		return to_return



	#gets records like 2016: 49-20 for all seasons
	def get_seasonal_records(self, original_data):
		records=[]
		for x in range(0, len(original_data)):
			data=original_data[x]

			num_wins=0
			for y in range(0, len(data['other_team'])):
				if data['game_scores'][y][0]>data['game_scores'][y][1]:
					num_wins+=1

			# record=num_wins-len(data['game_scores'])-num_wins
			record=[num_wins, len(data['game_scores'])-num_wins]
			records.append(record)

		return records








	# #loads all game data of specified team: ["lal", "los-angeles-lakers"]
	# def load_data(self, team, date):


	# 	print("Loading data of "+str(team[1])+"...")

	# 	to_return=[]
	# 	reached_end=False

	# 	years=os.listdir("./"+str(self.league)+"/team_data/")
	# 	for x in range(0, len(years)):
	# 		year=years[x]

	# 		if os.path.isdir("./"+str(self.league)+"/team_data/"+year) and reached_end==False:
	# 			path="./"+str(self.league)+"/team_data/"+year+"/"+team[1]+".csv"
	# 			contents=self.read_from_csv(path)

	# 			data={}
	# 			data['year']=year
	# 			data['dates']=[]
	# 			data['other_team']=[]
	# 			data['home_away']=[]
	# 			data['game_scores']=[]
	# 			data['period_scores']=[]
	# 			for x in range(0, len(contents)):
	# 				# self.game_urls.append("")

	# 				#newly scraped data has dates with format 2-23-16.
	# 				#csv files modified and saved again as csvs have format 2/23/16
	# 				#changes 2/23/16 to 2-23-16
	# 				contents[x][0]=contents[x][0].replace("/", "-")

	# 				#stops loading data if date is reached
	# 				if contents[x][0]==date:
	# 					reached_end=True
	# 					break

	# 				data['dates'].append(contents[x][0])
	# 				data['other_team'].append(contents[x][1])
	# 				data['home_away'].append(contents[x][2])
	# 				data['game_scores'].append([ int(contents[x][3].split(" ")[0]) , int(contents[x][4].split(" ")[0]) ])

	# 				#loads all quarter scores into single list
	# 				temp=[]
	# 				for item in contents[x][5:]:
	# 					if item!="":
	# 						temp.append(int(item))

	# 				#splits list in half to account for overtime quarters
	# 				new_temp=[]
	# 				while len(new_temp)<len(temp):
	# 					new_temp.append(temp.pop())

	# 				data['period_scores'].append([temp, new_temp])
	# 			to_return.append(data)

	# 	return to_return

