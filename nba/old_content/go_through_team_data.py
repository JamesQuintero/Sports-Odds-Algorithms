import os
import csv

def read_from_csv(path):
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

def save_to_csv(path, data):
	with open(path, 'w', newline='') as file:
		contents = csv.writer(file)
		contents.writerows(data)



dir_list=os.listdir("./team_data/")


for x in range(0, len(dir_list)):
	file_list=os.listdir("./team_data/"+str(dir_list[x]))

	for y in range(0, len(file_list)):
		contents=read_from_csv("./team_data/"+str(dir_list[x])+"/"+str(file_list[y]))

		print(dir_list[x])
		print(file_list[y])
		z=0
		while z<len(contents):
			print(contents[z])

			contents[z][2]=contents[z][2].split(' ')[0].strip()
			contents[z][3]=contents[z][3].split(' ')[0].strip()

			if contents[z][4]=="0":
				contents.pop(z)
			else:
				z+=1
		# input()

		save_to_csv("./team_data/"+str(dir_list[x])+"/"+str(file_list[y]), contents)