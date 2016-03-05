import cv2
import numpy as np
import json
import glob, os
import random, math, statistics
#circles should not be very thick nor very thin, 2px is ideal
#distance from left to first circle is around 13, radius is 8-9, dist btw 2 circles is 6
#distance btw circle in first row and second row is 18

path = "/home/neel/opencvproject/"
#USN = "1pi12cs106" #run eliminate and isrowEmpty for this
#USN = "1pi12cs105" #run add points and isrowEmpty for this
USN = "1pi12cs104"
#USN = "1pi12cs108"
#USN = "1pi12cs107"
#USN = "testimages" #works

'''read the naming convention from a configuration file which is a json file for the purpose of naming the image file'''
def namingConvention(test_no,sub_no):
	with open('data.json') as data_file:
		data = json.load(data_file)
	return data["test"][test_no-1],data["subject"][sub_no-1],data["year"]


'''detect all the circles on the left margin and filter out the filled circles'''
def detectCircles(img,cimg):
	points1 = []
	#detect circles using hough circle algorithm
	circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,20,param1=30,param2=15,minRadius=5,
		maxRadius=10)
	circles = np.uint16(np.around(circles))
	circles = circles.tolist() #convert ndarray to list
	circles = circles[0]
	circles.sort(key=lambda x : x[1])
	circles = eliminate_letters(circles)
	if len(circles) < 30:
		circles = addPoints(circles)
		print(circles)
		print("Error : Could not process image "+file+" belonging to USN : "+USN)
	print(len(circles))
	#print(circles)
	for i in circles:
		count = 0
		#print(i)
		cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),5)
		#check if the circle detected is filled
		for x in range(i[0]-i[2],i[0]+1):
			#checking no of pixels within the circle that are black
			if(thresh[i[1],x] == 0):
				count = count + 1
		print("count: "+str(count)+" Radius: "+str(i[2])+" Center: "+str(i))
		if(count > i[2]-4):
			#filled circle found, save the center co-ordinates and the radius
			points1.append([i[0],i[1],i[2]])
			#draw on filled circles in original image to highlight them
			cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),5)
			cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),5)
	'''sort the list with respect to axis 1 (y co-ordinate) to arrange the points from top
	to bottom in the image''' 
	points1.sort(key=lambda y: y[1]) 
	cv2.imwrite(path+"REAP/test"+ str((int)(random.random()*100)) +".jpg",cimg)
	return points1,circles

def eliminate_letters(circles):
	i = 0
	#if(len(circles) <= 30):
	#	return circles
	while(i < len(circles)):
		if i > len(circles)-4:
			#print(circles[i])
			for j in range(i,len(circles)):
				circles.pop(i)
			return circles
		index = check_for_letters(circles[i:i+5],i)
		if index > -1:
			print("index for popping:"+str(index))
			circles.pop(index)
			#circles = addPoints(circles)
			print("circle after popping :")
			print(circles)
			i = i + 5
			print("i after popping :"+str(i))
		elif( index == 100):
			circles[i:len(circles)-1] = []
		else:
			i = i + 5
	return circles

def check_for_letters(circles,j):
	#print(circles)
	index = -1
	average,mylist = getAverageOfFivePoints(circles)
	print(mylist)
	for i in mylist:
		#second row of circles
		if abs(j-5) % 10 == 0:
			if i in range(45,300):
				index = mylist.index(i)
				print("index:"+str(index))
				if index != 0:
					if circles[index][1] < circles[index+1][1]:
						index = index + 1
				if index == 0:
					index = index
				index = index + j
		else:
			#first row of circles
			if i in range(400,480):
				index = mylist.index(i)
				print("index:"+str(index))
				if index == 0:
					index = index
				else :
					index = -1
				index = index + j
	#variance = (int)(statistics.variance(mylist))
	#print("average : "+str(average))
	'''for i in range(0,len(mylist)) :
		if abs(mylist[i] - average) > 100 and (mylist[i] - mylist[i-1] < 350):
			index = j + i'''
		#print(index)
	return index

def checkIfCancelled(circle1,circle2):
	if abs(circle1[1] - circle2[1]) < circle1[2]:
		print("------------Cancelled------------")
		return True
	return False

'''crop out the answer part and also call getQuesNumber to identify the question number (both main question number and its subpart)'''
def crop(cimg,points,circles):
	j = 0
	#when none of the circles are marked in the page
	if len(points) == 0:
		return
	'''if len(circles) < 30:
		circles = addPoints(circles)
		print(circles)
		print("Error : Could not process image "+file+" belonging to USN : "+USN)'''
	i = 0
	
	for i in range(0,len(points)-1):
		if i % 2 == 0:
			while(isRowEmpty(circles[j:j+10],points,i)):
				print("Flag")
				j = j + 10
		#check if two consecutive circles are marked in the same row
		'''cancelled = checkIfCancelled(points[i],points[i+1])
		if cancelled:
			i = i + 3
			continue'''
		x1 = points[i][0]-points[i][2] # This line is not required
		x2 = cimg.shape[1] # width of the image
		y1 = points[i][1]-points[i][2]
		y2 = points[i+1][1]
		#check if the two circles are from two different questions and not the same question
		if y2-y1 > points[i][2]+50 :
			y1 = points[i-1][1]-points[i-1][2]
			#x1 = points[i-1][0]-points[i-1][2]
			x1 = 0
			# get the region of interest i.e the answer part
			roi = cimg[y1:y2,x1:x2]
			cv2.imwrite(path+"REAP/answers/"+test_name+sub_code
				+str(part1)+part2+str(year)+".jpg",roi)
		else:
			#circles are from the same question, get the first part of the question number
			part1 = getQuesNumber(circles[j:j+5],points[i][0],points[i][2])
			#get the second part
			part2 = getQuesNumber(circles[j+5:j+10],points[i+1][0],points[i][2])
			j = j + 10
			part2 = getCorrespondingLetter(part2)
			print("\nQuestion Number : "+str(part1)+part2)

		if i == len(points)-2:
			y2 = cimg.shape[0] #height of the image
			roi = cimg[y1:y2,0:x2]
			cv2.imwrite(path+"REAP/answers/"+test_name+sub_code+
				str(part1)+part2+str(year)+".jpg",roi)

