#http://www.oddsportal.com/basketball/usa/nba/results/#/page/11/
# scrapes Oddsportal.com for betting odds data

import os.path                  #script for directory/file handling
import time                     #scripting timing handling
import sys
from universal_functions import Universal_Functions


class Odds_Portal_Scraper:

	#can be nba, nhl, nfl, mlb
	league="nba"


	def __init__(self, league):
		self.league=league.lower()
		self.universal=Universal_Functions(self.league)

		self.league_teams=self.universal.load_league_teams()





	def scrape_historical_odds(self):

		season_urls=self.get_seasons(self.league)


		for x in range(0, len(season_urls)):
		# x=0

			try:
				#http://www.oddsportal.com/hockey/usa/nhl-2015-2016/results/
				if self.league=="nba" or self.league=="nhl":
					season_year=season_urls[x].split("-")[2].split("/")[0]
				#http://www.oddsportal.com/baseball/usa/mlb-2015/results/
				else:
					season_year=season_urls[x].split("-")[1].split("/")[0]
			except Exception as error:
				print("Invalid season: "+season_urls[x])
				continue


			print("Season year: "+str(season_year))
			path="./"+str(self.league)+"/oddsportal_odds/odds_"+str(season_year)+".csv"
			if os.path.exists(path)==False:

				#gets Page ID needed for url
				data=self.universal.scrape_webpage(season_urls[x])
				#if page timed out
				if data=="":
					time.sleep(10)
					data=self.universal.scrape_webpage(season_urls[x])

				to_find='new PageTournament({"id":"'
				start=data.find(to_find)+len(to_find)
				page_id=data[start : start+data[start:].find('"')]
				print("Season url: "+str(season_urls[x]))



				page_num=1
				to_save=[]
				#will break once last page is reached
				while True:
					url="http://fb.oddsportal.com/ajax-sport-country-tournament-archive/3/"+str(page_id)+"/X0/1/0/"+str(page_num)+"/"
					print("Url: "+str(url))

					headers=[('Referer', season_urls[x])]
					data=self.universal.scrape_webpage(url, headers)
					#if page timed out
					if data=="":
						time.sleep(10)
						data=self.universal.scrape_webpage(url)



					#removes unnecessary data
					data=data.replace("\\", "")
					data=data.split('{"html":"')[1]

					#splits games
					split=data.split("table-participant")[1:]

					
					for y in range(0, len(split)):
						# print(split[year])

						try:
							#game is in progress, so don't get odds
							if "in-play" not in split[y] and "inplay" not in split[y] and "play offs" not in split[y].lower():

								row=[]

								#gets teams
								if "/"+self.league+"/" in split[x]:
									start=split[y].find("/"+self.league+"/")+len("/"+self.league+"/")
									end=split[y].find('/"')
									teams=split[y][start:end]
								else:
									to_find="/"+self.league
									start=split[y].find(to_find)+len(to_find)
									start=start+split[y][start:].find("/")+1
									end=start+split[y][start:].find('/"')
									teams=split[y][start:end]

								
								temp_team=teams.split("-")
								temp_team.pop()
								teams="-".join(temp_team)

								# print("    Teams: "+str(teams))

								home_team=[]
								away_team=[]
								for z in range(0, len(self.league_teams)):
									#if team is in game
									if self.league_teams[z][1] in teams:
										#first team listed is home team for some reason
										if teams.index(self.league_teams[z][1])==0:
											home_team=self.league_teams[z]
										else:
											away_team=self.league_teams[z]

								# print("    Home team: "+str(home_team))
								# print("    Away team: "+str(away_team))

								row.append(away_team[0])
								row.append(home_team[0])


								#gets score
								to_find='table-score">'
								start=split[y].find(to_find)+len(to_find)
								score=split[y][ start: start+split[y][start:].find("</td>")]
								#remove OT
								score=score.replace("\xa0OT", "")
								score=score.split(":")
								# print("Score: "+str(score))

								row.append(score[1]+"-"+score[0])


								#gets odds
								to_find='xodd="'
								start=split[y].find(to_find)+len(to_find)
								end=split[y][start:].find('"')+start
								odds_home=self.decode(split[y][start:end])

								to_find='xodd="'
								temp=split[y][end:]
								start=temp.find(to_find)+len(to_find)
								end=temp[start:].find('"')+start
								odds_away=self.decode(temp[start:end])

								# print("   Home odds: "+str(odds_home))
								# print("   Away odds: "+str(odds_away))

								row.append(odds_away)
								row.append(odds_home)
							
								to_save.append(row)

						except Exception as error:
							print(error)
						
					if len(split)<=1:
						break
					else:
						page_num+=1
						

				if len(to_save)>0:
					path="./"+str(self.league)+"/oddsportal_odds/odds_"+str(season_year)+".csv"
					print(path+" | "+self.league+" | "+str(season_year))
					self.universal.save_to_csv(path, to_save)
				else:
					print("Not enough data to save "+str(season_year))



	def decode(self, odds):
		new_string=odds.replace("a", "1").replace("x", "2").replace("c", "3").replace("t", "4").replace("e", "5").replace("o", "6").replace("p", "7").replace("z", '.').replace("f", '|')

		split=new_string.split("|")
		# print("Format: "+str(formatUS(float(split[0])))+" | "+str(formatUS(float(split[1]))))
		return self.formatUS(float(split[1]))

	def formatUS(self, number):
		if (number >= 2):
			return int((number - 1) * 100)
		elif (number != 1):
			return -int(100 / (number - 1))
		else:
			return 0


			






	#gets years for listed seasons on ESPN's website
	def get_seasons(self, league):

		if league=="nba":
			url="http://www.oddsportal.com/basketball/usa/nba/results/"
		elif league=="nhl":
			url="http://www.oddsportal.com/hockey/usa/nhl/results/"
		elif league=="mlb":
			url="http://www.oddsportal.com/baseball/usa/mlb/results/"


		data=self.universal.scrape_webpage(url)

		start=data.index("<!-- PAGE BODY -->")
		end=data[start:].index("<!--  END PAGE BODY -->")

		new_data=data[start : start+end]

		# print(new_data)
		split=new_data.split('<strong><a href="')
		#removes excess form data
		for x in range(0, 5):
			split.pop(0)


		#retrieves season's year from URL in select HTML element
		to_return=[]
		for item in split:
			url=item[:item.find('"')]

			url="http://www.oddsportal.com"+str(url)
			print(url)

			to_return.append(url)

		return to_return




if __name__=="__main__":
	odds_portal_scraper = Odds_Portal_Scraper("mlb")

	odds_portal_scraper.scrape_historical_odds()
	# seasons = odds_portal_scraper.get_seasons()

	# for x in range(0, len(seasons)):
	# 	print(str(x)+" | "+str(seasons[x]))




