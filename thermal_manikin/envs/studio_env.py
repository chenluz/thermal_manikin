import gym
from gym import error, spaces, utils
from gym.utils import seeding
from .observation import thermalManikin
import numpy as np
import csv
import datetime
import time
import os 


# ref: https://github.com/openai/gym/tree/master/gym/envs

Tskin_max = 37
Tskin_min = 29


class StudioEnv(gym.Env):

	def __init__(self):
		self.nS = 1 # state space
		self.nA = 8 # action space 
		self.is_terminal = False
		self.step_count = 0
		self.cur_Skin = 0
		self.action = 0
		self.reward = 0
		self.mainkin = thermalManikin(os.path.dirname(os.path.realpath(__file__)) + "\Maniki.csv")
			

	def _step(self, action):
		""" take action and return next state and reward
		Parameters
		----------
		action: int, value is 0, 1, 2, 3, 4
			(0: temperature decrease 2 degreee; 1: decrease 1 degree; 2: no change, 
				3: increase 1 degree, 4: increase 2 degree)

		Return 
		----------
		ob:  array of state
		reward: float , PMV value

		"""
		# get fan 
		self.action = action
		print(action)
		#time.sleep(1)
		# get mean skin temperature after action
		self.cur_Skin = self.mainkin.get_latest_MST()
		state = self._process_state_DDQN(self.cur_Skin)
		self.reward = self._process_reward(self.cur_Skin)

		return state, self.reward, self.is_terminal, {}


	def _process_reward(self, skin_temp):
		"""
			It is assumed that thermal mankin is comfortable  when skin temperature is 34.
			The reward is the negative discrpency from the current skin temperature and 34
		"""
		reward = - abs(self.cur_Skin -34)
		return reward



	def _process_state_DDQN(self, skin_temp):
		""" convert skin temperature to value with 0 and 1
		Parameters
		----------
		skin_temp: float,  
		Return 
		----------
		state: float from 0 to 1

		""" 
		state = (skin_temp - Tskin_min)*1.0/(Tskin_max - Tskin_min) 
	
		return state



	def _reset(self):
		self.is_terminal = False
		self.cur_Skin = self.mainkin.get_latest_MST()
		state = self._process_state_DDQN(self.cur_Skin)
		return state



	def _render(self, mode='human', close=False):
		pass

	def my_render(self, folder, model='human', close=False):
	    with open(folder + "_render.csv", 'a', newline='') as csvfile:
	        fieldnames = ['time', 'action', 'skin_temp', 'reward']
	        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	        writer.writerow({fieldnames[0]: datetime.datetime.utcnow(), 
	        	fieldnames[1]:self.action, 
				fieldnames[2]:self.cur_Skin,
				fieldnames[3]:self.reward})




