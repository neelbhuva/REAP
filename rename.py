import os,glob,json

def namingConvention():
	with open('/var/www/html/REAP/configuration/config.json') as data_file:
		data = json.load(data_file)
	global source_path
	source_path = data["scanned_images_source_path"]
	global image_extension
	image_extension = data["image_extension"]

def rename():
	sub_directories = []
	for root,directories,files in os.walk(source_path):
		sub_directories.append(root)
	sub_directories.pop(0)
	for directory in sub_directories:
		i = 1
		for file in sorted(glob.glob(directory+"/*"+".jpg")):
			#print("\n\n"+file+"\n\n")
			l = file.split("/")
			l.pop()
			last = "/page" + str(i) + image_extension
			i = i + 1
			path = "/".join(l)
			path = path + last
			#print(path)
			os.rename(file,path)

if __name__ == '__main__':
	namingConvention()
	rename()