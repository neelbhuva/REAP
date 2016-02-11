import cv2
import numpy as np
import json
#distance from left to first circle is around 13, radius is 8-9, dist btw 2 circles is 6
#distance btw circle in first row and second row is 18
dist_from_left = 13
dist_btw_circles = 6

def detectCircles(img,cimg):
	points1 = []
	#detect circles using hough circle algorithm
	circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,20,param1=30,param2=15,minRadius=5,maxRadius=10)
	circles = np.uint16(np.around(circles))
	circles = circles.tolist() #convert ndarray to list
	circles = circles[0]
	circles.sort(key=lambda x : x[1])
	print(circles)
	for i in circles:
		count = 0
		#print(i)
		cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
		#check if the circle detected is filled
		for x in range(i[0]-i[2],i[0]):
			#checking no of pixels within the circle that are black
			if(thresh[i[1],x] == 0):
				count = count + 1
		#print("count: "+str(count)+" Radius: "+str(i[2]))
		if(count > i[2]-3):
			#filled circle found, save the center co-ordinates and the radius
			points1.append([i[0],i[1],i[2]])
			#draw on filled circles in original image to highlight them
			cv2.circle(cimg,(i[0],i[1]),i[2],(0,255,0),2)
			cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)
	'''sort the list with respect to axis 1 (y co-ordinate) to arrange the points from top
	to bottom in the image''' 
	points1.sort(key=lambda y: y[1]) 
	cv2.imwrite("/home/neel/opencvproject/REAP/test.jpg",cimg)
	return points1,circles

'''def crop(cimg,points,circles):
	for i in range(0,len(points)-1):
		#print("i : " + str(i))
		x1 = points[i][0]-points[i][2] # This line is not required
		x2 = cimg.shape[1] # width of the image
		y1 = points[i][1]-points[i][2]
		y2 = points[i+1][1]
		#check if the two circles are from two different questions and not the same question
		if y2-y1 > points[i][2]+50 :
			y1 = points[i-1][1]-points[i-1][2]
			x1 = points[i-1][0]-points[i-1][2]
			# get the region of interest i.e the answer part
			roi = cimg[y1:y2,x1:x2]
			cv2.imwrite("/home/neel/opencvproject/REAP/answers/"+str(part1)+part2+".jpg",roi)
		else:
			#circles are from the same question, get the first part of the question number
			part1 = quesNumber(points[i][0])
			#get the second part
			part2 = quesNumber(points[i+1][0])
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
			print("\npart1 : "+str(part1))
			print("part2 : "+part2)
			#print(points[i][0],points[i+1][0])

		if i == 6:
			y2 = cimg.shape[0] #height of the image
			print(x1,y1,x2,y2)
			roi = cimg[y1:y2,x1:x2]
			cv2.imwrite("/home/neel/opencvproject/REAP/answers/"+str(part1)+part2+"1.jpg",roi)'''

def crop(cimg,points,circles):
	j = 0
	for i in range(0,len(points)-1):
		#print("i : " + str(i))
		x1 = points[i][0]-points[i][2] # This line is not required
		x2 = cimg.shape[1] # width of the image
		y1 = points[i][1]-points[i][2]
		y2 = points[i+1][1]
		#check if the two circles are from two different questions and not the same question
		if y2-y1 > points[i][2]+50 :
			y1 = points[i-1][1]-points[i-1][2]
			x1 = points[i-1][0]-points[i-1][2]
			# get the region of interest i.e the answer part
			roi = cimg[y1:y2,x1:x2]
			cv2.imwrite("/home/neel/opencvproject/REAP/answers/"+str(part1)+part2+".jpg",roi)
		else:
			#circles are from the same question, get the first part of the question number
			part1 = quesNumber(circles[j:j+5],points[i][0],points[i][2])
			#get the second part
			part2 = quesNumber(circles[j+5:j+10],points[i+1][0],points[i][2])
			j = j + 10
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
			print("\npart1 : "+str(part1))
			print("part2 : "+part2)
			#print(points[i][0],points[i+1][0])

		if i == 6:
			y2 = cimg.shape[0] #height of the image
			print(x1,y1,x2,y2)
			roi = cimg[y1:y2,x1:x2]
			cv2.imwrite("/home/neel/opencvproject/REAP/answers/"+str(part1)+part2+".jpg",roi)

def quesNumber(circles,x1,radius):
	j = 0
	print(circles)
	min_x = circles[0][0]
	for i in circles:
		if(i[0] < min_x):
			min_x = i[0]   # min_x is the x coordinate of the center of first circle
			min_radius = i[2] # min_radius is the radius of first circle
	if(x1 < min_x + dist_btw_circles + radius):
		part1 = 1
	elif(x1 < min_x + dist_btw_circles * 2 + radius * 2):
		part1 = 2
	elif(x1 < min_x + dist_btw_circles*3+ 2*radius * 2):
		part1 = 3
	elif(x1 < min_x + dist_btw_circles*4 + 3*radius * 2):
		part1 = 4
	elif(x1 < min_x + dist_btw_circles*5 + 4*radius * 2):
		part1 = 5
	return part1


if __name__ == '__main__':	
	image = input("Enter the name of the image with extension : ")
	
	#read the image
	cimg = cv2.imread('/home/neel/opencvproject/testimages/'+image+'.jpg')

	#convert to grayscale image
	img = cv2.imread('/home/neel/opencvproject/testimages/'+image+'.jpg',0)

	#get the part before the left margin
	img = img[0:img.shape[0],0:150]
	
	#img = cv2.GaussianBlur(img,(5,5),0)
	img = cv2.medianBlur(img,5)
	thresh = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2)
	
	#get the co-ordinates and radius of filled circles
	points,circles = detectCircles(img,cimg)
	
	#crop the answer parts and also detect corresponding question numbers
	crop(cimg,points,circles)
	print(points)

	cv2.imwrite("/home/neel/opencvproject/REAP/thresh.jpg",thresh)
	cv2.imshow('detected circles',cimg)
	cv2.waitKey(0)
	cv2.destroyAllWindows()