# global methods for the sports bettor program

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


class Universal_Functions:

	league_teams=[]

	#7 used from March to November
	#8 used from November to March
	daylight_savings=-7


	#can be nba, nhl, nfl, mlb
	league="nba"

	def __init__(self, league):
		self.league=league.lower()
		self.league_teams=self.load_league_teams()

	#loads all game data of specified team: ["lal", "los-angeles-lakers"]
	def load_data(self, team, end_date):
		# print("Loading data of "+str(team[1])+"...")

		to_return=[]
		reached_end=False

		years=os.listdir("./"+str(self.league)+"/team_data/")
		for x in range(0, len(years)):
			year=years[x]

			if os.path.isdir("./"+str(self.league)+"/team_data/"+year) and reached_end==False:
				path="./"+str(self.league)+"/team_data/"+year+"/"+team[1]+".csv"
				contents=self.read_from_csv(path)

				data={}
				data['year']=year
				data['dates']=[]
				data['other_team']=[]
				data['home_away']=[]
				data['game_scores']=[]
				data['period_scores']=[]
				for x in range(0, len(contents)):

					#newly scraped data has dates with format 2-23-16.
					#csv files modified and saved again as csvs have format 2/23/16
					#changes 2/23/16 to 2-23-16
					contents[x][0]=contents[x][0].replace("/", "-")

					#stops loading data if date is reached
					if contents[x][0]==end_date:
						reached_end=True
						break

					data['dates'].append(contents[x][0])
					data['other_team'].append(contents[x][1])
					data['home_away'].append(contents[x][2])
					data['game_scores'].append([ int(contents[x][3].split(" ")[0]) , int(contents[x][4].split(" ")[0]) ])

					#loads all quarter scores into single list
					temp=[]
					for item in contents[x][5:]:
						if item!="":
							if item=="-":
								item=0
							temp.append(int(item))

					#splits list in half to account for overtime quarters
					new_temp=[]
					while len(new_temp)<len(temp):
						new_temp.append(temp.pop())
					#because they were added on backwards
					new_temp.reverse()


					data['period_scores'].append([temp, new_temp])
				to_return.append(data)

		return to_return


	

	#gets games being played on specified date
	def get_games(self, date):

		folder_list=os.listdir("./"+str(self.league)+"/team_data")

		#gets year directory to traverse from checking date var
		year=""
		for folder in folder_list:
			if folder in date:
				year=folder


		team_files=os.listdir("./"+str(self.league)+"/team_data/"+year)


		games=[]
		for x in range(0, len(team_files)):

			team_name=team_files[x].replace(".csv", "")

			#gets full team name
			team=[]
			for y in range(0, len(self.league_teams)):
				if team_name==self.league_teams[y][1]:
					team=self.league_teams[y]

			# print(str(team)+" | "+str(team_name))
			if len(team)>0:

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
						for z in range(0, len(self.league_teams)):
							if data['other_team'][y]==self.league_teams[z][0]:
								other_team=self.league_teams[z]
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

	#returns odds for a game that can be found using the paramters
	def get_odds_game(self, year, away_team, home_team, game_scores):
		path="./"+str(self.league)+"/oddsportal_odds/odds_"+str(year)+".csv"
		if os.path.exists(path):

			string_game_score=str(game_scores[0])+"-"+str(game_scores[1])

			odds=self.read_from_csv(path)
			for x in range(0, len(odds)):
				if odds[x][0]==away_team[0] and odds[x][1]==home_team[0] and odds[x][2]==string_game_score:

					to_return=[int(odds[x][3]), int(odds[x][4])]
					return to_return
				# else:
				# 	print(str(odds[x][0])+":"+str(away_team[0])+" | "+str(odds[x][1])+":"+str(home_team[0])+" | "+str(odds[x][2])+":"+str(string_game_score))

			return [0,0]


	def scrape_webpage(self, url):

		user_agents=[]
		user_agents.append("Mozilla/5.0 (X10; Ubuntu; Linux x86_64; rv:25.0)")
		user_agents.append("Mozilla/5.0 (Windows NT 6.0; WOW64; rv:12.0)")
		user_agents.append("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537")
		user_agents.append("Mozilla/5.0 (Windows NT 6.1) AppleWebKit/540 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/540")
		user_agents.append("Mozilla/5.0 (Windows; U; Windows NT 5.2; it; rv:1.8.1.11) Gecko/20071327 Firefox/2.0.0.10")
		user_agents.append("Opera/9.3 (Windows NT 5.1; U; en)")

		#initializes url variables
		opener=urllib.request.build_opener(urllib.request.HTTPRedirectHandler(),urllib.request.HTTPHandler(debuglevel=0))
		opener.addheaders = [('User-agent', random.choice(user_agents))]

		try:
			response = opener.open(url, timeout=30)
			http_code=response.code
			info=response.info()

			data=response.read()
			data=data.decode('UTF-8', errors='ignore')

			#decode HTML
			h=html.parser.HTMLParser()
			data=h.unescape(data)

			return data
		except Exception as exception:
			print("scrape_webpage(): "+str(exception))
			return ""

	#loads list of league teams
	def load_league_teams(self):
		file_open=open('./'+str(self.league)+'/'+str(self.league)+'_teams.txt')

		teams=[]
		for line in file_open:
			temp=line.split("|")

			for x in range(0, len(temp)):
				temp[x]=temp[x].strip()

			teams.append(temp)

		return teams



	#returns time 14:45 for file naming purposes
	def get_current_time(self):
		#2013-12-15 17:45:35.177000
		curDate=str(datetime.datetime.utcnow() + datetime.timedelta(hours=self.daylight_savings))
		date=curDate.split(' ')

		#17:45:35.177000
		time=date[1].split(':')
		time[2]=time[2][ :time[2].index(".") ]

		#17:45
		new_time=str(time[0])+":"+str(time[1])+":"+str(time[2])
		return new_time

	#get today's date for file naming purposes
	def get_today(self):
		today=str(date.today()).split("-")

		to_return={}
		to_return['year']=int(today[0])
		to_return['month']=int(today[1])
		to_return['day']=int(today[2])
		return to_return


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