from gym.envs.registration import register

register(
    id='manikin_control-v0',
    entry_point='thermal_manikin.envs:StudioTestEnv'
)

register(
    id='manikin_control-v1',
    entry_point='thermal_manikin.envs:StudioEnv'
)

