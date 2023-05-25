import pygame

class Timer:
	def __init__(self, duration):
		self.duration = duration
		self.time_running = 0
		self.active = False
		self.start_time = 0

	def activate(self):
		self.active = True
		self.start_time = pygame.time.get_ticks()

	def deactivate(self):
		self.active = False
		self.start_time = 0
		self.time_running = 0

	def update(self):
		current_time = pygame.time.get_ticks()
		self.time_running = current_time - self.start_time
		if self.time_running >= self.duration:
			self.deactivate()