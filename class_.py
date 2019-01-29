import pygame,math,random
from pygame import *
from math import *

class Tank(object):
	def __init__(self,call,team):
		self.x = 0
		self.y = 0
		self.hx = 0
		self.hy = 0
		self.rt = 0
		self.trt = 0
		self.hp = 0
		self.call = call
		self.ltp = 0
		self.team = team
		self.flag = None
		self.timer = 0
		self.exp_rad = 0
	def render(self,screen,call,scrollx,scrolly):
		if self.hx!=0 or self.hy!=0:
			rt = -atan2(self.hy,self.hx)/pi*180.-90.
			self.rt = rt
		else:
			rt = self.rt
		if self.hp>0:
			if self.call != call:
				if self.team == False:
					a = pygame.transform.rotate(pygame.image.load("rhull.png").convert_alpha(),rt)
					b = pygame.transform.rotate(pygame.image.load("rturret.png").convert_alpha(),self.trt)
					screen.blit(a,(self.x+430-a.get_width()/2-scrollx,self.y+340-a.get_height()/2-scrolly))
					screen.blit(b,(self.x+430-b.get_width()/2-scrollx,self.y+340-b.get_height()/2-scrolly))
				else:
					a = pygame.transform.rotate(pygame.image.load("bhull.png").convert_alpha(),rt)
					b = pygame.transform.rotate(pygame.image.load("bturret.png").convert_alpha(),self.trt)
					screen.blit(a,(self.x+430-a.get_width()/2-scrollx,self.y+340-a.get_height()/2-scrolly))
					screen.blit(b,(self.x+430-b.get_width()/2-scrollx,self.y+340-b.get_height()/2-scrolly))
				pygame.draw.rect(screen,(255,0,0),Rect(self.x+430-scrollx-15,self.y+340-scrolly-25,30,2))
				pygame.draw.rect(screen,(0,255,0),Rect(self.x+430-scrollx-15,self.y+340-scrolly-25,self.hp/3,2))
			else:
				if self.team == False:
					a = pygame.transform.rotate(pygame.image.load("rhull.png").convert_alpha(),rt)
					b = pygame.transform.rotate(pygame.image.load("rturret.png").convert_alpha(),self.trt)
					screen.blit(a,(430-a.get_width()/2,340-a.get_height()/2))
					screen.blit(b,(430-b.get_width()/2,340-b.get_height()/2))
				else:
					a = pygame.transform.rotate(pygame.image.load("bhull.png").convert_alpha(),rt)
					b = pygame.transform.rotate(pygame.image.load("bturret.png").convert_alpha(),self.trt)
					screen.blit(a,(430-a.get_width()/2,340-a.get_height()/2))
					screen.blit(b,(430-b.get_width()/2,340-b.get_height()/2))
				pygame.draw.rect(screen,(255,0,0),(430-15,340-25,30,2))
				pygame.draw.rect(screen,(0,255,0),(430-15,340-25,self.hp/3,2))
		elif self.timer > 285:
			rad = (-abs(self.timer - 285 - 7) + 15) * 5
			exp = pygame.transform.scale(pygame.image.load("exp.png").convert_alpha(), (rad, rad))
			if self.call == call:
				screen.blit(exp, (430-exp.get_width()/2,340-exp.get_height()/2))
			else:
				screen.blit(exp, (self.x+430-exp.get_width()/2-scrollx,self.y+340-exp.get_height()/2-scrolly))
	def run(self,mapobjs,rf,bf,spawns = False):
		self.ltp+=1
		if self.hp>0:
			self.x+=self.hx
			self.y+=self.hy
			for i in mapobjs:
				if i.type == "Wall":
					if sqrt((i.y+10-self.y)**2+(i.x+10-self.x)**2) < 25:
						self.x-=self.hx*2
						self.y-=self.hy*2
			if self.team == False:
				if sqrt((bf[1]+10-self.y)**2+(bf[0]+10-self.x)**2) < 25:
					bf[0] = self.x-10
					bf[1] = self.y-10
				self.flag = False
			else:
				if sqrt((rf[1]+10-self.y)**2+(rf[0]+10-self.x)**2) < 25:
					rf[0] = self.x-10
					rf[1] = self.y-10
				self.flag = True
		else:
			if spawns and self.timer < 100:
				if (self.x,self.y) not in spawns:
					po = random.choice(spawns)
					self.x = po[0]
					self.y = po[1]
				if self.flag!=None:
					if self.flag == True and self.team == False:
						bf[1] = self.y
						bf[0] = self.x
					elif self.flag == False and self.team == True:
						rf[0] = self.x
						rf[1] = self.y
					self.flag = None
			self.timer-=1
			if self.timer <= 0:
				self.timer = 300
				self.hp = 100

class Bullet(object):
	def __init__(self,sx,sy,rt,master):
		self.x = sx
		self.y = sy
		self.rt = rt
		self.alive = True
		self.master = master
		self.timer = 15
	def run(self,tanks,mapobjs):
		if self.alive:
			self.x+=sin(self.rt*pi/180.)*5
			self.y+=cos(self.rt*pi/180.)*5
			for i in tanks.keys():
				if self.master.call!=tanks[i].call and tanks[i].hp>0:
					if sqrt((tanks[i].y-self.y)**2+(tanks[i].x-self.x)**2) < 15:
						tanks[i].hp-=20
						self.alive = False
			for i in mapobjs:
				if i.type == "Wall" or (i.type == "Shield" and self.master.team != i.team):
					if sqrt((i.y+10-self.y)**2+(i.x+10-self.x)**2) < 13:
						self.alive = False
	def render(self,screen,scrollx,scrolly):
		if self.alive:
			pygame.draw.circle(screen,(0,0,0),(int(self.x)-scrollx+430,int(self.y)-scrolly+340),2)
		elif self.timer > 0:
			rad = (-abs(self.timer - 7) + 15) * 2
			exp = pygame.transform.scale(pygame.image.load("exp.png").convert_alpha(), (rad, rad))
			screen.blit(exp, (int(self.x)-scrollx+430-exp.get_width()/2,int(self.y)-scrolly+340-exp.get_height()/2))
			self.timer -= 1

