import socket,sys,random,thread,pygame
from socket import *
from class_ import *
import time as ti

host = ""

try:
	port = int(sys.argv[1])
	map = sys.argv[2]
except:
	f = open("srv.cfg","r").readlines()
	for i in f:
		g = i.split(":")
		if g[0] == "Port":
			port = int(g[1].strip())
		if g[0] == "Map":
			map = g[1].strip()

ss = socket(AF_INET,SOCK_DGRAM)
ss.bind((host,port))

tanks = {}
bullets = []

def run(id):
	global rscore,bscore
	clock = pygame.time.Clock()
	while (True):
		#if ti.time()-lastupdate >= 1./30.:
		clock.tick(30)
		lastupdate = ti.time()
		for i in tanks.keys():
			if tanks[i].team:
				tanks[i].run(mapobjs,rf,bf,spawns=bspawns)
			else:
				tanks[i].run(mapobjs,rf,bf,spawns=rspawns)
		for i in bullets:
			i.run(tanks,mapobjs)
		for i in mapobjs:
			if i.type == "Teleporter":
				i.run(tanks,mapobjs,rf,bf)
			if i.type == "Post":
				a = i.run(mapobjs,rf,bf,rscore,bscore)
				if a == True:
					bscore+=1
				if a == False:
					rscore-=1

def update(id):
	lastupdate = ti.time()
	while (True):
		if ti.time()-lastupdate >= 0.5:
			lastupdate = ti.time()
			for j in tanks:
				for i in tanks:
					ss.sendto("2 "+tanks[i].call+" "+str(tanks[i].x)+" "+str(tanks[i].y),j)
				ss.sendto("5 "+str(rf[0])+" "+str(rf[1])+" "+str(bf[0])+" "+str(bf[1]),j)
		

rspawns = []
bspawns = []
bscore = 0
rscore = 0

thread.start_new(run,(1,))
thread.start_new(update,(1,))

rc = 0
bc = 0

bf = [0,0]
rf = [0,0]

mapobjs = []
mapstring = ""

mapi = pygame.image.load(map)
for x in range(mapi.get_width()):
	for y in range(mapi.get_height()):
		color = mapi.get_at((x,y))
		if color == (0,0,0):
			mapobjs.append(Wall(x*20,y*20))
			mapstring+=mapobjs[-1].toString()+"\n"
		elif color == (100,0,0):
			rspawns.append((x*20+10,y*20+10))
			mapobjs.append(Ground(x*20,y*20))
		elif color == (0,0,100):
			bspawns.append((x*20+10,y*20+10))
			mapobjs.append(Ground(x*20,y*20))
		elif color == (0,0,255):
			mapobjs.append(Post(x*20,y*20,True))
			bf = [x*20,y*20]
		elif color == (255,0,0):
			mapobjs.append(Post(x*20,y*20,False))
			rf = [x*20,y*20]
		elif color == (255,255,255):
			mapobjs.append(Ground(x*20,y*20))
		elif color == (255,0,255):
			mapobjs.append(Ground(x*20,y*20))
			mapobjs.append(Shield(x*20,y*20,False))
		elif color == (0,255,255):
			mapobjs.append(Ground(x*20,y*20))
			mapobjs.append(Shield(x*20,y*20,True))
		else:
			mapobjs.append(Teleporter(x*20,y*20,color))

while True:
	inp,addr = ss.recvfrom(100)
	g = inp.split(" ")
	if g[0] == "-1":	
		if tanks[addr].team:
			rc-=1
		else:
			bc-=1
		for i in tanks.keys():
			ss.sendto("-1 "+tanks[addr].call,i)
		ndict = {}
		for i in tanks.keys():
			if i!=addr:
				ndict[i] = tanks[i]
		tanks = ndict
	if g[0] == "0":
		call = g[1]
		for i in mapobjs:
			ss.sendto("-1 "+i.toString(),addr)
		if bc>rc:
			tanks[addr] = Tank(call,True)
			rc+=1
			print True
		elif bc <= rc:
			tanks[addr] = Tank(call,False)
			bc+=1
			print False
		for i in tanks.keys():
			for j in tanks.keys():
				ss.sendto("0 "+tanks[j].call+" "+str(tanks[j].team),i)
		for i in tanks.keys():
			for j in tanks.keys():
				ss.sendto("0 "+tanks[i].call+" "+str(tanks[i].team),j)
		ss.sendto("6 "+str(rscore)+" "+str(bscore),addr)
			

	if g[0] == "1":
		hx = int(g[1])
		hy = int(g[2])
		tanks[addr].hx = hx
		tanks[addr].hy = hy
		for i in tanks.keys():
			ss.sendto("1 "+tanks[addr].call+" "+str(hx)+" "+str(hy),i)

	if g[0] == "2":
		tanks[addr].trt = int(g[1])
		for i in tanks.keys():
			ss.sendto("3 "+tanks[addr].call+" "+g[1],i)
	if g[0] == "3":
		if tanks[addr].hp > 0:
			bullets.append(Bullet(tanks[addr].x-15*sin(tanks[addr].trt*pi/180.),tanks[addr].y-15*cos(tanks[addr].trt*pi/180.),180+tanks[addr].trt,tanks[addr]))
			for i in tanks.keys():
				ss.sendto("4 "+tanks[addr].call,i)
		
