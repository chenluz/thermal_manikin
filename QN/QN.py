import random
import gym
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from keras import backend as K
from lib import plotting
import sys
import csv

MAX_STEP = 200
UPDATE_STEP = 30000


class QNAgent:
    def __init__(self, state_size, action_size,discount_factor, learning_rate):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = discount_factor    # discount rate
        self.learning_rate = learning_rate
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()
        self.step_count_total = 1
        self.target_update = UPDATE_STEP

    def _huber_loss(self, target, prediction):
        # sqrt(1+error^2)-1
        error = prediction - target
        return K.mean(K.sqrt(1+K.square(error))-1, axis=-1)

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss=self._huber_loss,
                      optimizer=Adam(lr=self.learning_rate))
        return model

    def update_target_model(self):
        # copy weights from model to target_model
        self.target_model.set_weights(self.model.get_weights())

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state,epsilon):
        #self.step_count_total += 1
        if np.random.rand() <= epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)

        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = self.model.predict(state)
            if done:
                target[0][action] = reward
            else:

                t = self.target_model.predict(next_state)[0]
                target[0][action] = reward + self.gamma * np.amax(t)
 
            self.model.fit(state, target, epochs=1, verbose=0)
        ## update target model
        if self.step_count_total % self.target_update == 0:
            print('update')
            self.update_target_model()


    def load(self, name):
        self.model.load_weights(name)
        return self.model

    def save(self, name):
        self.model.save_weights(name)


def q_learning(env, agent, num_episodes, batch_size, epsilon, epsilon_min, epsilon_decay, folder):
    """
    Q-Learning algorithm for fff-policy TD control using Function Approximation.
    Finds the optimal greedy policy while following an epsilon-greedy policy.
    
    Args:
        env: OpenAI environment.
        num_episodes: Number of episodes to run for.
        discount_factor: Lambda time discount factor.
        epsilon: Chance the sample a random action. Float betwen 0 and 1.
        epsilon_decay: Each episode, epsilon is decayed by this factor
    
    Returns:
        An EpisodeStats object with two numpy arrays for episode_lengths and episode_rewards.
    """
  
    # Keeps track of useful statistics
    stats = plotting.EpisodeStats(
        episode_lengths=np.zeros(num_episodes),
        episode_rewards=np.zeros(num_episodes))


    for i_episode in range(num_episodes):
        if epsilon > epsilon_min and i_episode > 500:
            # complete random exploration 500 episodes, 
            # then decrase exploration till epsilon less than epsilon_min
            epsilon *= epsilon_decay
        sys.stdout.flush()

        state = env.reset()
        state = np.reshape(state, [1, env.nS])

       
        for t in range(MAX_STEP):

            ## Decide action
            action = agent.act(state, epsilon)
            ## Advance the game to the next frame based on the action
            next_state, reward, done, _ = env.step(action)

            env.my_render(folder)

            stats.episode_rewards[i_episode] += reward
            stats.episode_lengths[i_episode] = t+1

            next_state = np.reshape(next_state, [1, env.nS])
            ## Remember the previous state, action, reward, and done
            agent.remember(state, action, reward, next_state, done)
            ## make next_state the new current state for the next frame.
            state = next_state
        
            if len(agent.memory) > batch_size:
                    agent.replay(batch_size)  

            if done: 
                break
        mean_score = stats.episode_rewards[i_episode]/stats.episode_lengths[i_episode]
        print("episode: {}/{}, score: {}, e: {:.2}, steps:{}, mean score:{:.2}"
            .format(i_episode, num_episodes,  stats.episode_rewards[i_episode], epsilon, 
                stats.episode_lengths[i_episode], 
                 mean_score))
        #if(i_episode > 200):
        write_csv(folder, i_episode, stats.episode_lengths[i_episode], mean_score)
        if(i_episode%50 == 0):
                agent.save(folder + "_qn" + str(i_episode) + ".h5")   
    agent.save(folder + "_qn-final" + ".h5")           

    return stats


def write_csv(folder, episode, step_num, average_score):
    with open(folder + "_score.csv", 'a', newline='') as csvfile:
        fieldnames = ['episode', 'step_num', 'average_score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({fieldnames[0]: episode, fieldnames[1]: step_num, 
            fieldnames[2]:average_score})


def evaluation(env, agent, folder):
    model = agent.load(folder + "_qn200.h5")
    for Skin in np.linspace(32,36,20):
        state = Skin
        print(state)
        state = env._process_state_DDQN(state)
        #env._print()
        state = np.reshape(state, [1, env.nS])
        target_f = model.predict(state)
        print(target_f)
        print(np.argmax(target_f))