def addPoints(circles):
	print("In addPoints")
	j = 0
	index = 0
	while(j < len(circles)):
		temp = circles[j:j+5]
		average,mylist = getAverageOfFivePoints(temp)
		print("average: "+str(average))
		for k in range(0,len(mylist)):
			if mylist[k] > 25:
				#print(k)
				index = k + 1
				print("index"+str(index))
				temp,xindex = createNewPoints(temp,index)
				for i in temp:
					circles.insert(j+xindex,i)
					index = index + 1
		j = j + 5
	return circles

def createNewPoints(temp,index):
	diff = []
	mylist = []
	temp = temp[0:index]
	for i in range(0,index):
		mylist.append(temp[i][0])
	mylist.sort()
	print(temp)
	print(mylist)
	for i in range(0,len(mylist)-1):
		diff.append(mylist[i+1]-mylist[i])
	average = (int)(statistics.mean(diff))
	print("average of x points: "+str(average))
	temp1 = []
	for j in range(0,5-index):
		for i in range(0,len(mylist)-1):
			if mylist[i+1]-mylist[i] > 30:
				xindex = i
				xvalue = mylist[xindex]
				mylist.insert(xindex+1,xvalue)
				break
		print(i)
		if(i == len(mylist)-2):
			print("last")
			xindex = i+1
			xvalue = mylist[xindex]
			mylist.insert(xindex+1,xvalue)
		temp1.append([xvalue+average,temp[index-1][1],temp[index-1][2]])
	print("temp :")
	print(temp1)
	return temp1,xindex


def getAverageOfFivePoints(circles):
	mylist = []
	diff = []
	for i in circles:
		mylist.append(i[1])
	for i in range(0,len(mylist)-1):
		diff.append(abs(mylist[i+1]-mylist[i]))
	return (int)(statistics.mean(mylist)),diff


def isRowEmpty(circles,points,i):
	print("-------------------")
	print(circles)
	print(points)
	print("-------------------")
	if points[i] in circles:
		return False
	return True


def getCorrespondingLetter(part2):
	if part2 == 1:
		part2 = "a"
	elif part2 == 2:
		part2 = "b"
	elif part2 == 3:
		part2 = "c"
	elif part2 == 4:
		part2 = "d"
	else:
		part2 = "e"
	return part2
	
'''identify the question number'''
def getQuesNumber(circles,x1,radius):
	xlist = []
	for i in circles:
		xlist.append(i[0])
	xlist.sort()
	print("xlist : " + str(xlist))
	print("x1 : "+str(x1)+"  Radius : "+str(radius))
	#dist_btw_circles = getDistBtwCircles(circles)
	if(x1 == xlist[0]):
		part1 = 1
	elif(x1 == xlist[1]):
		part1 = 2
	elif(x1 == xlist[2]):
		part1 = 3
	elif(x1 == xlist[3]):
		part1 = 4
	elif(x1 == xlist[4]):
		part1 = 5
	return part1

def getDistBtwCircles(circles):
	dist = []
	circles.sort(key=lambda x : x[0])
	print(circles)
	for i in range(0,len(circles)-1):
		dist.append(circles[i+1][0]-circles[i+1][2]-circles[i][2]-circles[i][0])
	return min(dist)




if __name__ == '__main__':
	#image = input("\nEnter the name of the image : ")
	#test_no = int(input("\nEnter the test number (eg:1,2,3) : "))
	#sub_no = int(input("\nEnter the subject no(Eg:1,2,3...9) : "))
	test_no = 1
	sub_no = 1
	#The glob module finds all the pathnames matching a specified pattern
	for file in glob.glob(path+"images/"+USN+"/*.jpg"):
		print("\n\n"+file+"\n\n")
		#read the image
		cimg = cv2.imread(file)
		height,width = cimg.shape[:2]
		cimg = cv2.resize(cimg,(1168,1734),interpolation = cv2.INTER_CUBIC)
		#convert to grayscale image
		img = cv2.imread(file,0)
		height,width = img.shape[:2]
		img = cv2.resize(img,(1168,1734),interpolation = cv2.INTER_CUBIC)
		#get the part before the left margin
		img = img[0:img.shape[0],0:170]	
		#cv2.imshow("img",img)
		#cv2.waitKey(0)
		#img = cv2.GaussianBlur(img,(5,5),0)
		img = cv2.medianBlur(img,5)
		thresh = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2)	
		cv2.imwrite(path+"images/"+"/thresh"+str((int)(random.random()*100))+".jpg",thresh)
		#read the naming convention from json file
		test_name,sub_code,year = namingConvention(test_no,sub_no)
		#get the co-ordinates and radius of filled circles
		points,circles = detectCircles(img,cimg)
		#crop the answer parts and also detect corresponding question numbers
		crop(cimg,points,circles)
		#cv2.imshow('detected circles',cimg)
		#cv2.waitKey(0)