class Wall(object):
	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.type = "Wall"
	def toString(self):
		return "Wall:"+str(self.x)+":"+str(self.y)
	def render(self,screen,scrollx,scrolly):
		if self.x-scrollx+430 > -50 and self.x-scrollx+430 < 860+50:
			if self.y-scrolly+340 > -50 and self.y-scrolly+340 < 680+50:
				screen.blit(pygame.image.load("wall.png").convert(),(self.x-scrollx+430,self.y-scrolly+340))

class Post(object):
	def __init__(self,x,y,team):
		self.x = x
		self.y = y
		self.team = team
		self.type = "Post"
	def toString(self):
		return "Post:"+str(self.x)+":"+str(self.y)+":"+str(self.team)
	def grab(self,rf,bf,rscore,bscore):
		if self.team == False:
			rf[0] = self.x
			rf[1] = self.y
			bscore+=1
		else:
			bf[0] = self.x
			bf[1] = self.y
			rscore+=1
	def render(self,screen,scrollx,scrolly):
		if self.x-scrollx+430 > -50 and self.x-scrollx+430 < 860+50:
			if self.y-scrolly+340 > -50 and self.y-scrolly+340 < 680+50:
				if self.team:
					screen.blit(pygame.image.load("Blue.png").convert(),(self.x-scrollx+430,self.y-scrolly+340))
				else:
					screen.blit(pygame.image.load("Red.png").convert(),(self.x-scrollx+430,self.y-scrolly+340))
	def run(self,mapobjs,rf,bf,rscore,bscore):
		if self.team == False and sqrt((bf[1]-self.y)**2+(bf[0]-self.x)**2) < 15:
			for i in mapobjs:
				if i.type == "Post" and i.team == True:
					i.grab(rf,bf,rscore,bscore)
					return True
		if self.team == True and sqrt((rf[1]-self.y)**2+(rf[0]-self.x)**2) < 15:
			for i in mapobjs:
				if i.type == "Post" and i.team == False:
					i.grab(rf,bf,rscore,bscore)
					return False

class Ground(object):
	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.type = "Ground"
	def toString(self):
		return "Ground:"+str(self.x)+":"+str(self.y)
	def render(self,screen,scrollx,scrolly):
		if self.x-scrollx+430 > -50 and self.x-scrollx+430 < 860+50:
			if self.y-scrolly+340 > -50 and self.y-scrolly+340 < 680+50:
				screen.blit(pygame.image.load("ground.png").convert(),(self.x-scrollx+430,self.y-scrolly+340))

class Shield(object):
	def __init__(self,x,y,team):
		self.x = x
		self.y = y
		self.team = team
		self.type = "Shield"
	def toString(self):
		return "Shield:"+str(self.x)+":"+str(self.y)+":"+str(self.team)
	def render(self,screen,scrollx,scrolly):
		if self.x-scrollx+430 > -50 and self.x-scrollx+430 < 860+50:
			if self.y-scrolly+340 > -50 and self.y-scrolly+340 < 680+50:
				if self.team:
					screen.blit(pygame.image.load("bshield.png").convert_alpha(),(self.x-scrollx+430,self.y-scrolly+340))
				else:
					screen.blit(pygame.image.load("rshield.png").convert_alpha(),(self.x-scrollx+430,self.y-scrolly+340))

class Teleporter(object):
	def __init__(self,x,y,chan):
		self.x = x
		self.y = y
		self.id = random.randint(0,100101010011010)
		self.chan = chan
		self.type = "Teleporter"
	def toString(self):
		return "Teleporter:"+str(self.x)+":"+str(self.y)+":"+str(self.chan[0])+":"+str(self.chan[1])+":"+str(self.chan[2])
	def run(self,tanks,mapobjs,rf,bf):
		for i in tanks.keys():
			if sqrt((tanks[i].y-self.y-10)**2+(tanks[i].x-self.x-10)**2) < 10 and tanks[i].ltp>100:
				for j in mapobjs:
					if j.type == "Teleporter":
						if j.chan == self.chan and j.id!=self.id:
							if sqrt((bf[1]+10-self.y)**2+(bf[0]+10-self.x)**2) < 25:
								tanks[i].x = j.x+10
								tanks[i].y = j.y+10
								bf[0] = tanks[i].x
								bf[1] = tanks[i].y
							if sqrt((rf[1]+10-self.y)**2+(rf[0]+10-self.x)**2) < 25:
								tanks[i].x = j.x+10
								tanks[i].y = j.y+10
								rf[0] = tanks[i].x
								rf[1] = tanks[i].y
							tanks[i].x = j.x+10
							tanks[i].y = j.y+10
							tanks[i].hx = 0
							tanks[i].hy = 0
							tanks[i].ltp = 0

	def render(self,screen,scrollx,scrolly):
		if self.x-scrollx+430 > -50 and self.x-scrollx+430 < 860+50:
			if self.y-scrolly+340 > -50 and self.y-scrolly+340 < 680+50:
				pygame.draw.rect(screen,self.chan,Rect(self.x-scrollx+430,self.y-scrolly+340,20,20))
				screen.blit(pygame.image.load("teleporter.png").convert_alpha(),(self.x-scrollx+430,self.y-scrolly+340))
