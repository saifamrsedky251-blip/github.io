import pygame,random,math,os,time
pygame.mixer.init()
def check_assets():
 if not os.path.exists("assets"):os.makedirs("assets")
 pygame.init()
 def c(n,c,s=(40,40),r=0):surf=pygame.Surface(s,pygame.SRCALPHA);(pygame.draw.circle(surf,c,(s[0]//2,s[1]//2),s[0]//2)if r else surf.fill(c));pygame.image.save(surf,f"assets/{n}.png")
 for ch in["wizard","knight","archer","enemy","boss","xp","chest"]:c(ch,(random.randint(50,255),50,255))
 c("bullet",(255,255,255),(8,8),1);c("orb",(0,255,255),(10,10),1);c("legendary",(255,215,0),(18,18),1)
 # Special for wizard
 wizard_surf = pygame.Surface((40,40),pygame.SRCALPHA)
 wizard_surf.fill((150,50,255))
 pygame.draw.polygon(wizard_surf, (0,0,0), [(15,5),(25,5),(20,15)])  # hat
 pygame.draw.line(wizard_surf, (139,69,19), (30,25), (38,20), 2)  # wand
 pygame.image.save(wizard_surf, "assets/wizard.png")
class Player(pygame.sprite.Sprite):
 def __init__(self,t):
  super().__init__()
  self.type=t;self.image=pygame.Surface((40,40),pygame.SRCALPHA)
  cols={"Wizard":(150,50,255),"Knight":(100,100,100),"Archer":(50,200,50)};self.base_color=cols.get(t,(255,255,255));self.image.fill(self.base_color);self.rect=self.image.get_rect(center=(600,450))
  stats={"Knight":(350,3.5,18,0.7),"Archer":(150,6.5,12,1.6),"Wizard":(180,5.0,14,1.2)};self.max_hp,self.speed,self.base_dmg,self.atk_speed=stats.get(t,(180,5.0,14,1.2))
  self.hp=self.max_hp;self.dmg_mult=1.0;self.atk_level=0;self.max_hp_level=0;self.level,self.xp,self.xp_next=1,0,100
  self.skills={"Firebreath":0,"Lightning":0};self.last_hit=0;self.last_shot={"Basic":0};[self.last_shot.update({k:0})for k in self.skills]
  self.fire_particles=[];self.lightning_effects=[];self.camera_pos=pygame.math.Vector2(self.rect.center);self.iframe_time=1000;self.iframe_until=0;self.camera_shake=0
  self.firebreath_active = 0  # remaining frames for firebreath activation
  self.last_direction = pygame.math.Vector2(1,0)  # default direction (right)
 @property
 def atk_speed_per_ms(self):return self.atk_speed/1000.0
 @property
 def move_speed(self):return self.speed
 @property
 def dmg(self):return (self.base_dmg*self.dmg_mult)*(1+self.atk_level*0.1)
 def update_fire(self,n,time_scale,game_manager):
  l=self.skills["Firebreath"]
  if l>0:
   if self.firebreath_active <= 0:
    ls=self.last_shot.get("Firebreath",0)
    cd=(3000 - (l-1)*200) / time_scale  # cooldown starts at 3s, decreases by 0.2s per level
    if n - ls > cd:
     self.last_shot["Firebreath"]=n
     self.firebreath_active = 120 + (l-1) * 30  # duration in frames
     if "firebreath" in game_manager.sounds:game_manager.sounds["firebreath"].play()
   if self.firebreath_active > 0:
    for _ in range(1 if l<7 else 3):
     a=random.uniform(-12,12);s=random.uniform(5,8)+l*0.4;pv=self.last_direction.rotate(a)*s;sz=6+(2 if l>=4 else 0)+(4 if l==7 else 0);dm=(0.8+0.5*l)*3
     if l>=7:dm*=3.0
     lf=18 + l * 5;reach_mult=2 if l<7 else 5;sp=pygame.math.Vector2(self.rect.center)+self.last_direction*18*reach_mult;self.fire_particles.append({"pos":[sp.x,sp.y],"vel":pv,"life":lf,"size":sz,"dmg":dm,"age":0})
    self.firebreath_active -= time_scale
  [p.__setitem__("life",p["life"]-time_scale)or p.__setitem__("age",p["age"]+time_scale)or(p.__setitem__("pos",[p["pos"][0]+p["vel"].x * time_scale,p["pos"][1]+p["vel"].y * time_scale]))if p["life"]>0 else None for p in self.fire_particles[:]];self.fire_particles[:] = [p for p in self.fire_particles if p["life"] > 0]
 def update_lightning(self,t,n,enemies,time_scale,game_manager):
  l=self.skills["Lightning"]
  if l>0 and t and pygame.math.Vector2(t.rect.center).distance_to(self.rect.center)<350:
   ls=self.last_shot.get("Lightning",0);cd=1500
   if n-ls>cd:
    self.last_shot["Lightning"]=n;s=pygame.math.Vector2(self.rect.center);e=pygame.math.Vector2(t.rect.center);w=2+(l//3);dm=(8+l*6)*3*2
    if l>=7:dm*=2.2;w*=2
    chain = [t]
    for _ in range(2+l):
     nearby = [en for en in enemies.sprites() if en not in chain and pygame.math.Vector2(en.rect.center).distance_to(chain[-1].rect.center) < 500]
     if nearby:
      closest = min(nearby, key=lambda en: pygame.math.Vector2(en.rect.center).distance_to(chain[-1].rect.center))
      chain.append(closest)
     else:
      break
    for i in range(len(chain)):
     start_pos = s if i==0 else pygame.math.Vector2(chain[i-1].rect.center)
     end_pos = pygame.math.Vector2(chain[i].rect.center)
     self.lightning_effects.append({"start":start_pos,"end":end_pos,"life":8,"dmg":dm,"width":w,"hit":set()})
  [L.__setitem__("life",L["life"]-time_scale)for L in self.lightning_effects[:]]
  self.lightning_effects[:] = [L for L in self.lightning_effects if L["life"] > 0]


class GameManager:
 def __init__(self):
  check_assets();pygame.init();self.screen=pygame.display.set_mode((1200,900));pygame.display.set_caption("Bullet Heaven Roguelite");self.clock=pygame.time.Clock();self.font=pygame.font.SysFont("Georgia",22,1);self.title_font=pygame.font.SysFont("Garamond",56,1);self.state="MENU";self.up_options=[];self.scale_timer=0;self.boss_timer=0;self.world_offset=pygame.math.Vector2(0,0);self.camera_lerp=0.12;self.show_inventory=0;self.creative_mode=0;self.enemy_hp_mult=1.0;self.enemy_spd_mult=1.0;self.time_scale=1.0;self.show_difficulty_slider=0;self.difficulty_mult=1.0
  self.assets={}
  for a in["bullet","orb","legendary"]:
   try:self.assets[a]=pygame.image.load(f"assets/{a}.png").convert_alpha()
   except:surf=pygame.Surface((10,10),pygame.SRCALPHA);surf.fill((255,255,255));self.assets[a]=surf
  self.sounds={};self.boss_music=None
  sound_files={"firebreath":"assets/sounds/firebreath_burst.wav","level_up":"assets/sounds/level_up_chime.wav","game_over":"assets/sounds/game_over.wav","victory":"assets/sounds/victory.wav"}
  for key,path in sound_files.items():
   try:
    if os.path.exists(path):self.sounds[key]=pygame.mixer.Sound(path)
    else:print(f"Sound file not found: {path}")
   except Exception as e:print(f"Error loading {path}: {e}")
  if "firebreath" in self.sounds:self.sounds["firebreath"].set_volume(0.3)
  if "level_up" in self.sounds:self.sounds["level_up"].set_volume(0.9)
  if "game_over" in self.sounds:self.sounds["game_over"].set_volume(0.8)
  if "victory" in self.sounds:self.sounds["victory"].set_volume(0.9)
 def start_game(self,t):
  self.player=Player(t);self.enemies=pygame.sprite.Group();self.bullets=pygame.sprite.Group();self.orbs=pygame.sprite.Group();self.chests=pygame.sprite.Group();self.start_time=pygame.time.get_ticks();self.last_scale_time=self.start_time;self.last_boss_time=self.start_time;self.state="PLAYING";self.enemy_hp_mult=1.0;self.enemy_spd_mult=1.0;self.time_scale=1.0;self.game_time=0;self.last_enemy_double_time=0
 def spawn_enemy(self,b=0):
  e=pygame.sprite.Sprite()
  if b:e.image=pygame.Surface((90,90),pygame.SRCALPHA);e.image.fill((120,20,20));e.rect=e.image.get_rect();a=random.uniform(0,math.tau);d=random.uniform(650,850);e.rect.center=(self.player.rect.centerx+math.cos(a)*d,self.player.rect.centery+math.sin(a)*d);e.max_hp=int(500+150*self.player.level*self.enemy_hp_mult);e.hp=e.max_hp;e.speed=0.7*self.enemy_spd_mult;e.is_boss=1;e.is_final_boss=0
  else:e.image=pygame.Surface((30,30),pygame.SRCALPHA);e.image.fill((200,50,50));e.rect=e.image.get_rect();a=random.uniform(0,math.tau);e.rect.center=(self.player.rect.centerx+math.cos(a)*random.uniform(450,700),self.player.rect.centery+math.sin(a)*random.uniform(450,700));e.max_hp=int(20+self.player.level*8*self.enemy_hp_mult);e.hp=e.max_hp;e.speed=1.3*self.enemy_spd_mult;e.is_boss=0;e.is_final_boss=0
  self.enemies.add(e)
 def spawn_final_boss(self):
  e=pygame.sprite.Sprite();surf=pygame.Surface((200,200),pygame.SRCALPHA);pygame.draw.circle(surf,(100,0,150),(100,100),60);
  for i in range(8):a=i*(360/8);x=100+80*math.cos(math.radians(a));y=100+80*math.sin(math.radians(a));pygame.draw.circle(surf,(200,100,255),(int(x),int(y)),8)
  for r in [95,115]:pygame.draw.circle(surf,(150,50,200),(100,100),r,3)
  e.image=surf;e.rect=e.image.get_rect();e.rect.center=(self.player.rect.centerx,self.player.rect.centery-200);e.max_hp=int(576000+192000*self.player.level);e.hp=e.max_hp;e.speed=1.5;e.is_boss=1;e.is_final_boss=1;e.ring_rotation=0;e.damage=25+self.player.level*5
  e.eyes=[i for i in range(8)];e.eye_shoot_cooldown=0;e.last_eye_regen=pygame.time.get_ticks();e.last_eye_shot=pygame.time.get_ticks()
  try:
   if os.path.exists("assets/sounds/boss_music.mp3"):self.boss_music=pygame.mixer.Sound("assets/sounds/boss_music.mp3");self.boss_music.play(-1)
   else:print("Boss music file not found: assets/sounds/boss_music.mp3")
  except Exception as e:print(f"Error loading boss music: {e}")
  self.enemies.add(e)
 def generate_upgrades(self):
  p=[]
  if self.player.max_hp_level<10:p.append(("Max HP +5%","max_hp"))
  p.append(("ATK +10%","atk"));p.append(("Speed +1","speed"))
  for s in self.player.skills:
   if self.player.skills[s]<7:p.append((f"Level {s}",s))
  self.up_options=random.sample(p,min(3,len(p))) if len(p)>0 else p
 def award_drop(self,pos,b=0):
  if random.random()<0.3:
   o=pygame.sprite.Sprite();o.image=self.assets["orb"];o.rect=o.image.get_rect(center=pos);o.spawn_time=pygame.time.get_ticks();self.orbs.add(o)
 def update_difficulty(self,n):
  if n-self.last_scale_time>60000:self.last_scale_time=n;self.enemy_hp_mult*=1.12
  if n-self.last_boss_time>150000:self.last_boss_time=n;self.spawn_enemy(b=1)
  max_enemies=int((5+int(self.game_time/5000))*self.difficulty_mult)
  if random.random()<0.15 and len(self.enemies)<max_enemies:self.spawn_enemy(b=0)
 def automatic_fire(self,n,t):
  cd=int(max(120,1000/self.player.atk_speed) / self.time_scale)
  if n-self.player.last_shot["Basic"]>cd and t:
   b=pygame.sprite.Sprite();b.image=self.assets["bullet"];b.rect=b.image.get_rect(center=self.player.rect.center);dv=(pygame.math.Vector2(t.rect.center)-pygame.math.Vector2(b.rect.center))
   if dv.length()==0:dv=pygame.math.Vector2(1,0)
   b.vel=dv.normalize()*12;b.dmg=self.player.base_dmg*self.player.dmg_mult;self.bullets.add(b);self.player.last_shot["Basic"]=n
 def handle_level_up_choice(self,i):
  txt,key=self.up_options[i]
  if key=="max_hp":self.player.max_hp_level=min(self.player.max_hp_level+1,10);self.player.max_hp=int(self.player.max_hp*1.05);self.player.hp=self.player.max_hp
  elif key=="atk":self.player.atk_level+=1
  elif key=="speed":self.player.speed+=1
  else:self.player.skills[key]=min(self.player.skills[key]+1,7)
  self.player.level+=1;self.player.xp=0;self.player.xp_next=int(self.player.xp_next*1.2);self.state="PLAYING"
 def draw_hud(self):
  pygame.draw.rect(self.screen,(60,60,60),(16,16,220,28));pygame.draw.rect(self.screen,(200,0,0),(18,18,int((self.player.hp/self.player.max_hp)*(220-4)),24));hp=self.font.render(f"HP {int(self.player.hp)}/{self.player.max_hp}",1,(255,255,255));self.screen.blit(hp,(20,46));lvl=self.font.render(f"LVL {self.player.level}",1,(255,255,255));self.screen.blit(lvl,(20,70));xp=self.font.render(f"XP {self.player.xp}/{self.player.xp_next}",1,(255,255,255));self.screen.blit(xp,(20,96))
  scale_text=self.font.render(f"Speed: {self.time_scale:.1f}x",1,(255,255,255));self.screen.blit(scale_text,(20,120))
  if self.creative_mode:creative_text=self.font.render("CREATIVE MODE",1,(255,255,0));self.screen.blit(creative_text,(20,144));max_text=self.font.render("Press M to max abilities",1,(255,255,0));self.screen.blit(max_text,(20,168))
 def toggle_inventory(self):self.show_inventory=not self.show_inventory
 def draw_inventory(self):
  s=pygame.Surface((760,560),pygame.SRCALPHA);s.fill((10,10,20,190));r=s.get_rect(center=(600,450));self.screen.blit(s,r.topleft);title=self.title_font.render("ABILITIES & STATS",1,(255,215,0));self.screen.blit(title,(r.left+20,r.top+10))
  stats=[("Move Speed",f"{self.player.move_speed:.2f}"),("ATK Speed (per sec)",f"{self.player.atk_speed:.2f}"),("DMG",f"{self.player.dmg:.1f}"),("Max HP",f"{self.player.max_hp}")]
  y=r.top+80
  for k,v in stats:self.screen.blit(self.font.render(f"{k}: {v}",1,(255,255,255)),(r.left+30,y));y+=32
  y+=10;self.screen.blit(self.font.render("Abilities:",1,(255,255,255)),(r.left+30,y));y+=28
  for skill, level in self.player.skills.items():
   self.screen.blit(self.font.render(f"{skill}: Level {level}",1,(255,215,0)),(r.left+40,y));y+=32
  y+=20;self.screen.blit(self.font.render("Enemy Difficulty Multiplier:",1,(255,215,0)),(r.left+30,y));y+=30
  slider_x=r.left+40;slider_y=y;slider_width=300;slider_height=20;pygame.draw.rect(self.screen,(60,60,60),(slider_x,slider_y,slider_width,slider_height))
  handle_x=int(slider_x+(self.difficulty_mult-0.5)*slider_width/(5-0.5));pygame.draw.rect(self.screen,(255,215,0),(handle_x-8,slider_y-3,16,slider_height+6))
  diff_text=self.font.render(f"{self.difficulty_mult:.2f}x",1,(255,255,255));self.screen.blit(diff_text,(r.left+350,slider_y))
 def playing_loop(self):
  delta_time = (1000 / 60) * self.time_scale
  self.game_time += delta_time
  if self.game_time>=900000 and not hasattr(self,"final_boss_spawned"):print(f"Boss spawn triggered at {self.game_time}ms");self.final_boss_spawned=True;self.spawn_final_boss()
  self.screen.fill((15,15,20));n=pygame.time.get_ticks();self.update_difficulty(n)
  keys=pygame.key.get_pressed();move=pygame.math.Vector2(0,0)
  if keys[pygame.K_w]:move.y-=1
  if keys[pygame.K_s]:move.y+=1
  if keys[pygame.K_a]:move.x-=1
  if keys[pygame.K_d]:move.x+=1
  if move.length()>0:self.player.rect.center+=move.normalize()*self.player.move_speed * self.time_scale;self.player.last_direction=move.normalize()
  self.player.camera_pos+=(pygame.math.Vector2(self.player.rect.center)-self.player.camera_pos)*self.camera_lerp * self.time_scale;shake=pygame.math.Vector2(random.uniform(-self.player.camera_shake,self.player.camera_shake),random.uniform(-self.player.camera_shake,self.player.camera_shake))if self.player.camera_shake>0 else pygame.math.Vector2(0,0);cam_offset=pygame.math.Vector2(self.player.camera_pos.x-600,self.player.camera_pos.y-450)+shake
  target=min(self.enemies,key=lambda e:pygame.math.Vector2(e.rect.center).distance_to(self.player.rect.center))if self.enemies else None
  self.automatic_fire(n,target);tp=target.rect.center if target else None;self.player.update_fire(n,self.time_scale,self);self.player.update_lightning(target,n,self.enemies,self.time_scale,self)
  for b in self.bullets.sprites():
   b.rect.center=(b.rect.centerx+b.vel.x * self.time_scale,b.rect.centery+b.vel.y * self.time_scale)
   if not getattr(b,"is_boss_proj",False) and pygame.math.Vector2(b.rect.center).distance_to(self.player.rect.center)>1200:b.kill();continue
   if getattr(b,"is_boss_proj",False) and b.rect.colliderect(self.player.rect):
    dmg=getattr(b,"dmg",20)
    if not self.creative_mode and pygame.time.get_ticks()>self.player.iframe_until:self.player.hp-=dmg;self.player.iframe_until=pygame.time.get_ticks()+self.player.iframe_time;print(f"Player hit by boss orb! HP now {self.player.hp}")
    b.kill();continue
   if not getattr(b,"is_boss_proj",False):
    hit=pygame.sprite.spritecollideany(b,self.enemies)
    if hit:
     if getattr(hit,"is_final_boss",0):hit.hp-=getattr(b,"dmg",10)
     else:hit.hp-=getattr(b,"dmg",10)
     b.kill()
    if hit and hit.hp<=0:final=getattr(hit,"is_final_boss",0);self.player.xp+=int(20+self.player.level*4+(50 if getattr(hit,"is_boss",0)else 0));self.award_drop(hit.rect.center,b=getattr(hit,"is_boss",0));hit.kill();(setattr(self.player,"camera_shake",20)if final else None);self.state="WIN" if final else ("LEVEL_UP" if self.player.xp>=self.player.xp_next else self.state);(self.generate_upgrades()if not final and self.player.xp>=self.player.xp_next else None);(self.sounds["level_up"].play()if not final and self.player.xp>=self.player.xp_next and "level_up" in self.sounds else None)
  for p in list(self.player.fire_particles):
   pr=pygame.Rect(p["pos"][0]-p["size"],p["pos"][1]-p["size"],p["size"]*2,p["size"]*2)
   for e in self.enemies.sprites():
    if e.rect.colliderect(pr):
     if getattr(e,"is_final_boss",0):e.hp-=p["dmg"]
     else:e.hp-=p["dmg"]
    if e.hp<=0:final=getattr(e,"is_final_boss",0);self.player.xp+=int(12+self.player.level*3);self.award_drop(e.rect.center);e.kill();(setattr(self.player,"camera_shake",20)if final else None);self.state="WIN" if final else ("LEVEL_UP" if self.player.xp>=self.player.xp_next else self.state);(self.generate_upgrades()if not final and self.player.xp>=self.player.xp_next else None);(self.sounds["level_up"].play()if not final and self.player.xp>=self.player.xp_next and "level_up" in self.sounds else None)
  for L in list(self.player.lightning_effects):
   for e in self.enemies.sprites():
    dist = pygame.math.Vector2(e.rect.center).distance_to(L["end"])
    if e not in L["hit"] and dist<50:
     L["hit"].add(e)
     if getattr(e,"is_final_boss",0):e.hp-=L["dmg"]
     else:e.hp-=L["dmg"]
    if e.hp<=0:final=getattr(e,"is_final_boss",0);self.player.xp+=int(18+self.player.level*4);self.award_drop(e.rect.center);e.kill();(setattr(self.player,"camera_shake",20)if final else None);self.state="WIN" if final else ("LEVEL_UP" if self.player.xp>=self.player.xp_next else self.state);(self.generate_upgrades()if not final and self.player.xp>=self.player.xp_next else None);(self.sounds["level_up"].play()if not final and self.player.xp>=self.player.xp_next and "level_up" in self.sounds else None)
  for e in self.enemies.sprites():
   if getattr(e,"is_final_boss",0):
    n=pygame.time.get_ticks()
    if n-e.eye_shoot_cooldown>800 and e.eyes:
     for _ in range(3):
      if not e.eyes:break
      a=random.choice(e.eyes)
      eye_angle=a*(360/8)
      eye_x=e.rect.centerx+95*math.cos(math.radians(eye_angle))
      eye_y=e.rect.centery+95*math.sin(math.radians(eye_angle))
      dir_to_player=pygame.math.Vector2(self.player.rect.center)-pygame.math.Vector2((eye_x,eye_y))
      dir_to_player=dir_to_player.normalize()if dir_to_player.length()>0 else pygame.math.Vector2(0,0)
      proj=pygame.sprite.Sprite()
      proj.image=pygame.Surface((15,15),pygame.SRCALPHA)
      pygame.draw.circle(proj.image,(200,100,255),(7,7),7)
      proj.rect=proj.image.get_rect(center=(int(eye_x),int(eye_y)))
      proj.vel=dir_to_player*15
      proj.dmg=20
      proj.is_boss_proj=True
      self.bullets.add(proj)
      e.eyes.remove(a)
      e.last_eye_shot=n
     e.eye_shoot_cooldown=n
    if n-getattr(e,"last_eye_shot",n)>2500 and len(e.eyes)<8:
     e.eyes=list(range(8))
     e.last_eye_shot=n
  for e in self.enemies.sprites():
   d=pygame.math.Vector2(self.player.rect.center)-pygame.math.Vector2(e.rect.center)
   if d.length()>0:e.rect.centerx+=d.normalize().x*e.speed * self.time_scale;e.rect.centery+=d.normalize().y*e.speed * self.time_scale
   if e.rect.colliderect(self.player.rect):
    dmg=getattr(e,"damage",15)
    if not self.creative_mode and pygame.time.get_ticks()>self.player.iframe_until:self.player.hp-=dmg;self.player.iframe_until=pygame.time.get_ticks()+self.player.iframe_time
    if self.player.hp<=0:self.state="GAME_OVER"
  for o in pygame.sprite.spritecollide(self.player,self.orbs,1):self.player.xp+=15
  for o in list(self.orbs):
   if pygame.time.get_ticks()-getattr(o,"spawn_time",pygame.time.get_ticks())>20000:o.kill()
  if self.player.xp>=self.player.xp_next and self.state!="WIN":self.generate_upgrades();self.state="LEVEL_UP";(self.sounds["level_up"].play()if "level_up" in self.sounds else None)
  for e in self.enemies:
   if getattr(e,"is_final_boss",0):
    e.ring_rotation+=3*self.time_scale
    dp=(e.rect.x-int(cam_offset.x),e.rect.y-int(cam_offset.y))
    surf=pygame.Surface((200,200),pygame.SRCALPHA)
    pygame.draw.circle(surf,(100,0,150),(100,100),60)
    for eye_idx in e.eyes:a=eye_idx*(360/8);x=100+80*math.cos(math.radians(a));y=100+80*math.sin(math.radians(a));pygame.draw.circle(surf,(200,100,255),(int(x),int(y)),8)
    for r in [95,115]:pygame.draw.circle(surf,(150,50,200),(100,100),r,3)
    e.image=surf
    n=pygame.time.get_ticks()
    if n-getattr(e,"last_eye_regen",n)>300 and len(e.eyes)<8:e.eyes.append(len(e.eyes));setattr(e,"last_eye_regen",n)
   dp=(e.rect.x-int(cam_offset.x),e.rect.y-int(cam_offset.y));self.screen.blit(e.image,dp);hp_r=max(0,e.hp/getattr(e,"max_hp",1));pygame.draw.rect(self.screen,(40,40,40),(dp[0],dp[1]-6,e.rect.width,4));pygame.draw.rect(self.screen,(0,200,0),(dp[0],dp[1]-6,int(e.rect.width*hp_r),4))
  for b in self.bullets:dp=(b.rect.x-int(cam_offset.x),b.rect.y-int(cam_offset.y));self.screen.blit(b.image,dp)if hasattr(b,'image')else pygame.draw.circle(self.screen,(255,255,255),dp,4)
  for o in self.orbs:dp=(o.rect.x-int(cam_offset.x),o.rect.y-int(cam_offset.y));self.screen.blit(self.assets["orb"],dp)
  pd=self.player.image;self.screen.blit(pd,(600-pd.get_width()//2,450-pd.get_height()//2))
  for p in self.player.fire_particles:px=int(p["pos"][0]-cam_offset.x);py=int(p["pos"][1]-cam_offset.y);color=(0,random.randint(80,180),255)if self.player.skills["Firebreath"]==7 else(255,random.randint(80,180),0);pygame.draw.circle(self.screen,color,(px,py),p["size"])
  for L in self.player.lightning_effects:s=(int(L["start"].x-cam_offset.x),int(L["start"].y-cam_offset.y));e=(int(L["end"].x-cam_offset.x),int(L["end"].y-cam_offset.y));points=[s]+[(int((s[0]+(e[0]-s[0])*(i/6))+random.randint(-12,12)),int((s[1]+(e[1]-s[1])*(i/6))+random.randint(-12,12)))for i in range(1,6)]+[e];pygame.draw.lines(self.screen,(180,220,255),0,points,L["width"])


  self.draw_hud()
  elapsed = int(self.game_time / 1000)
  minutes = elapsed // 60
  seconds = elapsed % 60
  timer_text = self.font.render(f"{minutes:02d}:{seconds:02d}", 1, (255, 255, 255))
  timer_rect = timer_text.get_rect(center=(600, 30))
  self.screen.blit(timer_text, timer_rect)
  if pygame.time.get_ticks()<self.player.iframe_until:s=pygame.Surface((84,84),pygame.SRCALPHA);s.fill((255,255,255,40));self.screen.blit(s,(600-42,450-42))
  if self.show_inventory:self.draw_inventory()
  pygame.display.flip()
 def run(self):
  while 1:
   n=pygame.time.get_ticks()
   for event in pygame.event.get():
    if event.type==pygame.QUIT:pygame.quit();return
    if self.state=="LEVEL_UP"and event.type==pygame.MOUSEBUTTONDOWN:mx,my=pygame.mouse.get_pos();[self.handle_level_up_choice(i)for i in range(3)if pygame.Rect(250+i*240,360,220,60).collidepoint(mx,my)]
    if self.state=="MENU"and event.type==pygame.MOUSEBUTTONDOWN:mx,my=pygame.mouse.get_pos();[self.start_game(t)for i,t in enumerate(["Wizard","Knight","Archer"])if pygame.Rect(450,300+i*100,300,60).collidepoint(mx,my)]
    if event.type==pygame.KEYDOWN:
     if event.key==pygame.K_i:self.toggle_inventory()
     if event.key==pygame.K_c:self.creative_mode=not self.creative_mode
     if event.key==pygame.K_m and self.creative_mode:self.player.skills={"Firebreath":7,"Lightning":7};self.game_time=900000;self.final_boss_spawned=True;self.spawn_final_boss()
     if event.key==pygame.K_r and self.state=="GAME_OVER":self.state="MENU"
     if event.key==pygame.K_r and self.state=="WIN":self.state="MENU"
     if event.key==pygame.K_b:self.spawn_enemy(b=1)
     if event.key==pygame.K_LEFT:
      if self.show_inventory:self.difficulty_mult=max(0.5,self.difficulty_mult-0.1)
      else:self.time_scale=max(0.1,self.time_scale-0.1)
     if event.key==pygame.K_RIGHT:
      if self.show_inventory:self.difficulty_mult=min(5.0,self.difficulty_mult+0.1)
      else:self.time_scale=min(10.0,self.time_scale+0.1)
     if event.key==pygame.K_DOWN:self.time_scale=1.0
   if self.state=="MENU":self.screen.fill((10,10,20));select_hero_text=self.title_font.render("SELECT YOUR HERO",1,(255,255,255));select_hero_rect=select_hero_text.get_rect(center=(600,90));self.screen.blit(select_hero_text,select_hero_rect);[(pygame.draw.rect(self.screen,(50,50,70),(450,300+i*100,300,60)),self.screen.blit(self.font.render(t,1,(255,255,255)),(550,315+i*100)))for i,t in enumerate(["Wizard","Knight","Archer"])];pygame.display.flip()
   if self.state=="PLAYING":self.playing_loop()
   if self.state=="LEVEL_UP":
     self.screen.fill((20,20,40));choose_talent_text=self.title_font.render("CHOOSE A TALENT",1,(255,215,0));choose_talent_rect=choose_talent_text.get_rect(center=(600,120));self.screen.blit(choose_talent_text,choose_talent_rect)
     for i,(txt,key)in enumerate(self.up_options):r=pygame.Rect(250+i*240,360,220,60);pygame.draw.rect(self.screen,(60,60,90),r);l=txt if not(key in self.player.skills and self.player.skills[key]>=7)else f"{txt} (Evolved)";self.screen.blit(self.font.render(l,1,(255,255,255)),(r.x+12,r.y+18))
     pygame.display.flip()
   if self.state=="GAME_OVER":
    self.screen.fill((50,0,0))
    game_over_text=self.title_font.render("GAME OVER",1,(255,255,255))
    game_over_rect=game_over_text.get_rect(center=(600,340))
    self.screen.blit(game_over_text,game_over_rect)
    self.screen.blit(self.font.render("Press R to return to menu",1,(255,255,255)),(470,420))
    pygame.display.flip()
    try:
     if "game_over" in self.sounds and not hasattr(self,"game_over_played"):self.sounds["game_over"].play();self.game_over_played=True
    except Exception as e:print(f"Error playing game_over: {e}");self.game_over_played=True
   if self.state=="WIN":
    self.screen.fill((0,50,0))
    win_text=self.title_font.render("CONGRATULATIONS YOU WIN!",1,(255,255,0))
    win_rect=win_text.get_rect(center=(600,340))
    self.screen.blit(win_text,win_rect)
    self.screen.blit(self.font.render("Press R to return to menu",1,(255,255,255)),(470,420))
    pygame.display.flip()
    try:
     if "victory" in self.sounds and not hasattr(self,"victory_played"):self.sounds["victory"].play();self.victory_played=True
    except Exception as e:print(f"Error playing victory: {e}");self.victory_played=True
   if (self.state=="GAME_OVER" or self.state=="WIN"):
    if self.boss_music:
     try:self.boss_music.stop();self.boss_music=None
     except:pass
    for sound_key in ["firebreath","lightning","level_up"]:
     if sound_key in self.sounds:
      try:self.sounds[sound_key].stop()
      except:pass
   self.clock.tick(60)
if __name__=="__main__":GameManager().run()
