import socket,sys,thread,pygame
from socket import *
from class_ import *
from pygame import *
pygame.init()

s = socket(AF_INET,SOCK_DGRAM)

try:
	srvaddr = sys.argv[1]
	port = int(sys.argv[2])
	call = sys.argv[3]
except:
	f = open("client.cfg","r").readlines()
	for i in f:
		g = i.split(":")
		if g[0] == "Port":
			port = int(g[1].strip())
		if g[0] == "Callsign":
			call = g[1].strip()
		if g[0] == "Server":
			srvaddr = g[1].strip()

host = (srvaddr,port)

s.sendto("0 "+call,host)

tanks = {}
bullets = []
mapobjs = []

bf = [0,0]
rf = [0,0]
bscore = 0
rscore = 0

def listen(id):
	global tanks,bf,rf
	while (True):
		inp,addr = s.recvfrom(1024000)
		g = inp.split(" ")
		if g[0] == "-1":
			mapstring = g[1]
			for i in mapstring.split("\n"):
				h = i.split(":")
				if h[0] == "Wall":
					mapobjs.append(Wall(int(h[1]),int(h[2])))
				if h[0] == "Post":
					mapobjs.append(Post(int(h[1]),int(h[2]),h[3]=="True"))
					if h[3] == "True":
						bf = [int(h[1]),int(h[2])]
					else:
						rf = [int(h[1]),int(h[2])]
				if h[0] == "Ground":
					mapobjs.append(Ground(int(h[1]),int(h[2])))
				if h[0] == "Shield":
					mapobjs.append(Shield(int(h[1]),int(h[2]),h[3]=="True"))
				if h[0] == "Teleporter":
					mapobjs.append(Teleporter(int(h[1]),int(h[2]),(int(h[3]),int(h[4]),int(h[5]))))
		if g[0] == "0":
			call1 = g[1]
			if g[2] == "False":
				tanks[call1] = Tank(call1,False)
			else:
				tanks[call1] = Tank(call1,True)
		if len(tanks)>0:
			if g[0] == "-1":
				ndict = {}
				for i in tanks.keys():
					if i!=g[1]:
						ndict[i] = tanks[i]
				tanks = ndict
			if g[0] == "1":
				hx = int(g[2])
				hy = int(g[3])
				tanks[g[1]].hx = hx
				tanks[g[1]].hy = hy
			if g[0] == "2":
				tanks[g[1]].x = int(float(g[2]))
				tanks[g[1]].y = int(float(g[3]))
			if g[0] == "3":
				tanks[g[1]].trt = int(float(g[2]))
			if g[0] == "4":
				bullets.append(Bullet(tanks[g[1]].x-15*sin(tanks[g[1]].trt*pi/180.),tanks[g[1]].y-15*cos(tanks[g[1]].trt*pi/180.),180+tanks[g[1]].trt,tanks[g[1]]))
			if g[0] == "5":
				rf = [int(g[1]),int(g[2])]
				bf = [int(g[3]),int(g[4])]
			if g[0] == "6":
				rscore = int(g[1])
				bscore = int(g[2])
thread.start_new(listen,(1,))

screen = pygame.display.set_mode((860,680),0,32)
pygame.display.set_caption("Microtanks")
pygame.display.set_icon(pygame.image.load("tank.png"))

hx = 0
hy = 0
scrollx = 0
scrolly = 0

clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

font = pygame.font.SysFont("Sans",30)

while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			s.sendto("-1",host)
			raise SystemExit
		if event.type == KEYDOWN:
			if event.key == K_w:
				hy = -1
			if event.key == K_s:
				hy = 1
			if event.key == K_d:
				hx = 1
			if event.key == K_a:
				hx = -1
			s.sendto("1 "+str(hx)+" "+str(hy),host)
		if event.type == KEYUP:
			if event.key == K_w:
				hy = 0
			if event.key == K_s:
				hy = 0
			if event.key == K_d:
				hx = 0
			if event.key == K_a:
				hx = 0
			s.sendto("1 "+str(hx)+" "+str(hy),host)
		if event.type == MOUSEBUTTONDOWN:
			s.sendto("3",host)
	mx,my = pygame.mouse.get_pos()
	trt = int(-atan2(my-340,mx-430)/pi*180.-90.)
	s.sendto("2 "+str(trt),host)
	clock.tick(30)
	try:
		scrollx = tanks[call].x
		scrolly = tanks[call].y
	except:
		pass
	screen.fill((255,255,255))
	for i in mapobjs:
		if i.type in ["Ground","Post","Teleporter"]:
			i.render(screen,scrollx,scrolly)
			if i.type == "Post":
				a = i.run(mapobjs,rf,bf,rscore,bscore)
				if a == False:
					rscore+=1
				if a == True:
					bscore+=1
	for i in bullets:
		i.run(tanks,mapobjs)
		i.render(screen,scrollx,scrolly)
	for i in tanks.keys():
		tanks[i].render(screen,call,scrollx,scrolly)
		tanks[i].run(mapobjs,rf,bf)
	for i in mapobjs:
		if not i.type in ["Ground","Post","Teleporter"]:
			i.render(screen,scrollx,scrolly)
			if i.type == "Teleporter":
				pass
				#i.run(tanks,mapobjs,rf,bf)
	screen.blit(pygame.image.load("bf.png").convert_alpha(),(bf[0]+435-scrollx,bf[1]+345-scrolly))
	screen.blit(pygame.image.load("rf.png").convert_alpha(),(rf[0]+435-scrollx,rf[1]+345-scrolly))
	a = font.render(str(rscore)+" / "+str(bscore),True,(0,0,0))
	screen.blit(a,(430-a.get_width()/2,0))
	pygame.display.update()
