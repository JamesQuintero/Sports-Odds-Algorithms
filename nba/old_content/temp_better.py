# scrapes websites for urls then gets the url's robots.txts to get disallowed urls


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


class Sports_Better:

	opener = None
	Scraper=None

	user_agents=[]
	nba_teams=[]

	



	def __init__(self):
		self.initialize_user_agents()
		self.nba_teams=self.load_nba_teams()

	#analyzes a single team
	def single_team_analysis(self, team):

		print("Single Team Analysis:")
		print("1) Load data")
		print("2) Update data")
		choice=int(input("Choice: "))

		if choice==1:
			data=self.load_data(team, "")
			self.analyze(team, data)
		elif choice==2:
			self.update_data(team)

	#analyzes 2 teams and compares to determine which has best chance of winning
	def team_comparison(self, team1, team2):

		date=input("Date to test (M-D-YYYY): ")
		data1=self.load_data(team1, date)
		data2=self.load_data(team2, date)


		returned1=self.analyze2(team1, team2, data1, "away")
		returned2=self.analyze2(team2, team1, data2, "home")


		algo_data=self.algorithm(date, returned1, returned2)


		record_points=             algo_data['record_points']
		home_away_points=          algo_data['home_away_points']
		home_away_10_games_points= algo_data['home_away_10_games_points']
		last_10_games_points=      algo_data['last_10_games_points']
		avg_points=                algo_data['avg_points']
		avg_points_10_games=       algo_data['avg_points_10_games']
		total=                     algo_data['total']


		to_output=[]
		to_output.append("")
		to_output.append("Date: "+str(date))
		to_output.append("Away: "+str(team1[1])+" | Home: "+str(team2[1]))
		to_output.append("Seasonal Record:   "+str(record_points))
		to_output.append("Home Away:         "+str(home_away_points))
		to_output.append("Home away 10:      "+str(home_away_10_games_points))
		to_output.append("Last 10 games:     "+str(last_10_games_points))
		to_output.append("Avg points:        "+str(avg_points))
		to_output.append("Avg points 10:     "+str(avg_points_10_games))
		to_output.append("--------")
		to_output.append("Total: "+str(total))
		to_output.append("")


		for line in to_output:
			print(line)

		self.save_to_txt("./analyze/"+str(team1[1])+" - "+str(team2[1])+" analysis.txt", to_output)



	#backtests algorithm for games played on date
	def backtest(self, date):

		games=self.get_games(date)



		to_save=[]
		for x in range(0, len(games)):

			data1=self.load_data(games[x]['team1'], games[x]['date'])
			data2=self.load_data(games[x]['team2'], games[x]['date'])


			returned1=self.analyze2(games[x]['team1'], games[x]['team2'], data1, "away")
			returned2=self.analyze2(games[x]['team2'], games[x]['team1'], data2, "home")


			algo_data=self.algorithm(games[x]['date'], returned1, returned2)


			record_points=             algo_data['record_points']
			home_away_points=          algo_data['home_away_points']
			home_away_10_games_points= algo_data['home_away_10_games_points']
			last_10_games_points=      algo_data['last_10_games_points']
			avg_points=                algo_data['avg_points']
			avg_points_10_games=       algo_data['avg_points_10_games']
			total=                     algo_data['total']


			to_add=[]
			to_add.append("")
			to_add.append(games[x]['team1'][0])
			to_add.append(games[x]['team2'][0])
			to_add.append(total)


			#if team1 is projected to win
			if total>0:
				to_add.append(games[x]['team1'][0])
			elif total<0:
				to_add.append(games[x]['team2'][0])

			#if team1 actually won
			if games[x]['game_scores'][0]>games[x]['game_scores'][1]:
				to_add.append(games[x]['team1'][0])
			else:
				to_add.append(games[x]['team2'][0])

			score=str(games[x]['game_scores'][0])+"-"+str(games[x]['game_scores'][1])
			to_add.append(score)

			to_save.append(to_add)


		header=["", "Away", "Home", "Algo points", "Proj winner", "Winner", "Score"]
		to_save.insert(0, header)




		self.save_to_csv("./analyze/"+str(date)+"_analysis.csv", to_save)




		# record_points=             algo_data['record_points']
		# home_away_points=          algo_data['home_away_points']
		# home_away_10_games_points= algo_data['home_away_10_games_points']
		# last_10_games_points=      algo_data['last_10_games_points']
		# avg_points=                algo_data['avg_points']
		# avg_points_10_games=       algo_data['avg_points_10_games']
		# total=                     algo_data['total']



	#uses an algorithm 
	def algorithm(self, date, returned1, returned2):
		record_points             =self.calculate_points("seasonal_records",          returned1['seasonal_records'],  returned2['seasonal_records'])
		home_away_points          =self.calculate_points("home_away_records",         returned1['home_away_record'],  returned2['home_away_record'])
		home_away_10_games_points =self.calculate_points("home_away_10_game_records", returned1['home_away_record'],  returned2['home_away_record'])
		last_10_games_points      =self.calculate_points("last_10_games",             returned1['current_win_ratio'], returned2['current_win_ratio'])
		avg_points                =self.calculate_points("avg_points",                returned1['avg_game_points'],   returned2['avg_game_points'])
		avg_points_10_games       =self.calculate_points("avg_points_10_games",       returned1['avg_game_points'],   returned2['avg_game_points'])


		record_points             /=    10
		home_away_points          /=    10
		home_away_10_games_points /=    5
		last_10_games_points      /=    5
		avg_points                /=    8
		avg_points_10_games       /=    8



		total=record_points + home_away_points + home_away_10_games_points + last_10_games_points + avg_points + avg_points_10_games

		avg_points=self.convert_number(avg_points)
		avg_points_10_games=self.convert_number(avg_points_10_games)
		total=self.convert_number(total)

		to_return={}
		to_return['record_points']=             record_points
		to_return['home_away_points']=          home_away_points
		to_return['home_away_10_games_points']= home_away_10_games_points
		to_return['last_10_games_points']=      last_10_games_points
		to_return['avg_points']=                avg_points
		to_return['avg_points_10_games']=       avg_points_10_games
		to_return['total']=                     total
		return to_return





		
		# win_loss=returned['current_win_ratio']
		# last_10_games=returned['10_game_win_ratio']


		# wins_against=returned['win_loss_streaks_against']
		

	
		# won=last_10_games[-1][str(win_10_games)][0]
		# num_games=last_10_games[-1][str(win_10_games)][1]
		# if num_games!=0:
		# 	to_output.append(indent+"   "+str(won)+" won out of "+str(num_games)+" games | "+str(won/num_games*100)+"%")
		# else:
		# 	to_output.append(indent+"   "+str(won)+" won out of "+str(num_games)+" games | N/A%")


		

		# #on winning streak
		# if wins_against['games_since_last_loss']>0:
		# 	to_output.append(indent+"Winning streak against "+str(wins_against['other_team'])+": "+str(wins_against['games_since_last_loss']))
		# 	to_output.append(indent+"   Winning streak "+home_away+": "+str(wins_against['games_since_last_loss_'+str(home_away)]))
		# elif wins_against['games_since_last_win']>0:
		# 	to_output.append(indent+"Losing streak against "+str(wins_against['other_team'])+": "+str(wins_against['games_since_last_win']))
		# 	to_output.append(indent+"   Losing streak "+home_away+": "+str(wins_against['games_since_last_win_'+str(home_away)]))



	def calculate_points(self, calc_type, returned1, returned2):

		if calc_type=="seasonal_records":
			points=(returned1[-1][0]-returned1[-1][1]) - (returned2[-1][0]-returned2[-1][1])

		elif calc_type=="home_away_records":
			points=(returned1['away_record'][-1][0]-returned1['away_record'][-1][1]) - (returned2['home_record'][-1][0]-returned2['home_record'][-1][1])

		elif calc_type=="home_away_10_game_records":
			points=(returned1['away_10_games'][-1][0]-returned1['away_10_games'][-1][1]) - (returned2['home_10_games'][-1][0]-returned2['home_10_games'][-1][1])

		elif calc_type=="last_10_games":
			win_10_games1=0
			for x in range(len(returned1)-1, len(returned1)-11, -1):
				win_10_games1+=returned1[x][2]

			win_10_games2=0
			for x in range(len(returned2)-1, len(returned2)-11, -1):
				win_10_games2+=returned2[x][2]

			points=win_10_games1 - win_10_games2

		elif calc_type=="avg_points":
			points= (returned1['avg_game_points'][-1]-returned1['avg_other_game_points'][-1]) - (returned2['avg_game_points'][-1]-returned2['avg_other_game_points'][-1])

		elif calc_type=="avg_points_10_games":
			points= (returned1['avg_10_games'][-1]-returned1['avg_other_10_games'][-1]) - (returned2['avg_10_games'][-1]-returned2['avg_other_10_games'][-1])

		# elif calc_type=="win_streak":



		return points



	#gets games being played on specified date
	def get_games(self, date):

		folder_list=os.listdir("./team_data")

		#gets year directory to traverse from checking date var
		year="2016"
		for folder in folder_list:
			if folder in date:
				year=folder


		team_files=os.listdir("./team_data/"+year)


		games=[]
		for x in range(0, len(team_files)):

			team_name=team_files[x].replace(".csv", "")

			#gets full team name
			team=[]
			for y in range(0, len(self.nba_teams)):
				if team_name==self.nba_teams[y][1]:
					team=self.nba_teams[y]


			data=self.load_data(team, "")

			#gets data corresponding to year
			for y in range(0, len(data)):
				if data[y]['year']==year:
					data=data[y]
					break


			to_add={}
			for y in range(0, len(data['other_team'])):

				
				if data['dates'][y]==date:

					to_add['date']=data['dates'][y]

					#gets correct team data by just using abbreviation
					other_team=[]
					for z in range(0, len(self.nba_teams)):
						if data['other_team'][y]==self.nba_teams[z][0]:
							other_team=self.nba_teams[z]
							break

					#team1 = away team. team2 = home team.
					if data['home_away'][y]=="away":
						to_add['team1']=team
						to_add['team2']=other_team
					else:
						to_add['team1']=other_team
						to_add['team2']=team
						data['game_scores'][y].reverse()

					to_add['game_scores']=data['game_scores'][y]

					#makes sure to not add duplicate games
					exists=False
					for z in range(0, len(games)):
						if games[z]['team1']==to_add['team1'] and games[z]['team2']==to_add['team2']:
							exists=True
							break
					if exists==False:
						games.append(to_add)

					break

		
		return games







	#analyzes current team and 
	def analyze(self, team, data):

		if os.path.isdir("./analyze/"+str(team[1]))==False:
			os.mkdir("./analyze/"+str(team[1]))

		home_away=input("Are they home or away: ").lower()
		other_team=input("Playing against (3 letter abbreviation): ")


		returned=self.analyze2(team, other_team, data, home_away)
		self.save_analysis(team, data, returned, home_away)
		

		returned['output']=self.get_output_analysis("", team, returned, home_away)


		more_output=self.analyze_wins_ranked_teams(team, data)
		# more_output=[]

		for line in more_output:
			returned['output'].append(line)


		self.save_to_txt("./analyze/"+str(team[1])+"/"+str(team[1])+"_analysis.txt", returned['output'])





	# #analyzes whatever team needed for self.analyze()
	# def analyze2(self, team, other_team, data, home_away):

	# 	to_return={}


	# 	#seasonal win-loss ratio
	# 	records=self.get_seasonal_records(data)
	# 	to_save=[]
	# 	for x in range(0, len(records)):
	# 		to_save.append(["1-1-"+str(data[x]['year']), records[x][0]-records[x][1]])
	# 	to_return['seasonal_records']=to_save
		

		
	# 	#average point stats
	# 	avg_points=self.get_avg_points(data)
	# 	to_save=[]
	# 	for x in range(0, len(avg_points['avg_game_points'])):
	# 		to_add=[]
	# 		to_add.append("1-1-"+str(data[x]['year']))
	# 		to_add.append(avg_points['avg_game_points'][x])
	# 		to_add.append(avg_points['avg_other_game_points'][x])
	# 		to_add.append(avg_points['avg_game_points'][x]+avg_points['avg_other_game_points'][x])
	# 		for y in range(0, len(avg_points['avg_quarter_points'][x])):
	# 			to_add.append(avg_points['avg_quarter_points'][x][y])
	# 		to_save.append(to_add)
	# 	to_return['avg_game_points']=to_save



	# 	#stats in home vs away games
	# 	home_away_records=self.get_home_away_record(data)
	# 	to_save=[]
	# 	for x in range(0, len(home_away_records['home_record'])):
	# 		to_add=[]
	# 		to_add.append("1-1-"+str(data[x]['year']))
	# 		to_add.append(home_away_records['home_record'][x][0])
	# 		to_add.append(home_away_records['home_record'][x][1])
	# 		to_save.append(to_add)
	# 	to_save.append(["","",""])
	# 	to_save.append(["","",""])
	# 	to_save.append(["","",""])
	# 	for x in range(0, len(home_away_records['away_record'])):
	# 		to_add=[]
	# 		to_add.append("1-1-"+str(data[x]['year']))
	# 		to_add.append(home_away_records['away_record'][x][0])
	# 		to_add.append(home_away_records['away_record'][x][1])
	# 		to_save.append(to_add)
	# 	to_return['home_away_record']=to_save



	# 	#seasonal win-loss ratio
	# 	win_loss=self.get_current_win_ratio(data)
	# 	to_return['current_win_ratio']=win_loss
		


	# 	#last 10 games win ratio
	# 	last_10_games=self.analyze_10_games_win_ratio(data)
	# 	to_save=[]
	# 	to_save.append(["Year", "win-loss", "num wins", "num games"])
	# 	for x in range(0, len(last_10_games)):


	# 		for y in range(-10, 11, 2):
	# 			to_add=[]
	# 			#only has year at beginning of listing
	# 			if y==-10:
	# 				to_add.append(data[x]['year'])
	# 			else:
	# 				to_add.append("")

	# 			# to_add.append(str(y))
	# 			temp={'-10': '"0-10"', '-8': '"1-9"', '-6': '"2-8"', '-4': '"3-7"', '-2': '"4-6"', '0': '"5-5"', '2': '"6-4"', '4': '"7-3"', '6': '"8-2"', '8': '"9-1"', '10': '"10-0"'}
	# 			#turns -4 into "3-7"
	# 			to_add.append(temp[str(y)])
	# 			to_add.append(last_10_games[x][str(y)][0])
	# 			to_add.append(last_10_games[x][str(y)][1])
	# 			#gets win percentage
	# 			if last_10_games[x][str(y)][1]!=0:
	# 				to_add.append("=C"+str(len(to_save)+1)+"/D"+str(len(to_save)+1)+"*100")
	# 			else:
	# 				to_add.append(0)

	# 			to_save.append(to_add)
	# 		to_save.append(["", "", "", ""])
	# 	to_return['10_game_win_ratio']=to_save





	# 	#winning or losing streaks against specified team
	# 	to_save=[]
	# 	if other_team!="":
	# 		wins_against=self.get_win_streaks_against(other_team, data)
	# 		to_save.append(["Losing streak", wins_against['games_since_last_win']])
	# 		to_save.append(["Winning streak", wins_against['games_since_last_loss']])
	# 		if home_away=="away":
	# 			to_save.append(["Losing streak away", wins_against['games_since_last_win_away']])
	# 			to_save.append(["Winning streak away", wins_against['games_since_last_loss_away']])
	# 		elif home_away=="home":
	# 			to_save.append(["Losing streak home", wins_against['games_since_last_win_home']])
	# 			to_save.append(["Winning streak home", wins_against['games_since_last_loss_home']])
	# 	to_return['win_loss_streaks_against']=to_save



	# 	return to_return



	#analyzes whatever team needed for self.analyze()
	def analyze2(self, team, other_team, data, home_away):

		to_return={}

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
		to_return['win_loss_streaks_against']=self.get_win_streaks_against(other_team, data)

		return to_return




	def save_analysis(self, team, data, returned, home_away):

		#seasonal win-loss ratio
		records=returned['seasonal_records']
		to_save=[]
		for x in range(0, len(records)):
			to_save.append(["1-1-"+str(data[x]['year']), records[x][0]-records[x][1]])
		self.save_to_csv("./analyze/"+str(team[1])+"/"+str(team[1])+"_seasonal_records.csv", to_save)
		

		
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
		self.save_to_csv("./analyze/"+str(team[1])+"/"+str(team[1])+"_avg_game_points.csv", to_save)



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
		self.save_to_csv("./analyze/"+str(team[1])+"/"+str(team[1])+"_home_away_record.csv", to_save)



		#seasonal win-loss ratio
		win_loss=returned['current_win_ratio']
		self.save_to_csv("./analyze/"+str(team[1])+"/"+str(team[1])+"_current_win_ratio.csv", win_loss)
		


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
		self.save_to_csv("./analyze/"+str(team[1])+"/"+str(team[1])+"_10_game_win_ratio.csv", to_save)





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
		self.save_to_csv("./analyze/"+str(team[1])+"/"+str(team[1])+"_win_loss_streaks_against.csv", to_save)


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
	def analyze_wins_ranked_teams(self, team, data):

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

			#gets "los-angeles-lakers" if given "lal"
			for y in range(0, len(self.nba_teams)):
				name=self.nba_teams[y]
				if name[0]==other_team[0]:
					other_team[1]=name[1]




			indent="   "


			cur_data=self.load_data(team, date)
			print(cur_data[-1]['other_team'][-1])
			returned=self.analyze2(team, other_team[0], cur_data, data[-1]['home_away'][x])
			output=self.get_output_analysis(indent, team, returned, data[-1]['home_away'][x])

			for line in output:
				total_output.append(line)

			other_data=self.load_data(other_team, date)
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




	# #returns num wins/loss of self.team against other team
	# def get_win_stats_against(self, other_team, original_data):


	# 	to_return=[]
	# 	for x in range(0, len(original_data)):
	# 		data=original_data[x]

	# 		year=data['year']

	# 		wins=0
	# 		num_games=0
	# 		wins_away=0
	# 		wins_home=0
	# 		for y in range(0, len(data['other_team'])):
	# 			if data['other_team'][y]==other_team:
	# 				num_games+=1

	# 				if data['game_scores'][y][0]>data['game_scores'][y][1]:
	# 					wins+=1

	# 					if data['home_away'][y]=="away":
	# 						wins_away+=1
	# 					else:
	# 						wins_home+=1



	# 		to_add={}
	# 		to_add['year']=year
	# 		to_add['wins']=wins
	# 		to_add['num_games']=num_games
	# 		to_add['wins_away']=wins_away
	# 		to_add['wins_home']=wins_home

	# 		to_return.append(to_add)

	# 	#only keeps last 3 years
	# 	for x in range(0, len(to_return)-5):
	# 		to_return.pop(0)

	# 	return to_return

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

					if x==len(original_data)-1:
						print(str(year)+" | "+str(other_team)+" | "+str(data['game_scores'][y][0])+"-"+str(data['game_scores'][y][1]))

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



			# to_add={}
			# to_add['year']=year
			# to_add['wins']=wins
			# to_add['num_games']=num_games
			# to_add['wins_away']=wins_away
			# to_add['wins_home']=wins_home

			# to_return.append(to_add)

		return to_return

	# #gets percentage of games won if ahead after 1st quarter, 2nd quarter, etc.
	# def get_perc_win_quarters_ahead(self, data):



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
				print("Year: "+str(original_data[x]['year']))

				#gets avg_game_points
				total_points=0
				other_total_points=0
				for y in range(0, len(data['other_team'])):
					total_points+=data['game_scores'][y][0]
					other_total_points+=data['game_scores'][y][1]

				average=total_points/len(data['other_team'])
				average_other=other_total_points/len(data['other_team'])

				avg_game_points.append(self.convert_number(average))
				avg_other_game_points.append(self.convert_number(average_other))


				#gets average points for last 10 games
				total_points=0
				other_total_points=0
				for y in range(len(data['other_team'])-1, len(data['other_team'])-11, -1):
					total_points+=data['game_scores'][y][0]
					other_total_points+=data['game_scores'][y][1]
				average=total_points/10
				avg_10_games.append(self.convert_number(average))
				average=other_total_points/10
				avg_other_10_games.append(self.convert_number(average))



				#gets avg_game_points
				total_quarters=[0]*8
				for y in range(0, len(data['other_team'])):
					#adds current team's 4 quarters
					for z in range(0, 4):
						total_quarters[z]+=int(data['quarter_scores'][y][0][z])
					#adds other team's 4 quarters
					for z in range(0,4):
						total_quarters[z+4]+=int(data['quarter_scores'][y][1][z])
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





	def update_data(self, team):

		years=self.get_seasons(team)


		for x in range(0, len(years)):
			url="http://espn.go.com/nba/team/schedule/_/name/"+str(team[0])+"/year/"+str(years[x])+"/"+str(team[1])
			path="./team_data/"+str(years[x])+"/"+team[1]+".csv"
			print("URL: "+str(url))
			# print("PATH: "+str(path))

			# print(os.listdir("./team_data/2003/"))


			if os.path.isfile(path)==False:
				data=self.scrape_game_scores(url)


				data['other_team']=[]
				data['quarter_scores']=[]


				for game_url in data['game_urls']:
					time.sleep(1)
					quarter_data=self.scrape_quarter_data(team, url, game_url)
					other_team=quarter_data['other_team']
					quarter_scores=quarter_data['scores']
					if quarter_data['other_team']=="":
						time.sleep(5)
						quarter_data=self.scrape_quarter_data(team, url, game_url)
						other_team=quarter_data['other_team']
						quarter_scores=quarter_data['scores']

					data['other_team'].append(other_team)
					data['quarter_scores'].append(quarter_scores)



				to_save=[]
				for y in range(0, len(data['game_scores'])):
					score=data['game_scores'][y].split("-")

					if data['other_team'][y]!=0:

						temp=[]
						temp.append(str(data['dates'][y]))
						temp.append(data['other_team'][y])
						temp.append(data['home_away'][y])
						temp.append(score[0])
						temp.append(score[1])

						for quarter in data['quarter_scores'][y][0]:
							temp.append(quarter)

						for quarter in data['quarter_scores'][y][1]:
							temp.append(quarter)

					to_save.append(temp)

				
				print("Saving: "+str(path))
				self.save_to_csv(path, to_save)



	#loads all game data of specified team: ["lal", "los-angeles-lakers"]
	def load_data(self, team, date):
		print("Loading data of "+str(team[1])+"...")

		to_return=[]

		years=os.listdir("./team_data/")
		for x in range(0, len(years)):
			year=years[x]

			if os.path.isdir("./team_data/"+year):
				path="./team_data/"+year+"/"+team[1]+".csv"
				contents=self.read_from_csv(path)

				data={}
				data['year']=year
				data['dates']=[]
				data['other_team']=[]
				data['home_away']=[]
				data['game_scores']=[]
				data['quarter_scores']=[]
				for x in range(0, len(contents)):
					# self.game_urls.append("")

					#newly scraped data has dates with format 2-23-16.
					#csv files modified and saved again as csvs have format 2/23/16
					#changes 2/23/16 to 2-23-16
					contents[x][0]=contents[x][0].replace("/", "-")

					#stops loading data if date is reached
					if contents[x][0]==date:
						break

					data['dates'].append(contents[x][0])
					data['other_team'].append(contents[x][1])
					data['home_away'].append(contents[x][2])
					data['game_scores'].append([ int(contents[x][3].split(" ")[0]) , int(contents[x][4].split(" ")[0]) ])

					#loads all quarter scores into single list
					temp=[]
					for item in contents[x][5:]:
						if item!="":
							temp.append(int(item))

					#splits list in half to account for overtime quarters
					new_temp=[]
					while len(new_temp)<len(temp):
						new_temp.append(temp.pop())

					data['quarter_scores'].append([temp, new_temp])
				to_return.append(data)

		return to_return



	#gets years for listed seasons on ESPN's website
	def get_seasons(self, team):
		url="http://espn.go.com/nba/team/schedule/_/name/"+str(team[0])
		data=self.scrape_webpage(url)

		start=data.index("Year:")
		end=data[start:].index("</form>")

		new_data=data[start : start+end]

		# print(new_data)
		split=new_data.split('<option value="')
		#removes excess form data
		split.pop(0)
		#removes current season's url because we'll get it later
		split.pop(0)


		#retrieves season's year from URL in select HTML element
		to_return=[]
		for item in split:
			temp=item.split('"')
			url=temp[0]

			index=url.index("year/")
			year=url[ index+5: index+5+4]
			to_return.append(int(year))

		#Sorts smallest to largest then increments latest year to get current year
		#since ESPN's website doesn't include current season's
		to_return.sort()
		to_return.append(to_return[-1]+1)


		return to_return






	#gets scores and game urls
	#if new data, retrieve quarter scores and add all to global lists
	def scrape_game_scores(self, url):
		data={}
		data['dates']=[]
		data['home_away']=[]
		data['game_urls']=[]
		data['game_scores']=[]
		data['quarter_scores']=[]


		content=self.scrape_webpage(url)

		try:
			start=content.index("Regular Season Schedule")
			end=content.index("<!-- begin sponsored links -->")

			new_data=content[start:end]
			

			#separates each game
			temp=new_data.split('<li class="team-name">')

			#gets scores and game urls for better scores
			old_date=""
			for x in range(0, len(temp)):
				try:
					#if lost game
					lost="game-status loss" in temp[x]

					#determines whether game was at home or away
					if "@" in temp[x-1]:
						home_away="away"
					else:
						home_away="home"

					#gets game date
					temp_split=temp[x].split('<tr class="evenrow')
					if len(temp_split)==1:
						temp_split=temp[x].split('<tr class="oddrow')
					#turns ...][ team-90-24"><td>Wed, Oct 14</td><td><ul... into [ team-90-24"><td>Wed, Oct 14]
					temp_split=temp_split[1][: temp_split[1].index("</td>") ]
					#turns [ team-90-24"><td>Wed, Oct 14] into "Wed, Oct 14"
					string_date=temp_split.split("<td>")[1]
					#turns "Wed, Oct 14" into "Oct 14"
					string_date=string_date.split(", ")[1]
					#turns "Oct 14" into ["Oct", "14"]
					split_date=string_date.split(" ")
					months={"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
					#gets year from url
					split_url=url.split("/year/")
					year=int(split_url[1][: split_url[1].index("/") ])
					date=str(months[split_date[0]])+"-"+split_date[1]+"-"+str(year)
					if x==0:
						old_date=date



					string_to_find='<li class="score"><a href="'
					game_link=temp[x][ temp[x].index(string_to_find)+len(string_to_find): ]

					score=game_link[ game_link.index('">')+2:game_link.index("</a>") ]

					#if lost game, switch score order since site always lists highest score first
					if lost:
						temp2=score.split("-")
						score=temp2[1]+"-"+temp2[0]


					game_link=game_link[ :game_link.index('"') ]
					game_link="http://espn.go.com"+game_link

					#goes to playbyplay page since it has the same info and loads more quickly
					game_link=game_link.replace("recap", "playbyplay")

					data['dates'].append(old_date)
					data['game_urls'].append(game_link)
					data['game_scores'].append(score)
					data['home_away'].append(home_away)
					old_date=date


				except Exception as error:
					pass
			return data
		except Exception as error:
			print(error)

			return data


	#gets a game's scores for each quarter
	def scrape_quarter_data(self, team, team_url, game_url):

		print()
		data=self.scrape_webpage(game_url)

		print("Game url: "+str(game_url))
		if data=="":
			return {'other_team': "", 'scores': [[0,0,0,0], [0,0,0,0]]}


		try:
			start=data.index('<div id="custom-nav"')
			end=data[start:].index('<div id="gamepackage-links-wrap">')+start
		except Exception as error:
			print(error)
			return {'other_team': "", 'scores': [[0,0,0,0], [0,0,0,0]]}

		# split_data[start:end].split('class="abbrev"')
		
		split=data[start:end].split('<span class="abbrev"')
		split.pop(0)


		#returns [lal, lal, okc, okc]
		for x in range(0, len(split)):
			split[x]=split[x][ split[x].index(">")+1 : split[x].index("<")]

		# split.pop(0)
		# split.pop(1)
		
		team1=split[0].lower()
		team2=split[1].lower()
		print("Team1: "+str(team1)+" | Team2: "+str(team2))
		print("Cur team: "+str(team[0])+" | "+str(team[1]))
		



		# start=data.index('Final</span>')
		start=data.index('<div id="custom-nav"')
		end=start+data[start:].index("</table>")

		new_data=data[start:end].replace("\n", "").replace("\t", "")

		#separates each game
		rows=new_data.split('final-score">')

		rows.pop(0)
		rows.pop()
		for x in range(0, len(rows)):
			rows[x]=rows[x].split('team-name">')[-1]


		# temp=rows[0].replace("<", "").replace(">","").split("td")
		for x in range(0, len(rows)):
			rows[x]=rows[x].split("<td")
			rows[x].pop(0)
			rows[x].pop()
			for y in range(0, len(rows[x])):
				rows[x][y]=rows[x][y].replace("</td>", "")
				rows[x][y]=rows[x][y].replace(">", "")



		scores=rows
		if team1==team[0]:
			other_team=team2
		else:
			temp=scores[1]
			scores[1]=scores[0]
			scores[0]=temp
			other_team=team1
		

		#some games don't include a 4th quarter
		while len(scores[0])<4:
			scores[0].append(0)
		while len(scores[1])<4:
			scores[1].append(0)

		to_return={}
		to_return['other_team']=other_team
		to_return['scores']=scores
		# return scores
		return to_return


	def scrape_webpage(self, url):
		try:
			#initializes url variables
			self.opener.addheaders = [('User-agent', random.choice(self.user_agents))]

			response = self.opener.open(url, timeout=30)
			http_code=response.code
			info=response.info()

			data=response.read()
			data=data.decode('UTF-8', errors='ignore')

			#decode HTML
			h=html.parser.HTMLParser()
			data=h.unescape(data)

			return data
		except Exception as exception:
			print(exception)
			return ""

	def initialize_user_agents(self):
		self.user_agents.append("Mozilla/5.0 (X10; Ubuntu; Linux x86_64; rv:25.0)")
		self.user_agents.append("Mozilla/5.0 (Windows NT 6.0; WOW64; rv:12.0)")
		self.user_agents.append("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537")
		self.user_agents.append("Mozilla/5.0 (Windows NT 6.1) AppleWebKit/540 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/540")
		self.user_agents.append("Mozilla/5.0 (Windows; U; Windows NT 5.2; it; rv:1.8.1.11) Gecko/20071327 Firefox/2.0.0.10")
		self.user_agents.append("Opera/9.3 (Windows NT 5.1; U; en)")

		#initializes url variables
		self.opener=urllib.request.build_opener(urllib.request.HTTPRedirectHandler(),urllib.request.HTTPHandler(debuglevel=0))
		self.opener.addheaders = [('User-agent', random.choice(self.user_agents))]

	#loads list of nba teams
	def load_nba_teams(self):

		file_open=open('./nba_teams.txt')

		teams=[]
		for line in file_open:
			temp=line.split("|")

			for x in range(0, len(temp)):
				temp[x]=temp[x].strip()

			teams.append(temp)

		return teams


	def read_from_csv(self, path):
		if os.path.isfile(path):
			with open(path, newline='') as file:
				contents = csv.reader(file)

				temp_list=[]
				for row in contents:
					temp_matrix=[]
					for stuff in row:
						 temp_matrix.append(stuff)
					temp_list.append(temp_matrix)

				return temp_list
		else:
			return []

	def save_to_csv(self, path, data):
		with open(path, 'w', newline='') as file:
			contents = csv.writer(file)
			contents.writerows(data)

	def save_to_txt(self, path, data):
		with open(path, "w") as file:
			for item in data:
				file.write(str(item)+"\n\r")
		

	def convert_number(self, number):
		return int(number*100)/100



if __name__=="__main__":

	# game="nba"

	nba_scraper = Sports_Better()


	print("Menu")
	print("1) Single team analysis")
	print("2) Compare 2 teams")
	print("3) Backtest algorithm")
	choice=int(input("Choice: "))

	#single team analysis
	if choice==1:

		nba_teams=nba_scraper.load_nba_teams()
		print("NBA teams:")
		for x in range(0, len(nba_teams)):
			print(str(x)+": "+nba_teams[x][1])
		choice = int(input("Choice: "))

		nba_scraper.single_team_analysis(nba_teams[choice])

	#compares 2 teams and determines the winner
	elif choice==2:

		nba_teams=nba_scraper.load_nba_teams()
		print("NBA teams:")
		for x in range(0, len(nba_teams)):
			print(str(x)+": "+nba_teams[x][1])
		team1 = nba_teams[int(input("Away Team #: "))]
		team2 = nba_teams[int(input("Home Team #: "))]
		nba_scraper.team_comparison(team1, team2)

	#backtests algorithm
	elif choice==3:
		print("Backtest menu")
		print("1) Backtest date")
		print("2) Backtest a team")
		choice=int(input("Choice: "))

		if choice==1:
			date=input("Date: ")
			nba_scraper.backtest(date)

	

	# nba_scraper.run(nba_teams[choice])


	# nba_teams=nba_scraper.load_nba_teams()
	# choice=int(input("Choice: "))


	# if choice==1:
	# 	for x in range(0, int(len(nba_teams)/2)):
	# 		nba_scraper.single_team_analysis(nba_teams[x])

	# if choice==2:
	# 	for x in range(int(len(nba_teams)/2*1), int(len(nba_teams)/2*2)):
	# 		nba_scraper.single_team_analysis(nba_teams[x])



















