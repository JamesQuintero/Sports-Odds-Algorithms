
# uses an algorithm to calculate sports betting odds


import urllib.request           #script for URL request handling
import urllib.parse             #script for URL handling
from urllib import request
import html.parser              #script for HTML handling
import os.path                  #script for directory/file handling
import csv                      #script for CSV file handling
import sys
from universal_functions import Universal_Functions


class Algo:

	#can be nba, nhl, nfl, mlb
	league="nba"

	universal=None


	algorithm={}
	



	def __init__(self, league):
		self.league=league

		self.algorithm['nba']=[10, 10, 5, 5,  8,  8,   3, 3]
		self.algorithm['nhl']=[10, 3,  3, 3, 0.5, 0.5, 3, 3]
		self.algorithm['mlb']=[10, 10, 5, 5,  8,  8,   3, 3]

		self.universal=Universal_Functions(league)


	#returns algo results
	def calculate(self, date, returned1, returned2):
		record_points             =self.calculate_points("seasonal_records",          returned1['seasonal_records'],         returned2['seasonal_records'])
		home_away_points          =self.calculate_points("home_away_records",         returned1['home_away_record'],         returned2['home_away_record'])
		home_away_10_games_points =self.calculate_points("home_away_10_game_records", returned1['home_away_record'],         returned2['home_away_record'])
		last_10_games_points      =self.calculate_points("last_10_games",             returned1['current_win_ratio'],        returned2['current_win_ratio'])
		avg_points                =self.calculate_points("avg_points",                returned1['avg_game_points'],          returned2['avg_game_points'])
		avg_points_10_games       =self.calculate_points("avg_points_10_games",       returned1['avg_game_points'],          returned2['avg_game_points'])
		win_streak                =self.calculate_points("win_streak",                returned1['win_loss_streaks_against'], returned2['win_loss_streaks_against'])
		win_streak_home_away      =self.calculate_points("win_streak_home_away",      returned1['win_loss_streaks_against'], returned2['win_loss_streaks_against'])


		# print(self.algorithm)

		#doesn't count variables if they're negative (for testing algorithms)
		if self.algorithm[self.league][0]<0:
			record_points=             0
		if self.algorithm[self.league][1]<0:
			home_away_points=          0
		if self.algorithm[self.league][2]<0:
			home_away_10_games_points= 0
		if self.algorithm[self.league][3]<0:
			last_10_games_points=      0
		if self.algorithm[self.league][4]<0:
			avg_points=                0
		if self.algorithm[self.league][5]<0:
			avg_points_10_games=       0
		if self.algorithm[self.league][6]<0:
			win_streak=                0
		if self.algorithm[self.league][7]<0:
			win_streak_home_away=      0



		record_points             /=    self.algorithm[self.league][0]
		home_away_points          /=    self.algorithm[self.league][1]
		home_away_10_games_points /=    self.algorithm[self.league][2]
		last_10_games_points      /=    self.algorithm[self.league][3]
		avg_points                /=    self.algorithm[self.league][4]
		avg_points_10_games       /=    self.algorithm[self.league][5]
		win_streak                /=    self.algorithm[self.league][6]
		win_streak_home_away      /=    self.algorithm[self.league][7]



		


		# record_points             /=    10
		# home_away_points          /=    5
		# home_away_10_games_points /=    4
		# last_10_games_points      /=    5
		# avg_points                /=    10
		# avg_points_10_games       /=    10
		# win_streak                /=    3
		# win_streak_home_away      /=    3



		total=record_points + home_away_points + home_away_10_games_points + last_10_games_points + avg_points + avg_points_10_games + win_streak + win_streak_home_away

		# #always has home team win
		# total=-1


		avg_points=self.universal.convert_number(avg_points)
		avg_points_10_games=self.universal.convert_number(avg_points_10_games)
		total=self.universal.convert_number(total)

		to_return={}
		to_return['record_points']=             record_points
		to_return['home_away_points']=          home_away_points
		to_return['home_away_10_games_points']= home_away_10_games_points
		to_return['last_10_games_points']=      last_10_games_points
		to_return['avg_points']=                avg_points
		to_return['avg_points_10_games']=       avg_points_10_games
		to_return['win_streak']=                win_streak
		to_return['win_streak_home_away']=      win_streak_home_away
		to_return['total']=                     total
		return to_return





	#calculates based off winning odds for every variable in algo
	#ALGO_V2
	def calculate_V2(self, date, returned1, returned2):
		record_points             =self.calculate_points("seasonal_records",          returned1['seasonal_records'],  returned2['seasonal_records'])
		home_away_points          =self.calculate_points("home_away_records",         returned1['home_away_record'],  returned2['home_away_record'])
		home_away_10_games_points =self.calculate_points("home_away_10_game_records", returned1['home_away_record'],  returned2['home_away_record'])
		last_10_games_points      =self.calculate_points("last_10_games",             returned1['current_win_ratio'], returned2['current_win_ratio'])
		avg_points                =self.calculate_points("avg_points",                returned1['avg_game_points'],   returned2['avg_game_points'])
		avg_points_10_games       =self.calculate_points("avg_points_10_games",       returned1['avg_game_points'],   returned2['avg_game_points'])
		# win_streak                =self.calculate_points("win_streak",                returned1['win_loss_streaks_against'], returned2['win_loss_streaks_against'])
		win_streak_home_away      =self.calculate_points("win_streak_home_away",      returned1['win_loss_streaks_against'], returned2['win_loss_streaks_against'])


		algo_vars=[]
		algo_vars.append(record_points)
		algo_vars.append(home_away_points)
		algo_vars.append(home_away_10_games_points)
		algo_vars.append(last_10_games_points)
		algo_vars.append(avg_points)
		algo_vars.append(avg_points_10_games)
		# algo_vars.append(win_streak)
		if self.league=="nhl":
			algo_vars.append(win_streak_home_away)


		print("Record points: "+str(record_points))
		print("Home away points: "+str(home_away_points))
		print("Home away 10 game points: "+str(home_away_10_games_points))
		print("Last 10 games: "+str(last_10_games_points))
		print("Avg points: "+str(avg_points))
		print("Avg points 10 games: "+str(avg_points_10_games))

		#new algo divides by 3 to fit it into a levels chart that has increments of 3. Let's skip the middle man and just divide by 9.


		if self.league=="nba":
			dividers=[]
			dividers.append(9)
			dividers.append(6)
			dividers.append(3)
			dividers.append(3)
			dividers.append(3)
			dividers.append(3)
			# dividers.append(1)
			# dividers.append(1)

			max_points=[]
			max_points.append(10)
			max_points.append(10)
			max_points.append(7)
			max_points.append(7)
			max_points.append(8)
			max_points.append(10)
			# max_points.append(10)
			# max_points.append(10)



			#puts total points at a max of 10
			for x in range(0, len(algo_vars)):
				algo_vars[x] /= dividers[x]

				if algo_vars[x]>max_points[x]:
					algo_vars[x]=max_points[x]
				elif algo_vars[x]<max_points[x]*-1:
					algo_vars[x]=-max_points[x]


			odds={}

			#calculates odds from records stat
			x=abs(algo_vars[0])
			y=-0.065*(x**2) + 5.4*x + 52.5
			y=self.universal.convert_number(y)
			odds['records']=y
			print("Records: "+str(y))

			#calculates odds from home_away stat
			x=abs(algo_vars[1])
			y=-0.42*(x**2) + 9*x + 50
			y=self.universal.convert_number(y)
			odds['home_away']=y
			print("Home away: "+str(y))

			#calculates odds from home_away_10_games stat
			x=abs(algo_vars[2])
			y=-0.34*(x**2) + 10*x + 41.3
			y=self.universal.convert_number(y)
			odds['home_away_10_games']=y
			print("Home away 10 games: "+str(y))

			#calculates odds from last_10_games stat
			x=abs(algo_vars[3])
			y=-0.39*(x**2) + 4.3*x + 51
			y=self.universal.convert_number(y)
			odds['last_10_games']=y
			print("Last 10 games: "+str(y))

			#calculates odds from avg_points stat
			x=abs(algo_vars[4])
			y=-0.44*(x**2) + 10.3*x + 44.2
			y=self.universal.convert_number(y)
			odds['avg_points']=y
			print("Avg points: "+str(y))

			#calculates odds from avg_points_10_games stat
			x=abs(algo_vars[5])
			y=-0.009*(x**2) + 4.9*x + 49
			y=self.universal.convert_number(y)
			odds['avg_points_10_games']=y
			print("Avg points 10 games: "+str(y))

		elif self.league=="nhl":
			dividers=[]
			dividers.append(3)
			dividers.append(3)
			dividers.append(3) # dividers.append(6)
			dividers.append(3)
			dividers.append(0.3) #is 3/10 since algo_v1 would *10 then /3, so *10/3 or /(3/10)
			dividers.append(0.6) #is 3/5 since algo_v1 would *5 then /3, so *5/3 or /(3/5)
			# dividers.append(1)
			dividers.append(6)

			max_points=[]
			max_points.append(10)
			max_points.append(10)
			max_points.append(7) # max_points.append(4)
			max_points.append(7)
			max_points.append(10)
			max_points.append(9)
			# max_points.append(0)
			max_points.append(7)

			#puts total points at a max of 10
			for x in range(0, len(algo_vars)):
				algo_vars[x] /= dividers[x]

				if algo_vars[x]>max_points[x]:
					algo_vars[x]=max_points[x]
				elif algo_vars[x]<max_points[x]*-1:
					algo_vars[x]=-max_points[x]


			odds={}

			#calculates odds from records stat
			x=abs(algo_vars[0])
			y=0.081*(x**2) + 0.41*x + 51.6
			y=self.universal.convert_number(y)
			odds['records']=y
			print("Records: "+str(y))

			#calculates odds from home_away stat
			x=abs(algo_vars[1])
			y= -0.16*(x**2) + 3.1*x + 49.6
			y=self.universal.convert_number(y)
			odds['home_away']=y
			print("Home away: "+str(y))

			#calculates odds from home_away_10_games stat
			x=abs(algo_vars[2])
			# y=4.26*x + 49.8
			y= -0.274*(x**2) + 4.4*x + 48
			y=self.universal.convert_number(y)
			odds['home_away_10_games']=y
			print("Home away 10 games: "+str(y))

			#calculates odds from last_10_games stat
			x=abs(algo_vars[3])
			y=0.64*(x**2) - 1.4*x + 53.93
			y=self.universal.convert_number(y)
			odds['last_10_games']=y
			print("Last 10 games: "+str(y))

			#calculates odds from avg_points stat
			x=abs(algo_vars[4])
			y=-0.21*(x**2) + 3.28*x + 49.9
			y=self.universal.convert_number(y)
			odds['avg_points']=y
			print("Avg points: "+str(y))

			#calculates odds from avg_points_10_games stat
			x=abs(algo_vars[5])
			y=0.69*(x**2) - 2.15*x + 54.1
			y=self.universal.convert_number(y)
			odds['avg_points_10_games']=y
			print("Avg points 10 games: "+str(y))

			#calculates odds from win_streak_home_away stat
			x=abs(algo_vars[6])
			y=-0.63*(x**3) + 7.76*(x**2) - 18.32*x + 65
			y=self.universal.convert_number(y)
			odds['win_streak_home_away']=y
			print("Win Streak Home Away: "+str(y))

			if odds['win_streak_home_away']<60:
				odds['win_streak_home_away']=50



		elif self.league=="mlb":
			dividers=[]
			dividers.append(6)
			dividers.append(6)
			dividers.append(3)
			dividers.append(3)
			dividers.append(0.3) #is 3/10 since algo_v1 would /0.1 or *10 then /3, so *10/3 or /(3/10) | or 0.1*3...
			dividers.append(1.5) #OR dividers.append(3)
			# dividers.append(1) DOESN'T MEAN SHIT
			# dividers.append(6) DOESN'T MEAN SHIT

			max_points=[]
			max_points.append(10)
			max_points.append(10)
			max_points.append(7)
			max_points.append(7)
			max_points.append(10)
			max_points.append(8) #OR max_points.append(4)
			# max_points.append(0)
			# max_points.append(7)

			#puts total points at a max of 10
			for x in range(0, len(algo_vars)):
				algo_vars[x] /= dividers[x]

				if algo_vars[x]>max_points[x]:
					algo_vars[x]=max_points[x]
				elif algo_vars[x]<max_points[x]*-1:
					algo_vars[x]=-max_points[x]


			odds={}

			#calculates odds from records stat
			x=abs(algo_vars[0])
			y=-0.0378*(x**2) + 1.5474*x + 50.776
			y=self.universal.convert_number(y)
			odds['records']=y
			print("Records: "+str(y))


			


			#calculates odds from home_away stat
			x=abs(algo_vars[1])
			y=-0.2226*(x**2) + 3.8472*x + 47.282
			y=self.universal.convert_number(y)
			odds['home_away']=y
			print("Home away: "+str(y))

			#calculates odds from home_away_10_games stat
			x=abs(algo_vars[2])
			y=0.3025*(x**2) + 1.4568*x + 49.518
			y=self.universal.convert_number(y)
			odds['home_away_10_games']=y
			print("Home away 10 games: "+str(y))

			#calculates odds from last_10_games stat
			x=abs(algo_vars[3])
			y=0.3039*(x**2) + 0.1154*x + 51.6
			y=self.universal.convert_number(y)
			odds['last_10_games']=y
			print("Last 10 games: "+str(y))

			#calculates odds from avg_points stat
			x=abs(algo_vars[4])
			y=-0.1938*(x**2) + 3.1638*x + 49.105
			y=self.universal.convert_number(y)
			
			odds['avg_points']=y
			print("Avg points: "+str(y))

			#calculates odds from avg_points_10_games stat
			x=abs(algo_vars[5])
			y=0.0301*(x**3) + 0.5611*(x**2) - 0.6103*x + 51.278
			y=self.universal.convert_number(y)
			odds['avg_points_10_games']=y
			print("Avg points 10 games: "+str(y))








		print("Odds home_away before: "+str(odds["home_away"]))

		#corrects percentages <50
		for key in odds.keys():
			#if -49% or something
			# if odds[key]<0 and odds[key]>-50:
			# 	odds[key]=(odds[key] + 100)
			# elif odds[key]>0 and odds[key]<50:
				# odds[key]=(odds[key] - 100)
			if(odds[key]<50):
				odds[key] = 50

		print("Odds home_away after: "+str(odds["home_away"]))

		#subtracts 50 since 50 is origin
		for key in odds.keys():
			odds[key]-=50

		print("Odds home_away after2: "+str(odds["home_away"]))

		#reverses odds so that all values that get plugged in stay above 50%
		# if a favorable team is unfavorable, the parabola algo might be a problem.
		if algo_vars[0]<0:
			odds['records']*=-1

		if algo_vars[1]<0:
			odds['home_away']*=-1

		if algo_vars[2]<0:
			odds['home_away_10_games']*=-1

		if algo_vars[3]<0:
			odds['last_10_games']*=-1

		if algo_vars[4]<0:
			odds['avg_points']*=-1

		if algo_vars[5]<0:
			odds['avg_points_10_games']*=-1

		if self.league=="nhl" and algo_vars[6]<0:
			odds['win_streak_home_away']*=-1

		print("Odds home_away after3: "+str(odds["home_away"]))

		#can also have average equal highest odds. Or average equals average between two highest odds. 



		## Averages two highest ##
		# #gets 2 highest odds even if one is opposite sign
		# highest=0
		# highest2=0
		# for key in odds.keys():
		# 	if abs(odds[key])>abs(highest):
		# 		if abs(highest)>abs(highest2):
		# 			highest2=highest
		# 		highest=odds[key]

		# 	elif abs(odds[key])>abs(highest2):
		# 		highest2=odds[key]
		# average=(highest+highest2)/2



		## adds all favorites, adds all underdogs, then averages the two totals ##
		# favorite_total=0
		# underdog_total=0
		# for key in odds:
		# 	if odds[key]>0:
		# 		favorite_total+=odds[key]
		# 	else:
		# 		underdog_total+=odds[key]
		# average=(favorite_total+underdog_total)/2


		# print()
		# #adds all favorites, adds all underdogs, then averages the two totals
		# away_total=0
		# home_total=0
		# for key in odds:
		# 	if odds[key]>0:
		# 		print(key+" pos: "+str(odds[key]/100))
		# 		away_total+=(odds[key]/100)
		# 	else:
		# 		print(key+" neg: "+str(odds[key]/100))
		# 		home_total+=(odds[key]/100)
		# print("away total: "+str(away_total))
		# print("home total: "+str(home_total))
		# average=(away_total+home_total)/len(odds.keys())
		# print("average: "+str(average))
		# average = average/2*100




		# print()
		# #adds all favorites, adds all underdogs, then averages the two totals
		# differences_total=0
		# for key in odds:
		# 	if odds[key]>0:
		# 		differences_total+=(odds[key] - (100-odds[key]))
		# 	else:
		# 		differences_total+=(odds[key] + (100 + odds[key]))
		# average=(differences_total)/len(odds.keys())
		# print("average: "+str(average))


		print()
		#adds all favorites, adds all underdogs, then averages the two totals
		total=0
		for key in odds:
			total+=odds[key]
		average=(total)/len(odds.keys())
		print("average: "+str(average))



		# print()




		if average>0:
			average+=50
		else:
			average-=50



		print("Favorite: "+str(average))

		for key in odds.keys():
			if odds[key]<0:
				odds[key]-=50
			else:
				odds[key]+=50




		to_return={}
		to_return['record_points']=             odds['records']
		to_return['home_away_points']=          odds['home_away']
		to_return['home_away_10_games_points']= odds['home_away_10_games']
		to_return['last_10_games_points']=      odds['last_10_games']
		to_return['avg_points']=                odds['avg_points']
		to_return['avg_points_10_games']=       odds['avg_points_10_games']
		# to_return['win_streak']=                win_streak
		if self.league=="nhl":
			to_return['win_streak_home_away']=      odds['win_streak_home_away']
		to_return['total']=                     self.universal.convert_number(average)
		return to_return



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

		elif calc_type=="win_streak":
			#if away team has win streak
			if returned1['games_since_last_loss']>0:
				points=int(returned1['games_since_last_loss']) - (int(returned2['games_since_last_win'])*-1)
			else:
				points=(int(returned1['games_since_last_win'])*-1) - int(returned2['games_since_last_loss'])

		elif calc_type=="win_streak_home_away":
			#if away team has win streak
			if returned1['games_since_last_loss_away']>0:
				points=int(returned1['games_since_last_loss_away']) - (int(returned2['games_since_last_win_home'])*-1)
			else:
				points=(int(returned1['games_since_last_win_away'])*-1) - int(returned2['games_since_last_loss_home'])



		return points