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


class NHL_Scraper:

	opener = None
	user_agents=[]
	

	# game_urls=[]
	# game_scores=[]
	# quarter_scores=[]
	# home_away=[]

	nhl_teams=[]
	data=[]



	team=[]



	def __init__(self):
		self.initialize_user_agents()

		self.reset()
		

	def reset(self):
		# self.game_urls=[]
		# self.game_scores=[]
		# self.quarter_scores=[]
		# self.home_away=[]

		self.data=[]



	def run(self, team):
		self.reset()
		self.team=team

		print("Menu")
		print("1) Load data")
		print("2) Update data")
		choice=int(input("Choice: "))

		if choice==1:
			self.load_data()
			self.analyze()
		elif choice==2:
			self.update_data()



		
	def analyze(self):

		data={}
		data['year']=""
		data['other_team']=[]
		data['home_away']=[]
		data['game_scores']=[]
		data['quarter_scores']=[]


		if os.path.isdir("./analyze/"+str(self.team[1]))==False:
			os.mkdir("./analyze/"+str(self.team[1]))





		#seasonal win-loss ratio
		records=self.get_seasonal_records()
		to_save=[]
		for x in range(0, len(records)):
			to_save.append(["1-1-"+str(self.data[x]['year']), records[x][0]-records[x][1]])
		self.save_to_csv("./analyze/"+str(self.team[1])+"/"+str(self.team[1])+"_seasonal_records.csv", to_save)

		
		#average point stats
		avg_points=self.get_avg_points()
		to_save=[]
		for x in range(0, len(avg_points['avg_game_points'])):
			to_add=[]
			to_add.append("1-1-"+str(self.data[x]['year']))
			to_add.append(avg_points['avg_game_points'][x])
			to_add.append(avg_points['avg_other_game_points'][x])
			to_add.append(avg_points['avg_game_points'][x]+avg_points['avg_other_game_points'][x])
			for y in range(0, len(avg_points['avg_quarter_points'][x])):
				to_add.append(avg_points['avg_quarter_points'][x][y])
			to_save.append(to_add)
		self.save_to_csv("./analyze/"+str(self.team[1])+"/"+str(self.team[1])+"_avg_game_points.csv", to_save)


		#stats in home vs away games
		home_away_records=self.get_home_away_record()
		to_save=[]
		for x in range(0, len(home_away_records['home_record'])):
			to_add=[]
			to_add.append("1-1-"+str(self.data[x]['year']))
			to_add.append(home_away_records['home_record'][x][0])
			to_add.append(home_away_records['home_record'][x][1])
			to_save.append(to_add)
		to_save.append(["","",""])
		to_save.append(["","",""])
		to_save.append(["","",""])
		for x in range(0, len(home_away_records['away_record'])):
			to_add=[]
			to_add.append("1-1-"+str(self.data[x]['year']))
			to_add.append(home_away_records['away_record'][x][0])
			to_add.append(home_away_records['away_record'][x][1])
			print(to_add)
			to_save.append(to_add)
		self.save_to_csv("./analyze/"+str(self.team[1])+"/"+str(self.team[1])+"_home_away_record.csv", to_save)


		#seasonal win-loss ratio
		win_loss=self.get_current_win_ratio()
		self.save_to_csv("./analyze/"+str(self.team[1])+"/"+str(self.team[1])+"_current_win_ratio.csv", win_loss)


		last_10_games=self.analyze_10_games_win_ratio()
		to_save=[]
		to_save.append(["Year", "win-loss", "num wins", "num games"])
		for x in range(0, len(last_10_games)):


			for y in range(-10, 11, 2):
				to_add=[]
				#only has year at beginning of listing
				if y==-10:
					to_add.append(self.data[x]['year'])
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
		self.save_to_csv("./analyze/"+str(self.team[1])+"/"+str(self.team[1])+"_10_game_win_ratio.csv", to_save)









		home_away=input("Are they home or away: ").lower()

		to_output=[]
		to_output.append("")
		to_output.append("")
		# print("Analysis:")
		to_output.append(self.team[1])

		if (records[-1][0]-records[-1][1])>(records[-2][0]-records[-2][1]):
			temp="uptrend"
		else:
			temp="downtrend"
		to_output.append("Season: "+str(records[-1][0]-records[-1][1])+" on "+str(temp))

		if home_away=="away":
			to_output.append("Home-Away: "+str(home_away_records['away_record'][-1][0])+"-"+str(home_away_records['away_record'][-1][1])+" away")
			to_output.append("   Last 10 away games: "+str(home_away_records['away_10_games'][-1][0])+"-"+str(home_away_records['away_10_games'][-1][1]))
		elif home_away=="home":
			to_output.append("Home-Away: "+str(home_away_records['home_record'][-1][0])+"-"+str(home_away_records['home_record'][-1][1])+" home")
			to_output.append("   Last 10 home games: "+str(home_away_records['home_10_games'][-1][0])+"-"+str(home_away_records['home_10_games'][-1][1]))
		# to_output.append("Last 10 games: ")


		win_10_games=0
		for x in range(len(win_loss)-1, len(win_loss)-11, -1):
			win_10_games+=win_loss[x][2]

		temp={'-10': '0-10', '-8': '1-9', '-6': '2-8', '-4': '3-7', '-2': '4-6', '0': '5-5', '2': '6-4', '4': '7-3', '6': '8-2', '8': '9-1', '10': '10-0'}
		to_output.append("10 Games: "+temp[str(win_10_games)])
		won=last_10_games[-1][str(win_10_games)][0]
		# print(win_10_games)
		num_games=last_10_games[-1][str(win_10_games)][1]
		if num_games!=0:
			to_output.append("   "+str(won)+" won out of "+str(num_games)+" games | "+str(won/num_games*100)+"%")
		else:
			to_output.append("   "+str(won)+" won out of "+str(num_games)+" games | N/A%")


		to_output.append("Avg points: "+str(avg_points['avg_game_points'][-1])+" - "+str(avg_points['avg_other_game_points'][-1]))
		to_output.append("   Last 10 games: "+str(avg_points['avg_10_games'][-1])+" - "+str(avg_points['avg_other_10_games'][-1]))


		for x in range(0, len(to_output)):
			print(to_output[x])

		self.save_to_txt("./analyze/"+str(self.team[1])+"/"+str(self.team[1])+"_analysis.txt", to_output)





	#determines whether teams win or lose more often if they have a good or bad last 10 games
	def analyze_10_games_win_ratio(self):

		to_return=[]
		for x in range(0, len(self.data)):
			data=self.data[x]


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
	def get_current_win_ratio(self):

		data=self.data[-1]
		# data=self.data[0]

		to_return=[]
		cur_score=0
		for x in range(0, len(data['game_scores'])):
			to_add=[]
			to_add.append(data['game_scores'][x][0])
			to_add.append(data['game_scores'][x][1])
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
	def get_home_away_record(self):

		to_return={}
		to_return['home_record']=[]
		to_return['away_record']=[]
		to_return['home_10_games']=[]
		to_return['away_10_games']=[]
		for x in range(0, len(self.data)):
			data=self.data[x]


			home_away=data['home_away']
			game_scores=data['game_scores']

			# home_record=[0,0]
			# away_record=[0,0]
			# home_10_games=[0,0]
			# away_10_games=[0,0]
			# for y in range(0, len(home_away)):

			# 	if home_away[y]=="home":
			# 		if game_scores[y][0]>game_scores[y][1]:
			# 			home_record[0]+=1
			# 		else:
			# 			home_record[1]+=1
			# 	elif home_away[y]=="away":
			# 		if game_scores[y][0]>game_scores[y][1]:
			# 			away_record[0]+=1
			# 		else:
			# 			away_record[1]+=1
			# to_return['home_record'].append(home_record)
			# to_return['away_record'].append(away_record)

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
	def get_avg_points(self):

		to_return={}


		avg_game_points=[]
		avg_other_game_points=[]
		avg_10_games=[]
		avg_other_10_games=[]
		avg_quarters=[]
		for x in range(0, len(self.data)):
			data=self.data[x]
			print("Year: "+str(self.data[x]['year']))

			if len(data['other_team'])!=0:

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
				total_quarters=[0]*6
				for y in range(0, len(data['other_team'])):
					# print(data['quarter_scores'][y])
					#adds current team's 3 quarters
					for z in range(0, 3):
						total_quarters[z]+=int(data['quarter_scores'][y][0][z])
					#adds other team's 3 quarters
					for z in range(0,3):
						total_quarters[z+3]+=int(data['quarter_scores'][y][1][z])
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
	def get_seasonal_records(self):
		records=[]
		for x in range(0, len(self.data)):
			data=self.data[x]

			num_wins=0
			for y in range(0, len(data['other_team'])):
				if data['game_scores'][y][0]>data['game_scores'][y][1]:
					num_wins+=1

			# record=num_wins-len(data['game_scores'])-num_wins
			record=[num_wins, len(data['game_scores'])-num_wins]
			records.append(record)

		return records




	def update_data(self):
		years=self.get_seasons()


		# for x in range(0, len(years)):
		start=0
		end=len(years)

		# if self.team[0]=="van":
		# 	start=len(years)-1
		# 	end=len(years)

		for x in range(start, end):
			url="http://espn.go.com/nhl/team/schedule/_/name/"+str(self.team[0])+"/year/"+str(years[x])+"/"+str(self.team[1])
			# url="http://"+str(self.team[0])+".nhl.com/club/gamelog.htm?season="+str(self.seasons[x])
			path="./team_data/"+str(years[x])+"/"+str(self.team[1])+".csv"
			print("URL: "+str(url))
			print("PATH: "+str(path))

			# input()


			# print(os.listdir("./team_data/2003/"))


			if os.path.isfile(path)==False:
				data=self.scrape_game_scores(url)

				data['year']=years[x]
				data['other_team']=[]
				data['quarter_scores']=[]


				for game_url in data['game_urls']:
					time.sleep(1)
					quarter_data=self.scrape_quarter_data(url, game_url)
					other_team=quarter_data['other_team']
					quarter_scores=quarter_data['scores']
					if quarter_scores[0][0]==-1:
						time.sleep(5)
						quarter_data=self.scrape_quarter_data(url, game_url)
						other_team=quarter_data['other_team']
						quarter_scores=quarter_data['scores']

					# if quarter_scores[0][0]!=-1:
					data['other_team'].append(other_team)
					data['quarter_scores'].append(quarter_scores)

				print(len(data['other_team']))
				print(len(data['home_away']))


				to_save=[]
				for y in range(0, len(data['game_scores'])):
					score=data['game_scores'][y].split("-")

					# print(y)
					if data['quarter_scores'][y][0][0]!=-1:

						temp=[]
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



	#loads all game data
	def load_data(self):
		self.data=[]

		years=os.listdir("./team_data/")
		for x in range(0, len(years)):
			year=years[x]
			print(year)

			if os.path.isdir("./team_data/"+year):
				path="./team_data/"+year+"/"+self.team[1]+".csv"
				contents=self.read_from_csv(path)

				data={}
				data['year']=year
				data['other_team']=[]
				data['home_away']=[]
				data['game_scores']=[]
				data['quarter_scores']=[]
				for x in range(0, len(contents)):
					# self.game_urls.append("")

					data['other_team'].append(contents[x][0])
					data['home_away'].append(contents[x][1])
					# print(str(contents[x][2])+" | "+str(contents[x][3]))
					# data['game_scores'].append([ int(contents[x][2].replace("OT", "").strip()), int(contents[x][3].replace("OT", "").strip())])
					data['game_scores'].append([ int(contents[x][2].split(" ")[0]) , int(contents[x][3].split(" ")[0]) ])

					#loads all quarter scores into single list
					# print(str(contents[x]))
					temp=[]
					for item in contents[x][4:]:
						if item!="":
							temp.append(int(item))

					#splits list in half to account for overtime quarters
					new_temp=[]
					while len(new_temp)<len(temp):
						new_temp.append(temp.pop())

					data['quarter_scores'].append([temp, new_temp])

					# print(str(self.home_away[-1])+" | "+str(self.game_scores[-1])+" | "+str(self.quarter_scores[-1]))

				self.data.append(data)

		for x in range(0, len(self.data)):
			year=self.data[x]['year']
			other_teams=self.data[x]['other_team']
			home_away=self.data[x]['home_away']

			print("Year: "+str(year))
			for y in range(0, len(other_teams)):
				print("  Other team: "+str(other_teams[y])+" | "+str(home_away[y]))
			print()



	#gets years for listed seasons on ESPN's website
	def get_seasons(self):
		url="http://espn.go.com/nhl/team/schedule/_/name/"+str(self.team[0])
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
		data['home_away']=[]
		data['game_urls']=[]
		data['game_scores']=[]
		data['quarter_scores']=[]


		content=self.scrape_webpage(url)

		# print(content)
		# input()

		try:
			start=content.index("Regular Season Schedule")
			# end=content.index("<!-- begin sponsored links -->")
			end=content.index("Preseason Schedule")

			new_data=content[start:end]


			#separates each game
			temp=new_data.split('<li class="team-name">')

			#gets scores and game urls for better scores
			for x in range(0, len(temp)):
			# for x in range(0, 5):
				# print(temp[x])
				# print()
				try:
					#if lost game
					lost="game-status loss" in temp[x]

					#determines whether game was at home or away
					if "@" in temp[x-1]:
						home_away="away"
					else:
						home_away="home"

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

					# self.game_urls.append(game_link)
					# self.game_scores.append(score)
					# self.home_away.append(home_away)
					data['game_urls'].append(game_link)
					data['game_scores'].append(score)
					data['home_away'].append(home_away)
				except Exception as error:
					pass
			return data
		except Exception as error:
			print(error)

			return data


	#gets a game's scores for each quarter
	def scrape_quarter_data(self, team_url, game_url):
		print()
		data=self.scrape_webpage(game_url)

		print("Game url: "+str(game_url))
		if data=="" or game_url=="http://espn.go.com":
			return {'other_team': "", 'scores': [[-1,-1,-1], [-1,-1,-1]]}

		#gets teams playing in this game
		start=data.index("var omniPageName =")
		end=data[start:].index(";")+start
		# print(data[start:end])
		
		split=data[start:end].split("+")
		split.pop(0)
		split.pop(0)
		team1=split[0].replace('"', "")
		team2=split[2].replace('"', "")
		print("Team1: "+str(team1)+" | Team2: "+str(team2))
		print("Cur team: "+str(self.team[0])+" | "+str(self.team[1]))
		if team1==self.team[0]:
			other_team=team2
		else:
			other_team=team1


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





	#gets rid of HTML encoded parts of the url
	def clean_url(self, url):
		#adds http://
		if "https://" not in url and "http://" not in url:
			url="http://"+url

		
		url=urllib.parse.unquote(url)

		return url

	#separates url variable into http, url, uri parts
	def get_url_data(self, url):
		url=self.clean_url(url)

		#temporarily removes http:// stuff
		http=False
		https=False
		if "http://" in url:
			url=url.replace("http://", "")
			http=True
		elif "https://" in url:
			url=url.replace("https://", "")
			https=True
		
		
		temp=url.split("/")
		uri=""

		#gets uri if it has it
		if "?" in temp[0]:
			temp=temp[0].split("?")
			uri="?".join(temp[1:])

		to_return={}
		to_return['http']=""
		to_return['url']=temp[0]
		to_return['uri']=uri

		if http:
			to_return['http']="http"
		elif https:
			to_return['http']="https"

		return to_return


	def initialize_user_agents(self):
		self.user_agents.append("Mozilla/5.0 (X10; Ubuntu; Linux x86_64; rv:25.0)")
		self.user_agents.append("Mozilla/5.0 (Windows NT 6.0; WOW64; rv:12.0)")
		self.user_agents.append("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537")
		self.user_agents.append("Mozilla/5.0 (Windows NT 6.1) AppleWebKit/540 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/540")
		self.user_agents.append("Mozilla/5.0 (Windows; U; Windows NT 5.2; it; rv:1.8.1.11) Gecko/20071327 Firefox/2.0.0.10")
		self.user_agents.append("Opera/9.3 (Windows NT 5.1; U; en)")
		self.opener=urllib.request.build_opener(urllib.request.HTTPRedirectHandler(),urllib.request.HTTPHandler(debuglevel=0))
		#picks random user agent for each running of program
		self.opener.addheaders = [('User-agent', random.choice(self.user_agents))]

	#loads list of nhl teams
	def load_nhl_teams(self):
		file_open=open('./nhl_teams.txt')

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
	nhl_scraper = NHL_Scraper()


	nhl_teams=nhl_scraper.load_nhl_teams()
	print("NHL teams:")
	for x in range(0, len(nhl_teams)):
		print(str(x)+": "+nhl_teams[x][1])
	choice = int(input("Choice: "))

	print(nhl_teams[choice])
	nhl_scraper.run(nhl_teams[choice])

	# choice=int(input("Choice: "))


	# if choice==1:
	# 	for x in range(0, int(len(nhl_teams)/4)):
	# 		nhl_scraper.run(nhl_teams[x])

	# if choice==2:
	# 	for x in range(int(len(nhl_teams)/4*1), int(len(nhl_teams)/4*2)):
	# 		nhl_scraper.run(nhl_teams[x])

	# if choice==3:
	# 	for x in range(int(len(nhl_teams)/4*2), int(len(nhl_teams)/4*3)):
	# 		nhl_scraper.run(nhl_teams[x])

	# if choice==4:
	# 	for x in range(int(len(nhl_teams)/4*3), int(len(nhl_teams))):
	# 		nhl_scraper.run(nhl_teams[x])


















