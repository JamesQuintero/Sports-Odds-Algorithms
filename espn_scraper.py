# scrapes espn.go.com for sports game data


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
import sqlite3
from universal_functions import Universal_Functions


class ESPN_Scraper:

	opener = None
	universal=None
	user_agents=[]

	output=[]
	output_path=""

	#can be nba, nhl, nfl, mlb
	league="nba"

	



	def __init__(self, league):
		self.league=league.lower()
		self.universal=Universal_Functions(league.lower())
		self.initialize_user_agents()


		self.output=[]
		today=self.universal.get_today()
		time=self.universal.get_current_time()
		#10:45 becomes 1045
		time = time.replace(":", "")
		self.output_path = "./"+league+"/output/espn_scraper_"+str(today['month'])+"-"+str(today['day'])+"-"+str(today['year'])+"_"+str(time)+".txt"
		self.output.append("---- Start output ----")






	def update_data(self, team, year):

		#scrapes all years worth of data
		if year=="":
			years=self.get_seasons(team)
			start=0
			end=len(years)
		#scrapes certain years worth fo data
		else:
			years=[year]
			start=0
			end=1


		for x in range(start, end):

			if self.league=="nhl":
				url="http://espn.com/"+str(self.league)+"/team/schedule/_/name/"+str(team[0])+"/year/"+str(years[x])+"/"+str(team[1])
				data=self.scrape_game_scores(url)
			elif self.league=="nba":
				#seasontype of 2 refers to regular season, while 1 and 3 refer to pre and post season respectively
				url="http://espn.go.com/"+str(self.league)+"/team/schedule/_/name/"+str(team[0])+"/year/"+str(years[x])+"/seasontype/2/"+str(team[1])
				data=self.scrape_game_scores(url)
			elif self.league=="mlb":
				#seasontype of 2 refers to regular season. MLB splits season into 2 halves
				url="http://espn.go.com/"+str(self.league)+"/team/schedule/_/name/"+str(team[0])+"/year/"+str(years[x])+"/seasontype/2/half/1/"+str(team[1])
				url2="http://espn.go.com/"+str(self.league)+"/team/schedule/_/name/"+str(team[0])+"/year/"+str(years[x])+"/seasontype/2/half/2/"+str(team[1])

				data=self.scrape_game_scores(url)
				data2=self.scrape_game_scores(url2)

				for y in range(0, len(data2['dates'])):
					data['dates'].append(data2['dates'][y])
					data['home_away'].append(data2['home_away'][y])
					data['game_urls'].append(data2['game_urls'][y])
					data['game_scores'].append(data2['game_scores'][y])


			path="./"+str(self.league)+"/team_data/"+str(years[x])+"/"+team[1]+".csv"


			self.to_print("Loading existing data")
			#gets proper season/year of data
			existing_data=self.universal.load_data(team, "", years[x])
			for y in range(0, len(existing_data)):
				if str(existing_data[y]['year'])==str(years[x]):
					existing_data=existing_data[y]
					break


			data['other_team']=[]
			data['period_scores']=[]

			for y in range(0, len(data['dates'])):

				#check if game data already scraped
				exists=False
				for z in range(0, len(existing_data['dates'])):
					if existing_data['dates'][z]==data['dates'][y]:
						exists=True
						break

				#if game data hasn't been scraped, scrape it and add it
				if exists==False:
					game_url=data['game_urls'][y]

					self.to_print("Returned "+str(data['dates'][y])+"'s game results")

					#goes to playbyplay page since it has the same info and loads more quickly
					game_period_url=game_url.replace("recap", "playbyplay")


					#scrapes for period score data
					self.to_print("Scraping "+str(data['dates'][y])+"'s period data: "+str(game_period_url))
					# time.sleep(1)
					period_data=self.scrape_period_data(team, url, game_period_url)
					other_team=period_data['other_team']
					period_scores=period_data['scores']
					if period_data['other_team']==-1:
						self.to_print("Scraping "+str(data['dates'][y])+"'s period data again")
						time.sleep(5)
						period_data=self.scrape_period_data(team, url, game_period_url)
						other_team=period_data['other_team']
						period_scores=period_data['scores']
					# other_team="lad"
					# period_scores=[[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]]



					#goes to boxscore page since it has the player's data for the game
					game_players_url=game_url.replace("recap", "boxscore")



					# #scrapes for players stats
					# player_stats=self.scrape_player_data(years[x], team, url, game_players_url)
					# if len(player_stats['away'])==0:
					# 	time.sleep(5)
					# 	self.scrape_player_data(years[x], team, url, game_players_url)

					# input("Pausing...")


					data['other_team'].append(other_team)
					# data['player_stats'].append(player_stats)
					data['game_scores'][y]=data['game_scores'][y].split("-")


					existing_data['dates'].append(data['dates'][y])
					existing_data['other_team'].append(other_team)
					existing_data['home_away'].append(data['home_away'][y])
					existing_data['game_scores'].append(data['game_scores'][y])
					existing_data['period_scores'].append(period_scores)

					self.save_output()



			to_save=[]
			for y in range(0, len(existing_data['game_scores'])):

				if existing_data['other_team'][y]!="" and existing_data['period_scores'][y][0][0]!=-1:
					score=existing_data['game_scores'][y]

					temp=[]
					temp.append(str(existing_data['dates'][y]))
					temp.append(existing_data['other_team'][y])
					temp.append(existing_data['home_away'][y])
					temp.append(score[0])
					temp.append(score[1])

					for period in existing_data['period_scores'][y][0]:
						temp.append(period)

					for period in existing_data['period_scores'][y][1]:
						temp.append(period)

					to_save.append(temp)

			
			self.to_print("Saving data to "+str(path))
			self.universal.save_to_csv(path, to_save)
		self.save_output()




	def update_player_data(self, team, year):
		#scrapes all years worth of data
		if year=="":
			years=self.get_seasons(team)
			start=0
			end=len(years)
		#scrapes certain years worth fo data
		else:
			years=[year]
			start=0
			end=1


		for x in range(start, end):
			url="http://espn.go.com/"+str(self.league)+"/team/schedule/_/name/"+str(team[0])+"/year/"+str(years[x])+"/"+str(team[1])
			path="./"+str(self.league)+"/team_data/"+str(years[x])+"/"+team[1]+".csv"
			print("Scraping: "+str(url))


			data=self.scrape_game_scores(url)


			data['other_team']=[]
			data['period_scores']=[]

			for y in range(0, len(data['dates'])):

				game_url=data['game_urls'][y]

				#goes to boxscore page since it has the player's data for the game
				game_players_url=game_url.replace("recap", "boxscore")



				#scrapes for players stats
				player_stats=self.scrape_player_data(years[x], team, url, game_players_url)
				if len(player_stats['away'])==0:
					time.sleep(5)
					self.scrape_player_data(years[x], team, url, game_players_url)




	#gets teams playing today
	def get_schedule(self):

		url="http://espn.go.com/"+str(self.league)+"/schedule"
		data=self.scrape_webpage(url)

		### OLD html ###
		# to_find="<caption>"

		# start=data.find(to_find)+len(to_find)
		# end=data[start:].find(to_find)
		

		to_start="<tbody>"
		to_end="</tbody>"

		start=data.find(to_start)+len(to_start)
		end=data[start:].find(to_end)

		new_data=data[start : start+end]


		abbrs = new_data.split("<abbr")
		abbrs.pop(0)

		teams=self.load_league_teams()


		games=[]
		temp=[]
		for x in range(0, len(abbrs)):
			start=abbrs[x].index('">')+2
			name_abbr=abbrs[x][start: abbrs[x].index("</abbr>") ].lower()

			full_team_name=[]
			for y in range(0, len(teams)):
				if teams[y][0]==name_abbr:
					full_team_name=teams[y]

			if x%2==0:
				temp.append(full_team_name)
			else:
				temp.append(full_team_name)
				games.append(temp)
				temp=[]



		return games



	#gets years for listed seasons on ESPN's website
	def get_seasons(self, team):
		url="http://espn.go.com/"+str(self.league)+"/team/schedule/_/name/"+str(team[0])
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
	#if new data, retrieve period scores and add all to global lists
	def scrape_game_scores(self, url):
		data={}
		data['dates']=[]
		data['home_away']=[]
		data['game_urls']=[]
		data['game_scores']=[]
		try:

			self.to_print("Scraping game scores from "+str(url))
			content=self.scrape_webpage(url)

			start=content.index("Regular Season Schedule")

			#espn has preseason stats for NHL teams, and that messes up the html
			if self.league=="nhl" and "preseason schedule" in content[start:].lower():
				end=content.index("Preseason Schedule")
			else:
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


					try:
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
					except Exception as error:
						exc_type, exc_obj, exc_tb = sys.exc_info()
						fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
						to_print=exc_type, fname, exc_tb.tb_lineno
						self.to_print("scrape_game_scores(), scraping date: "+str(to_print))

					# self.to_print("Date: "+str(date))
					# self.to_print("Old date: "+str(date))



					string_to_find='<li class="score"><a href="'
					# self.to_print("String to find: "+str(string_to_find))
					
					# print()
					game_link=temp[x][ temp[x].index(string_to_find)+len(string_to_find): ]

					score=game_link[ game_link.index('">')+2:game_link.index("</a>") ]

					# self.to_print("Score: "+str(score))

					#if lost game, switch score order since site always lists highest score first
					if lost:
						temp2=score.split("-")
						score=temp2[1]+"-"+temp2[0]


					#removes extra innings string "F/12" from scores
					temp2=score.split("-")
					temp2[0]=temp2[0].split(" ")
					temp2[0]=temp2[0][0]
					temp2[1]=temp2[1].split(" ")
					temp2[1]=temp2[1][0]
					score=temp2[0]+"-"+temp2[1]



					game_link=game_link[ :game_link.index('"') ]
					# game_link="http://espn.go.com"+game_link
					game_link="http:"+game_link


					data['dates'].append(old_date)
					data['game_urls'].append(game_link)
					data['game_scores'].append(score)
					data['home_away'].append(home_away)
					old_date=date


				except Exception as error:
					exc_type, exc_obj, exc_tb = sys.exc_info()
					fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
					to_print=exc_type, fname, exc_tb.tb_lineno
					self.to_print("scrape_game_scores(): "+str(to_print))
			return data
		except Exception as error:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			to_print=exc_type, fname, exc_tb.tb_lineno
			self.to_print("scrape_game_scores(): "+str(to_print))

			return data


	#gets a game's scores for each period
	def scrape_period_data(self, team, team_url, game_url):

		#espn uses old HTML code for nhl games
		if self.league=="nhl":
			print()
			data=self.scrape_webpage(game_url)

			print("Game url: "+str(game_url))
			# if data=="" or game_url=="http://espn.go.com":
			if data=="" or game_url=="http:":
				return {'other_team': -1, 'scores': [[-1,-1,-1], [-1,-1,-1]]}

			#gets teams playing in this game
			start=data.index("gameInfo:")
			end=data[start:].index(",")+start

			#now should have gameInfo:"nhl:game:gameid=400884409-ana+at+dal",
			# print(data[start:end])
			
			split = data[start:end].split("-")
			temp = split[1]
			#temp should now be ana+at+dal",
			split=temp.split("+")
			team1=split[0].replace('"', "")
			team2=split[2].replace('"', "")
			#team1 and team2 are the 3 letter abbreviations of teams EX: ana for anaheim-ducks
			print("Team1: "+str(team1)+" | Team2: "+str(team2))
			print("Cur team: "+str(team[0])+" | "+str(team[1]))
			if team1==team[0]:
				other_team=team2
			else:
				other_team=team1

			# input()


			# print(data)

			start=data.index('<table cellspacing="0" id="gp-linescore" class="linescore"  >')
			end=start+data[start:].index("</table>")

			new_data=data[start:end].replace("\n", "").replace("\t", "")
			

			#separates each game
			rows=new_data.split('<a href="')

			if len(rows)==2:
				#if first team listed is one with an old name
				if '<td class="team">' not in rows[1]:
					temp=rows[0].split('<td class="team">')
					temp.pop(0)
					temp.pop(0)
					temp.pop()

					rows[0]=temp[-1]
				#if second team listed is one with old name
				else:
					rows.pop(0)
					rows=rows[0].split('<td class="team">')
			else:
				rows.pop(0)


			for x in range(0, len(rows)):
				print(str(x)+" | "+str(rows[x]))




			scores=[]
			for row in rows:
				#separates each quarter
				quarters=row.split('text-align:center" >')

				temp=[]
				for quarter in quarters:
					score=quarter[ :quarter.index("</td>") ].strip()
					temp.append(score)
				scores.append(temp)

			#if team is listed 2nd, make it listed 1st for consistency
			#can't do last 2 characters because they could be in url even though not correct team. 5 guarenttes a / in test url for best comparison
			print("URL: "+str(team_url))
			print("Scores: "+str(scores))
			if len(scores)!=0:
				if team_url[-5:] in scores[1][0]:
					temp=scores[1]
					scores[1]=scores[0]
					scores[0]=temp

				scores[0].pop(0)
				scores[1].pop(0)

				#some games don't include a 3rd quarter
				while len(scores[0])<3:
					scores[0].append(0)
				while len(scores[1])<3:
					scores[1].append(0)


				to_return={}
				to_return['other_team']=other_team
				to_return['scores']=scores
				# return scores
				return to_return
			else:
				return {'other_team': "", 'scores': [[-1,-1,-1], [-1,-1,-1]]}


		elif self.league=="nba":
			data=self.scrape_webpage(game_url)

			print("Game url: "+str(game_url))
			if data=="":
				return {'other_team': -1, 'scores': [[0,0,0,0], [0,0,0,0]]}


			try:
				start=data.index('<div id="custom-nav"')
				end=data[start:].index('<div id="gamepackage-links-wrap">')+start
			except Exception as error:
				print("scrape_period_data.py" + str(error))
				return {'other_team': -1, 'scores': [[0,0,0,0], [0,0,0,0]]}

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
			

			#some games don't include a 4th period
			while len(scores[0])<4:
				scores[0].append(0)
			while len(scores[1])<4:
				scores[1].append(0)

			to_return={}
			to_return['other_team']=other_team
			to_return['scores']=scores
			# return scores
			return to_return

		# Baseball MLB
		elif self.league=="mlb":
			print()
			data=self.scrape_webpage(game_url)

			self.to_print("Game url: "+str(game_url))
			if data=="" or game_url=="http://espn.go.com" or game_url=="http://espn.go.com#":
				return {'other_team': -1, 'scores': [[-1,-1,-1,-1,-1,-1,-1,-1,-1], [-1,-1,-1,-1,-1,-1,-1,-1,-1]]}

			#gets teams playing in this game
			start=data.index("var omniPageName =")
			end=data[start:].index(";")+start
			
			#gets other team playing
			split=data[start:end].split("+")
			split.pop(0)
			split.pop(0)
			team1=split[0].replace('"', "")
			team2=split[2].replace('"', "")
			self.to_print("Team1: "+str(team1)+" | Team2: "+str(team2))
			self.to_print("Cur team: "+str(team[0])+" | "+str(team[1]))
			if team1==team[0]:
				other_team=team2
			else:
				other_team=team1
			# else:
				# return {'other_team': "", 'scores': [[-1,-1,-1-1,-1,-1,-1,-1,-1], [-1,-1,-1,-1,-1,-1,-1,-1,-1]]}

			self.to_print("Other team: "+str(other_team))




			#isolates period data html
			start=data.index('class="linescore"')
			end=start+data[start:].index("</table>")
			new_data=data[start:end].replace("\n", "").replace("\t", "")

			

			#separates each team
			rows=new_data.split('<a href="')
			if len(rows)==2:
				#if first team listed is one with an old name
				if '<td class="team" style="width: 3em !important">' not in rows[1]:
					temp=rows[0].split('<td class="team" style="width: 3em !important">')
					temp.pop(0)
					temp.pop(0)
					temp.pop()

					rows[0]=temp[-1]
				#if second team listed is one with old name
				else:
					rows.pop(0)
					rows=rows[0].split('<td class="team" style="width: 3em !important">')
			#removes column headers
			else:
				rows.pop(0)


			print()
			for x in range(0, len(rows)):
				print(str(x)+" | "+str(rows[x]))

			# input()



			scores=[]
			for row in rows:
				#separates each quarter
				quarters=row.split('text-align:center">')


				temp=[]
				for quarter in quarters:
					score=quarter[ :quarter.index("</td>") ].strip()
					temp.append(score)
				scores.append(temp)

			#if team is listed 2nd, make it listed 1st for consistency
			#can't do last 2 characters because they could be in url even though not correct team. 5 guarenttes a / in test url for best comparison
			self.to_print("URL: "+str(team_url))
			self.to_print("Scores: "+str(scores))
			# input()
			if len(scores)!=0 and len(scores[0])>1:
				#sorts scores to match teams
				if team_url[-5:] in scores[1][0]:
					temp=scores[1]
					scores[1]=scores[0]
					scores[0]=temp

				#remove urls from scores list
				scores[0].pop(0)
				scores[1].pop(0)

				#some games don't include a 3rd quarter
				while len(scores[0])<9:
					scores[0].append(0)
				while len(scores[1])<9:
					scores[1].append(0)

				#9th inning is "-" if team didn't have to go to bottom of the 9th
				if scores[0][-1]=="-":
					scores[0][-1]=0
				if scores[1][-1]=="-":
					scores[1][-1]=0



				to_return={}
				to_return['other_team']=other_team
				to_return['scores']=scores
				return to_return
			else:
				return {'other_team': "", 'scores': [[-1,-1,-1,-1,-1,-1,-1,-1,-1], [-1,-1,-1,-1,-1,-1,-1,-1,-1]]}
		


	
	def scrape_player_data(self, season, team, team_url, game_url):

		#espn uses old HTML code for nhl games
		# if self.league=="nhl":

		game_id=int(game_url.replace("http://espn.go.com/nba/boxscore?gameId=", "").replace("http://espn.go.com/nba/boxscore?id=", ""))

		data=self.scrape_webpage(game_url)

		print("Game url: "+str(game_url))
		if data=="" or game_url=="http://espn.go.com":
			return {'away': [], 'home': []}


		#gets first team listed
		start=data.index('<span class="team-name-short">')
		end=data[start:].index("</span>")+start
		first_team=data[start:end].lower()

		#gets second team listed
		start=data[end:].index('<span class="team-name-short">')+end
		end=data[start:].index("</span>")+start
		second_team=data[start:end].lower()
		



		#gets players playing in the game
		start=data.index('<article class="boxscore-tabs')
		end=start+data[start:].index("</article>")

		new_data=data[start:end]		

		#gets html for away team
		away_team=new_data[new_data.find('gamepackage-away-wrap">'): new_data.find('gamepackage-home-wrap">')]
		#gets html for home team
		home_team=new_data[new_data.find('gamepackage-home-wrap">'): ]



		away_player_stats=self.scrape_player_data2(away_team)
		home_player_stats=self.scrape_player_data2(home_team)


		#consolidates player stats
		player_ids=away_player_stats['player_ids']
		for player_id in home_player_stats['player_ids']:
			player_ids.append(player_id)
			print(player_id)
		player_stats=[]
		for stats in away_player_stats['player_stats']:
			player_stats.append(stats)
			player_stats[-1]['home_away']="away"
		for stats in home_player_stats['player_stats']:
			player_stats.append(stats)
			player_stats[-1]['home_away']="home"

		#add game_id
		#add season
		#add team
		#add home_away


		for x in range(0, len(player_ids)):

			#saves player data to sqlite file
			db = sqlite3.connect("./"+str(self.league)+"/player_data/"+str(player_ids[x])+".sqlite")
			cursor=db.cursor()

			try:
				cursor.execute('''CREATE TABLE "Games" (
					game_id TEXT PRIMARY KEY,
					season INTEGER, 
					home_away TEXT,
					pts INTEGER, 
					min INTEGER, 
					fg TEXT, 
					pt3 TEXT,
					ft TEXT,
					rb INTEGER,
					oreb INTEGER,
					dreb INTEGER,
					ast INTEGER,
					stl INTEGER,
					blk INTEGER,
					turn INTEGER,
					pf INTEGER
					)''')
				# print("Created table")
			except Exception as exception:
				# print("First exception")
				# print(exception)
				pass

			try:
				cursor.execute('''INSERT INTO "Games" (
				game_id, 
				season,
				home_away,
				pts, 
				min, 
				fg, 
				pt3,
				ft,
				rb,
				oreb,
				dreb,
				ast,
				stl,
				blk,
				turn,
				pf
				) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
				game_id,
				season,
				player_stats[x]['home_away'],
				player_stats[x]['points'],
				player_stats[x]['minutes_played'],
				player_stats[x]['field_goals'],
				player_stats[x]['three_pointers'],
				player_stats[x]['free_throws'],
				player_stats[x]['rebounds'],
				player_stats[x]['offensive_rebounds'],
				player_stats[x]['defensive_rebounds'],
				player_stats[x]['assists'],
				player_stats[x]['steals'],
				player_stats[x]['blocks'],
				player_stats[x]['turnovers'],
				player_stats[x]['personal_fouls'],
				))
				# print("Added data")
			except Exception as exception:
				pass
				# print("2nd exception")
				# print(exception)
					
			db.commit()
			db.close()


		to_return={}
		to_return['away']=away_player_stats
		to_return['home']=home_player_stats
		return to_return


	def scrape_player_data2(self, data):
		table=data.split('<tbody>')
		table.pop(0)


		starters=table[0]
		bench=table[1]

		starter_rows=starters.split("<tr>")
		starter_rows.pop(0)
		starter_rows.pop()

		bench_rows=bench.split("<tr")
		bench_rows.pop(0)
		bench_rows.pop()
		bench_rows.pop()




		player_ids=[]
		player_stats=[]

		starter_returned=self.scrape_player_data3(starter_rows)
		bench_returned=self.scrape_player_data3(bench_rows)


		for ids in starter_returned['player_ids']:
			player_ids.append(ids)

		for ids in bench_returned['player_ids']:
			player_ids.append(ids)

		for stats in starter_returned['player_stats']:
			player_stats.append(stats)

		for stats in bench_returned['player_stats']:
			player_stats.append(stats)

		# print()
		# for ids in player_ids:
		# 	print(ids)
		# for stat in player_stats:
		# 	print(stat)
		# print()

		to_return={}
		to_return['player_ids']=player_ids
		to_return['player_stats']=player_stats
		return to_return


	#scrapes player data from rows of players
	def scrape_player_data3(self, rows):

		player_ids=[]
		player_stats=[]
		for x in range(0, len(rows)):
			start=rows[x].find('href="')+len('href="')
			url=rows[x][ start: rows[x][start:].index('"')+start ]
			player_id=int(url.replace("http://espn.go.com/nba/player/_/id/", ""))
			player_ids.append(player_id)

			#fails if player didn't play
			try:
				player_data=rows[x].split("<td")
				player_data.pop(0)
				player_data.pop(0)

				stats={}
				stats['minutes_played']=int(player_data[0][ player_data[0].index(">")+1 : player_data[0].index("<") ])
				stats['field_goals']=player_data[1][ player_data[1].index(">")+1 : player_data[1].index("<") ]
				stats['three_pointers']=player_data[2][ player_data[2].index(">")+1 : player_data[2].index("<") ]
				stats['free_throws']=player_data[3][ player_data[3].index(">")+1 : player_data[3].index("<") ]
				stats['offensive_rebounds']=int(player_data[4][ player_data[4].index(">")+1 : player_data[4].index("<") ])
				stats['defensive_rebounds']=int(player_data[5][ player_data[5].index(">")+1 : player_data[5].index("<") ])
				stats['rebounds']=int(player_data[6][ player_data[6].index(">")+1 : player_data[6].index("<") ])
				stats['assists']=int(player_data[7][ player_data[7].index(">")+1 : player_data[7].index("<") ])
				stats['steals']=int(player_data[8][ player_data[8].index(">")+1 : player_data[8].index("<") ])
				stats['blocks']=int(player_data[9][ player_data[9].index(">")+1 : player_data[9].index("<") ])
				stats['turnovers']=int(player_data[10][ player_data[10].index(">")+1 : player_data[10].index("<") ])
				stats['personal_fouls']=int(player_data[11][ player_data[11].index(">")+1 : player_data[11].index("<") ])
				stats['points']=int(player_data[13][ player_data[13].index(">")+1 : player_data[13].index("<") ])
				player_stats.append(stats)
			except Exception as error:
				player_stats.append({'minutes_played': '0'})

			# print("Url: "+str(url)+" | Stats: "+str(stats))
		to_return={}
		to_return['player_ids']=player_ids
		to_return['player_stats']=player_stats
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

	def to_print(self, to_print):
		time=self.universal.get_current_time()

		to_print="["+str(time)+"] "+str(to_print)

		print(to_print)
		self.output.append(str(to_print))

	def save_output(self):
		self.universal.save_to_txt(self.output_path, self.output)

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











if __name__=="__main__":

	#### NHL ####
	espn_scraper = ESPN_Scraper("nhl")
	# espn_scraper.update_data(['ana','amaheim-ducks'], "2017")
	# espn_scraper.update_data(['ari','arizona-coyotes'], "2017")
	# espn_scraper.update_data(['bos','boston-bruins'], "2017")
	# espn_scraper.update_data(['buf','buffalo-sabres'], "2017")
	# espn_scraper.update_data(['cgy','calgary-flames'], "2017")
	# espn_scraper.update_data(['car','carolina-hurricanes'], "2017")
	# espn_scraper.update_data(['chi','chicago-blackhawks'], "2017")
	# espn_scraper.update_data(['col','colorado-avalanche'], "2017")
	# espn_scraper.update_data(['cbj','columbus-blue-jackets'], "2017")
	# espn_scraper.update_data(['dal','dallas-stars'], "2017")
	# espn_scraper.update_data(['det','detroit-red-wings'], "2017")
	# espn_scraper.update_data(['edm','edmonton-oilers'], "2017")
	# espn_scraper.update_data(['fla','florida-panthers'], "2017")
	# espn_scraper.update_data(['la','los-angeles-kings'], "2017")
	# espn_scraper.update_data(['min','minnesota-wild'], "2017")
	# espn_scraper.update_data(['mtl','montreal-canadiens'], "2017")
	espn_scraper.update_data(['nsh','nashville-predators'], "2017")
	# espn_scraper.update_data(['nj','new-jersey-devils'], "2017")
	# espn_scraper.update_data(['nyi','new-york-islanders'], "2017")
	# espn_scraper.update_data(['nyr','new-york-rangers'], "2017")
	# espn_scraper.update_data(['ott','ottawa-senators'], "2017")
	# espn_scraper.update_data(['phi','philadelphia-flyers'], "2017")
	# espn_scraper.update_data(['pit','pittsburgh-penguins'], "2017")
	# espn_scraper.update_data(['sj','san-jose-sharks'], "2017")
	# espn_scraper.update_data(['stl','st-louis-blues'], "2017")
	# espn_scraper.update_data(['tb','tampa-bay-lightning'], "2017")
	# espn_scraper.update_data(['tor','toronto-maple-leafs'], "2017")
	# espn_scraper.update_data(['van','vancouver-canucks'], "2017")
	# espn_scraper.update_data(['wsh','washington-capitals'], "2017")
	# espn_scraper.update_data(['wpg','winnipeg-jets'], "2017")

	#### MLB ####
	# espn_scraper = ESPN_Scraper("mlb")
	# espn_scraper.update_data(['ari','arizona-diamondbacks'], "2017")
	# espn_scraper.update_data(['atl','atlanta-braves'], "2017")
	# espn_scraper.update_data(['bal','baltimore-orioles'], "2017")
	# espn_scraper.update_data(['bos','boston-red-sox'], "2017")
	# espn_scraper.update_data(['chc','chicago-cubs'], "2017")
	# espn_scraper.update_data(['chw','chucago-white-sox'], "2017")
	# espn_scraper.update_data(['cin','cincinnati-reds'], "2017")
	# espn_scraper.update_data(['cle','cleveland-indians'], "2017")
	# espn_scraper.update_data(['col','colorado-rockies'], "2017")
	# espn_scraper.update_data(['det','detroit-tigers'], "2017")
	# espn_scraper.update_data(['hou','houston-astros'], "2017")
	# espn_scraper.update_data(['kc','kansas-city-royals'], "2017")
	# espn_scraper.update_data(['laa','los-angeles-angels'], "2017")
	# espn_scraper.update_data(['lad','los-angeles-dodgers'], "2017")
	# espn_scraper.update_data(['mia','miami-marlins'], "2017")
	# espn_scraper.update_data(['mil','milwaukee-brewers'], "2017")
	# espn_scraper.update_data(['min','minnesota-twins'], "2017")
	# espn_scraper.update_data(['nym','new-york-mets'], "2017")
	# espn_scraper.update_data(['nyy','new-york-yankees'], "2017")
	# espn_scraper.update_data(['oak','oakland-athletics'], "2017")
	# espn_scraper.update_data(['phi','philadelphia-phillies'], "2017")
	# espn_scraper.update_data(['pit','pittsburgh-pirates'], "2017")
	# espn_scraper.update_data(['sd','san-diego-padres'], "2017")
	# espn_scraper.update_data(['sf','san-francisco-giants'], "2017")
	# espn_scraper.update_data(['sea','seattle-mariners'], "2017")
	# espn_scraper.update_data(['stl','st.-louis-cardinals'], "2017")
	# espn_scraper.update_data(['tb','tampa-bay-rays'], "2017")
	# espn_scraper.update_data(['tex','texas-rangers'], "2017")
	# espn_scraper.update_data(['tor','toronto-blue-jays'], "2017")
	# espn_scraper.update_data(['wsh','washington-nationals'], "2017")


	# url="http://espn.go.com/mlb/team/schedule/_/name/laa/year/2016/seasontype/2/half/1/los-angeles-angels"
	# data=espn_scraper.scrape_game_scores(url)

	# for x in range(0, len(data['dates'])):
	# 	print("Date: "+data['dates'][x]+" | Score: "+data['game_scores'][x])


	# espn_scraper.scrape_period_data(['laa','los-angeles-angels'], "http://espn.go.com/mlb/team/schedule/_/name/laa/year/2016/half/1/los-angeles-angels", "http://espn.go.com/mlb/playbyplay?id=360404103")
	# espn_scraper.scrape_game_scores("http://espn.go.com/mlb/team/schedule/_/name/laa/year/2016/half/1/los-angeles-angels")
	# espn_scraper.scrape_game_scores("http://espn.go.com/nba/team/schedule/_/name/lal/year/2016/los-angeles-lakers")

	#### NBA ####
	# espn_scraper = ESPN_Scraper("nba")
	# espn_scraper.update_data(['atl','atlanta-hawks'], "2017")
	# espn_scraper.update_data(['bos','boston-celtics'], "2017")
	# espn_scraper.update_data(['bkn','brooklyn-nets'], "2017")
	# espn_scraper.update_data(['cha','charlotte-hornets'], "2017")
	# espn_scraper.update_data(['chi','chicago-bulls'], "2017")
	# espn_scraper.update_data(['cle','cleveland-cavaliers'], "2017")
	# espn_scraper.update_data(['dal','dallas-mavericks'], "2017")
	# espn_scraper.update_data(['den','denver-nuggets'], "2017")
	# espn_scraper.update_data(['det','detroit-pistons'], "2017")
	# espn_scraper.update_data(['gs','golden-state-warriors'], "2017")
	# espn_scraper.update_data(['hou','houston-rockets'], "2017")
	# espn_scraper.update_data(['ind','indiana-pacers'], "2017")
	# espn_scraper.update_data(['lac','los-angeles-clippers'], "2017")
	# espn_scraper.update_data(['lal','los-angeles-lakers'], "2017")
	# espn_scraper.update_data(['mem','memphis-grizzlies'], "2017")
	# espn_scraper.update_data(['mia','miami-heat'], "2017")
	# espn_scraper.update_data(['mil','milwaukee-bucks'], "2017")
	# espn_scraper.update_data(['min','minnesota-timberwolves'], "2017")
	# espn_scraper.update_data(['no','new-orleans-pelicans'], "2017")
	# espn_scraper.update_data(['ny','new-york-knicks'], "2017")
	# espn_scraper.update_data(['okc','oklahoma-city-thunder'], "2017")
	# espn_scraper.update_data(['orl','orlando-magic'], "2017")
	# espn_scraper.update_data(['phi','philadelphia-76ers'], "2017")
	# espn_scraper.update_data(['phx','phoenix-suns'], "2017")
	# espn_scraper.update_data(['por','portland-trail-blazers'], "2017")
	# espn_scraper.update_data(['sac','sacramento-kings'], "2017")
	# espn_scraper.update_data(['sa','san-antonio-spurs'], "2017")
	# espn_scraper.update_data(['tor','toronto-raptors'], "2017")
	# espn_scraper.update_data(['utah','utah-jazz'], "2017")
	# espn_scraper.update_data(['wsh','washington-wizards'], "2017")
	# espn_scraper.get_schedule()

	# scrape_player_data(self, team, team_url, game_url):

	# espn_scraper.scrape_player_data(2008, ["chi", "chicago-bulls"], "http://espn.go.com/nba/team/_/name/chi", "http://espn.go.com/nba/boxscore?id=280307002")

	# espn_scraper.update_player_data(['atl','atlanta-hawks'], "")
	# espn_scraper.update_player_data(['bos','boston-celtics'], "")
	# espn_scraper.update_player_data(['bkn','brooklyn-nets'], "")
	# espn_scraper.update_player_data(['cha','charlotte-hornets'], "")
	# espn_scraper.update_player_data(['chi','chicago-bulls'], "")
	# espn_scraper.update_player_data(['cle','cleveland-cavaliers'], "")
	# espn_scraper.update_player_data(['dal','dallas-mavericks'], "")
	# espn_scraper.update_player_data(['den','denver-nuggets'], "")
	# espn_scraper.update_player_data(['det','detroit-pistons'], "")
	# # espn_scraper.update_player_data(['gs','golden-state-warriors'], "")
	# espn_scraper.update_player_data(['hou','houston-rockets'], "")
	# espn_scraper.update_player_data(['ind','indiana-pacers'], "")
	# espn_scraper.update_player_data(['lac','los-angeles-clippers'], "")
	# espn_scraper.update_player_data(['lal','los-angeles-lakers'], "")
	# espn_scraper.update_player_data(['mem','memphis-grizzlies'], "")
	# espn_scraper.update_player_data(['mia','miami-heat'], "")
	# espn_scraper.update_player_data(['mil','milwaukee-bucks'], "")
	# espn_scraper.update_player_data(['min','minnesota-timberwolves'], "")
	# espn_scraper.update_player_data(['no','new-orleans-pelicans'], "")
	# espn_scraper.update_player_data(['ny','new-york-knicks'], "")
	# espn_scraper.update_player_data(['okc','oklahoma-city-thunder'], "")
	# espn_scraper.update_player_data(['orl','orlando-magic'], "")
	# espn_scraper.update_player_data(['phi','philadelphia-76ers'], "")
	# espn_scraper.update_player_data(['phx','phoenix-suns'], "")
	# espn_scraper.update_player_data(['por','portland-trail-blazers'], "")
	# espn_scraper.update_player_data(['sac','sacramento-kings'], "")
	# espn_scraper.update_player_data(['sa','san-antonio-spurs'], "")
	# espn_scraper.update_player_data(['tor','toronto-raptors'], "")
	# espn_scraper.update_player_data(['utah','utah-jazz'], "")
	# espn_scraper.update_player_data(['wsh','washington-wizards'], "")





