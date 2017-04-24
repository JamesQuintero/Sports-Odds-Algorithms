# Main script that utilizes the other scripts


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
from odds_calculator import Odds_Calculator
from oddsportal_scraper import Odds_Portal_Scraper
from universal_functions import Universal_Functions
from backtester import Backtester
from algo import Algo


class Sports_Better:

	scraper=None
	universal=None

	user_agents=[]
	league_teams=[]

	output=[]
	output_path=""


	#can be nba, nhl, nfl, mlb
	league="nba"

	num_periods={'nba': 4, 'nhl': 3, 'nfl': 4, 'mlb': 9}
	



	def __init__(self, league):
		self.league=league.lower()
		self.universal=Universal_Functions(self.league)


		self.output=[]
		today=self.universal.get_today()
		time=self.universal.get_current_time()
		#10:45 becomes 1045
		time = time.replace(":", "")
		self.output_path = "./"+league+"/output/output_"+str(today['month'])+"-"+str(today['day'])+"-"+str(today['year'])+"_"+str(time)+".txt"
		self.output.append("---- Start output ----")
		self.to_print("League: "+str(league))

		self.scraper=ESPN_Scraper(self.league)


	#prompts user for version of algorithm they want to use
	def get_algo_version(self):
		print("Backtest menu: Algorithm version:")
		print("1) Algo_V1 - Uses a point system")
		print("2) Algo_V2 - Uses a probability system")
		algo_version=int(input("Choice: "))
		
		if algo_version==1:
			algo_version="Algo_V1"
		elif algo_version==2:
			algo_version="Algo_V2"

		return algo_version

	#analyzes a single team
	def single_team_analysis(self):
		self.to_print("single_team_analysis()")

		league_teams=self.universal.load_league_teams()
		print(self.league+" teams:")
		for x in range(0, len(league_teams)):
			print(str(x)+": "+league_teams[x][1])
		choice = int(input("Choice: "))
		print()

		self.to_print("User chose "+str(league_teams[choice]))
		odds_calculator = Odds_Calculator(self.league)
		odds_calculator.single_team_analysis(league_teams[choice])

		self.save_output()

	#calculates betting odds for a game
	def calculate_odds_single_game(self):
		algo_version=self.get_algo_version()


		league_teams=self.universal.load_league_teams()

		#Prompts user for teams playing
		print(self.league+" teams:")
		for x in range(0, len(league_teams)):
			print(str(x)+": "+league_teams[x][1])
		team1 = int(input("Away Team #: "))
		team2 = int(input("Home Team #: "))
		
		print()

		date=input("Date to test (M-D-YYY): ")
		year=input("Current season year: ")

		
		# teams_to_test=[[team1, team2]]


		teams_to_test=[ 
		[28, 19],
		[19, 28],
		[21, 3],
		[3, 21],
		[2, 15],
		[15, 2],
		[22, 25],
		[25, 22],
		[27, 6],
		[6, 27],
		[23, 13],
		[13, 23],
		[10, 1],
		[1, 10],
		[0, 16],
		[16, 0],
		[28, 25],
		[25, 28],
		[21, 2],
		[2, 21],
		[27, 16],
		[16, 27],
		[23, 10],
		[10, 23],
		[25, 2],
		[2, 25],
		[27, 23],
		[23, 27],
		[2, 27],
		[27, 2],
		]

		for x in range(0, len(teams_to_test)):

			team1 = league_teams[teams_to_test[x][0]]
			team2 = league_teams[teams_to_test[x][1]]


			odds_calculator = Odds_Calculator(self.league)
			output=odds_calculator.team_comparison(algo_version, team1, team2, date, year)

			for line in output:
				print(line)

			self.universal.save_to_txt("./"+str(self.league)+"/analyze/team_comparison/"+str(team1[1])+" - "+str(team2[1])+" analysis.txt", output)


	#calculates betting odds for all games being played today
	def calculate_odds_all_games(self):

		#gets games being played today
		games_queue = self.scraper.get_schedule()


		algo_version=self.get_algo_version()
		date=input("Date to test (M-D-YYY): ")
		year=input("Current season year: ")

		


		total_output=[]
		for x in range(0, len(games_queue)):
			print(games_queue[x])



			team1 = games_queue[x][0]
			team2 = games_queue[x][1]
			print()


			odds_calculator = Odds_Calculator(self.league)
			output=odds_calculator.team_comparison(algo_version, team1, team2, date, year)

			for line in output:
				total_output.append(line)
				print(line)
			total_output.append("")

			self.universal.save_to_txt("./"+str(self.league)+"/analyze/team_comparison/"+str(algo_version)+" "+str(team1[1])+" - "+str(team2[1])+" analysis.txt", output)

		self.universal.save_to_txt("./"+str(self.league)+"/analyze/team_comparison/"+str(algo_version)+" "+str(date)+" games analysis.txt", total_output)


	# def test_new_algo(self):
	# 	team1=["gs", "golden-state-warriors"]
	# 	team2=["lal", "los-angeles-lakers"]
	# 	date="3-7-2016"
	# 	cur_year="2016"


	# 	algo=Algo(self.league)

	# 	espn_scraper=ESPN_Scraper(self.league)

	# 	espn_scraper.update_data(team1, cur_year)
	# 	espn_scraper.update_data(team2, cur_year)
	# 	data1=self.universal.load_data(team1, date)
	# 	data2=self.universal.load_data(team2, date)

	# 	odds_calculator = Odds_Calculator(self.league)

	# 	returned1=odds_calculator.analyze2(team1, team2, data1, "away")
	# 	returned2=odds_calculator.analyze2(team2, team1, data2, "home")


	# 	algo.calculate_V2(date, returned1, returned2)





	def backtest(self):
		algo_version=self.get_algo_version()

		print("1) Backtest "+str(algo_version)+" and output to CSV")
		print("2) Backtests Algo_V2's odds vs oddsportal odds, and outputs to CSV")
		print("3) Backtest "+str(algo_version)+" stats")
		# print("3) Backtest "+str(algo_version)+" $")
		choice=int(input("Choice: "))
		print()

		if choice==1:
			#start-date should be the middle of the season
			#end-date should be right before the end, or at the end, of the season
			start_date=input("Start date: ")
			end_date=input("End date: ")
			print()

			backtester=Backtester(self.league, algo_version)
			backtester.backtest_csv_output(start_date, end_date)


		elif choice==2:
			#start-date should be the middle of the season
			#end-date should be right before the end, or at the end, of the season
			start_date=input("Start date: ")
			end_date=input("End date: ")
			print()

			backtester=Backtester(self.league, "Algo_V2")
			backtester.backtest_odds(start_date, end_date)


		#Should backtest Algo_V1 first, to get a feel of the points, then backtest V2 based off results of V1 backtest
		elif choice==3:

			# for x in range(1, 2, 1):
			# # 	for b in range(2, 12, 2):
			# # 		for c in range(2, 12, 2):
			# # 			for d in range(2, 12, 2):
			# # 				for e in range(2, 16, 2):
			# # 					for f in range(2, 16, 2):

			# 	if algo_version=="Algo_V1":
			# 		# algo=[10, 10, 5, 5, 8, 8, 3, 3]
			# 		algo=[1, -1, -1, -1, -1, -1, -1, -1]
			# 		# algo=[-1, -1, -1, -1, -1, -1, x/2, -1]
			# 	else:
			# 		algo=[0,0,0,0,0,0,0,0]

			# 	# algo=[-1, -1,-1, -1, -1, -1, -1, -1]
			# 	# algo=[0,0,0,0,0,0,0,0]

			# 	# algo=[a,b,c,d,e,f,-1,-1]

			# 	start_date="7-1-2003"
			# 	end_date="10-1-2015"

			# 	backtester=Backtester(self.league, algo_version)
			# 	backtester.backtest_algo(start_date, end_date, algo)

				# #index in algo list
				# for x in range(2, 8):

				# 	#part of algo
				# 	# for y in range(2, 7, 2):
				# 	for y in range(1, 2, 1):

				# 		algo=[-1, -1, -1, -1, -1, -1, -1, -1]
				# 		algo[x]=y

				# 		#start_date = middle os MLB season
				# 		#end_date = few days before end of MLB season
				# 		start_date="7-1-2003"
				# 		end_date="10-1-2015"

				# 		backtester=Backtester(self.league, algo_version)
				# 		backtester.backtest_algo(start_date, end_date, algo)


				start_date="7-1-2003"
				end_date="10-1-2015"

				backtester=Backtester(self.league, algo_version)
				backtester.backtest_algo(start_date, end_date, [-1, -1, -1, -1, -1, -1, 0.5, -1])

				# backtester=Backtester(self.league, algo_version)
				# backtester.backtest_algo(start_date, end_date, [-1, -1, 0.5, -1, -1, -1, -1, -1])

				# backtester=Backtester(self.league, algo_version)
				# backtester.backtest_algo(start_date, end_date, [-1, -1, -1, 0.5, -1, -1, -1, -1])

				# backtester=Backtester(self.league, algo_version)
				# backtester.backtest_algo(start_date, end_date, [-1, -1, -1, -1, 0.1, -1, -1, -1])

				# backtester=Backtester(self.league, algo_version)
				# backtester.backtest_algo(start_date, end_date, [-1, -1, -1, -1, -1, 0.5, -1, -1])

				# backtester=Backtester(self.league, algo_version)
				# backtester.backtest_algo(start_date, end_date, [-1, -1, 1, -1, -1, -1, -1, -1])

				# backtester=Backtester(self.league, algo_version)
				# backtester.backtest_algo(start_date, end_date, [-1, -1, -1, 1, -1, -1, -1, -1])

				# backtester=Backtester(self.league, algo_version)
				# backtester.backtest_algo(start_date, end_date, [-1, -1, -1, -1, 1, -1, -1, -1])

				# backtester=Backtester(self.league, algo_version)
				# backtester.backtest_algo(start_date, end_date, [-1, -1, -1, -1, -1, 1, -1, -1])

				# backtester=Backtester(self.league, algo_version)
				# backtester.backtest_algo(start_date, end_date, [-1, -1, -1, -1, -1, -1, 1, -1])

				# backtester=Backtester(self.league, algo_version)
				# backtester.backtest_algo(start_date, end_date, [-1, -1, -1, -1, -1, -1, -1, 1])


		# elif choice==4:

	def to_print(self, to_print):
		time=self.universal.get_current_time()

		to_print="["+str(time)+"] "+str(to_print)

		print(to_print)
		self.output.append(str(to_print))

	def save_output(self):
		self.universal.save_to_txt(self.output_path, self.output)




	def test(self):
		self.scraper.get_schedule()






if __name__=="__main__":

	# game="nba"
	leagues=["NBA", "NHL", "NFL", "MLB"]

	print("League")
	for x in range(0, len(leagues)):
		print(str(x+1)+") "+leagues[x])
	choice=int(input("Choice: "))
	print()
	league=leagues[choice-1].lower()

	sports_better = Sports_Better(league)
	print("Menu:")
	print("1) Single team analysis")
	print("2) Calculate game odds (Single Game)")
	print("3) Calculate game odds (ALL Games Today)")
	print("4) Backtest algorithm")
	print("5) Test schedule scraper")
	choice=int(input("Choice: "))
	print()

	#single team analysis
	if choice==1:
		sports_better.single_team_analysis()

	#compares 2 teams in a single game and calculates the odds
	elif choice==2:
		sports_better.calculate_odds_single_game()

	#gets all games being played today and calculates the odds
	elif choice==3:
		sports_better.calculate_odds_all_games()

	#backtests algorithm
	elif choice==4:
		sports_better.backtest()

	#temp testing for new algorithn
	elif choice==5:
		sports_better.test()

