
from grid2op.Agent import BaseAgent

class MyGraduateAgent(BaseAgent):
    """
    The template to be used to create an agent: any controller of the power grid is expected to be a subclass of this
    grid2op.Agent.BaseAgent.
    """
    def __init__(self, action_space):
        """Initialize a new agent."""
        BaseAgent.__init__(self, action_space=action_space)

    def act(self, observation, reward, done):
        """The action that your agent will choose depending on the observation, the reward, and whether the state is terminal"""
        # do nothing for example (with the empty dictionary) :
        action = self.action_space()
        disconnected_lines = np.where(observation.line_status == False)[0]
        overflow_lines = np.where(observation.rho > 0.99)[0]
        if len(disconnected_lines) != 0:
            for line in disconnected_lines:
                action = self.action_space({"set_line_status": [(line, +1)]})
                print("I make a reconnection!")
                
                try:
                    obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(action)
                    observation._obs_env._reset_to_orig_state()
                    if np.max(observation.rho) < 1.0 and np.max(obs_simulate.rho) >= 1.0:
                        continue

                except BaseException:
                    print('reconnect_action error')
                    continue
                    
        elif len(overflow_lines) != 0:
            for line in overflow_lines:
                action = self.action_space({"change_bus": [line]})
                print("I change the bus of lines :", line)
                try:
                    obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(action)
                    observation._obs_env._reset_to_orig_state()
                    if np.max(observation.rho) < 1.0 and np.max(obs_simulate.rho) >= 1.0:
                        continue

                except BaseException:
                    print('change_topology_action error')
                    continue
        else:
            action = self.action_space({})
        return action
        
    
def make_agent(env, this_directory_path):
    my_agent = MyGraduateAgent(env.action_space)
    return my_agent
