
from grid2op.Agent import BaseAgent
import numpy as np

class ClimberAgent(BaseAgent):
    
    def __init__(self, action_space):
        BaseAgent.__init__(self, action_space=action_space)
        self.alarms_lines_area = env.alarms_lines_area
        self.alarms_area_names = env.alarms_area_names
        self.alarm_overflow_flag = False

    def act(self, observation, reward, done):
        reconnect_action = self.action_space()
        change_topology_action = self.action_space()
        do_nothing = self.action_space({})
        do_nothing_rho = 1000
        current_action_rho = 0
        action_errors = 0
        
        # Do nothing if there is no need for action
        try:
            obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(do_nothing)
            observation._obs_env._reset_to_orig_state()
            if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                #Find the max rho exists in sumalated network 
                do_nothing_rho = np.max(obs_simulate.rho)                
        except BaseException:
#             print('do_nothing_action error')
            action_errors = action_errors + 1
            
        disconnected_lines = np.where(observation.line_status == False)[0]
        reconnect_action_rho = 1000        
        reconnect_actions = []
        index = 0
        
        # Reconnect disconnected lines
        if len(disconnected_lines) != 0:
            for line in disconnected_lines:
                current_action = self.action_space()
                current_action = self.action_space({"set_line_status": [(line, +1)]})
                reconnect_actions.append(current_action)
                try:
                    obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                    observation._obs_env._reset_to_orig_state()
                    if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        raise BaseException
                    if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                        current_action_rho = np.max(obs_simulate.rho)
                        if current_action_rho < reconnect_action_rho:
                            #Find the max rho exists in sumalated network 
                            reconnect_action_rho = current_action_rho
                            reconnect_action =current_action 
                except BaseException:
#                     print('reconnect_action error')
                    action_errors = action_errors + 1
                    continue  
            if len(reconnect_actions) > 1:
                while index <= (len(reconnect_actions) - 1):                    
                    index = index - 1
                    current_action = reconnect_actions[index]+ reconnect_actions[index+1]
                    print("This action is the combined reconnect.", current_action)
                    index = index + 2
                    print("Index in reconnect action is : ", index)
                    try:
                        obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                        observation._obs_env._reset_to_orig_state()
                        if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                            raise BaseException
                        if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                            current_action_rho = np.max(obs_simulate.rho)
                            print("Rho of combined reconnect ", current_action_rho)
                            if current_action_rho < reconnect_action_rho:
                                #Find the max rho exists in sumalated network 
                                reconnect_action_rho = current_action_rho
                                reconnect_action =current_action
                                print("Rho of combined reconnect ", reconnect_action_rho)
                                print("This action is the combined reconnect.", reconnect_action)
                    except BaseException:
#                         print('reconnect_action error')
                        action_errors = action_errors + 1
                        continue

             
        
        overflow_lines = np.where(observation.rho > 0.99)[0]
        change_topology_rho = 1000
        current_change_topology_rho = 0
        change_topology_actions = []
        index_top = 0
        
        # Change buses where there is an overflow 
        if len(overflow_lines) != 0:
            for line in overflow_lines:                
                current_action = self.action_space()
                current_action = self.action_space({ "change_bus": line})
                change_topology_actions.append(current_action)
                try:
                    obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                    observation._obs_env._reset_to_orig_state()
                    if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        raise BaseException
                    if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                        current_change_topology_rho = np.max(obs_simulate.rho)
                        if current_change_topology_rho < change_topology_rho:
                            change_topology_rho = current_change_topology_rho
                            change_topology_action = current_action #self.action_space({"change_bus": overflow_lines})
                except BaseException:
#                     print('change_topology_action error')
                    action_errors = action_errors + 1
            if len(change_topology_actions) > 1:
                while index_top <= (len(change_topology_actions) - 1):
                    index_top = index_top - 1
                    current_action = change_topology_actions[index_top] + change_topology_actions[index_top+1]
                    print("This action is the combined topology.", current_action)
                    index_top = index_top + 2
                    print("Index in topology action is : ", index_top)
                    try:
                        obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                        observation._obs_env._reset_to_orig_state()
                        if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                            raise BaseException
                        if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                            current_action_rho = np.max(obs_simulate.rho)
                            print("Rho of combined topology ", current_action_rho)
                            if current_action_rho < change_topology_rho:
                                #Find the max rho exists in sumalated network 
                                change_topology_rho = current_action_rho
                                change_topology_action = current_action 
                                print("Rho of combined topology ", change_topology_rho)
                                print("This action is the combined topology.", change_topology_action)
                    except BaseException:
#                         print('change_topology_action error')
                        action_errors = action_errors + 1
                        continue
                
            
        
        redispatch_rho = 1000
        current_redispatch_rho = 0
        redispatch_action = self.action_space()
        redispatch_amount = np.arange(0.5, 15.5, 0.5)#[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0,  8.5, 9.0, 9.5, 10.0, 10.5]
        redispatch_actions = []
        index_red = 0
        redispatch_action_1 = self.action_space()
        redispatch_rho_1 = 1000
        redispatch_action_2 = self.action_space()
        redispatch_rho_2 = 1000
        redispatch_action_3 = self.action_space()
        redispatch_rho_3 = 1000
        redispatch_action_4 = self.action_space()
        redispatch_rho_4 = 1000
        redispatch_action_5 = self.action_space()
        redispatch_rho_5 = 1000
        
        # Redispatch action if all the other actions gives an overflowed state
        if do_nothing_rho >= 1.0 and reconnect_action_rho >= 1.0 \
        and change_topology_rho >= 1.0 and redispatch_rho >= 1.0:
            print(do_nothing_rho, reconnect_action_rho, change_topology_rho, redispatch_rho)
            for amount in redispatch_amount:
                for id in range(22):
                    current_action = self.action_space()
                    current_action = self.action_space({ "redispatch": [(id, amount)]})
                    try:
                        obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                        observation._obs_env._reset_to_orig_state()
                        if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                            raise BaseException
                        if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                            current_redispatch_rho = np.max(obs_simulate.rho)
                            if current_redispatch_rho < redispatch_rho:
                                redispatch_rho = current_redispatch_rho
                                redispatch_action = current_action
                            elif current_redispatch_rho < redispatch_rho_1:
                                redispatch_rho_1 = current_redispatch_rho
                                redispatch_action_1 = current_action
                            elif current_redispatch_rho < redispatch_rho_2:
                                redispatch_rho_2 = current_redispatch_rho
                                redispatch_action_2 = current_action
                            elif current_redispatch_rho < redispatch_rho_3:
                                redispatch_rho_3 = current_redispatch_rho
                                redispatch_action_3 = current_action
                            elif current_redispatch_rho < redispatch_rho_4:
                                redispatch_rho_4 = current_redispatch_rho
                                redispatch_action_4 = current_action
#                             if redispatch_rho < 1.0:
#                                 print("Break")
#                                 break
                    except BaseException:
#                         print('redispatch_action error')
                        action_errors = action_errors + 1
#                 if redispatch_rho < 1.0:
#                     print("Break")
#                     break


        current_combined_redispatch_rho = 0
        combined_redispatch_rho = 1000
        combined_redispatch_action = self.action_space()
        if redispatch_rho != 1000 and redispatch_rho_1 !=1000:
            try:
                current_action = self.action_space()
                current_action = redispatch_action + redispatch_action_1
                print("1+2",current_action)
                obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                observation._obs_env._reset_to_orig_state()
                if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        raise BaseException
                if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                    current_combined_redispatch_rho = np.max(obs_simulate.rho)
                    if current_combined_redispatch_rho < combined_redispatch_rho:
                        combined_redispatch_rho = current_combined_redispatch_rho
                        #                             print(redispatch_rho)
                        # A better solution is to convert the action into a vect and add every redispatch action gives a lower rho.
                        # To do that i have to check if the combined action is proper in simulate.
                        combined_redispatch_action = current_action
            except BaseException:
#                 print('combined actions error') 
                action_errors = action_errors + 1
    
        if redispatch_rho != 1000 and redispatch_rho_2 !=1000:
            try:
                current_action = self.action_space()
                current_action = redispatch_action + redispatch_action_2
                print("1+3",current_action)
                obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                observation._obs_env._reset_to_orig_state()
                if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        raise BaseException
                if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                    current_combined_redispatch_rho = np.max(obs_simulate.rho)
                    if current_combined_redispatch_rho < combined_redispatch_rho:
                        combined_redispatch_rho = current_combined_redispatch_rho
                        #                             print(redispatch_rho)
                        # A better solution is to convert the action into a vect and add every redispatch action gives a lower rho.
                        # To do that i have to check if the combined action is proper in simulate.
                        combined_redispatch_action = current_action
            except BaseException:
#                 print('combined actions error') 
                action_errors = action_errors + 1
    
        if redispatch_rho != 1000 and redispatch_rho_3 !=1000:
            try:
                current_action = self.action_space()
                current_action = redispatch_action + redispatch_action_3
                print("1+4",current_action)
                obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                observation._obs_env._reset_to_orig_state()
                if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        raise BaseException
                if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                    current_combined_redispatch_rho = np.max(obs_simulate.rho)
                    if current_combined_redispatch_rho < combined_redispatch_rho:
                        combined_redispatch_rho = current_combined_redispatch_rho
                        #                             print(redispatch_rho)
                        # A better solution is to convert the action into a vect and add every redispatch action gives a lower rho.
                        # To do that i have to check if the combined action is proper in simulate.
                        combined_redispatch_action = current_action
            except BaseException:
#                 print('combined actions error') 
                action_errors = action_errors + 1
    
        if redispatch_rho != 1000 and redispatch_rho_4 !=1000:
            try:
                current_action = self.action_space()
                current_action = redispatch_action + redispatch_action_4
                print("1+5",current_action)
                obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                observation._obs_env._reset_to_orig_state()
                if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        raise BaseException
                if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                    current_combined_redispatch_rho = np.max(obs_simulate.rho)
                    if current_combined_redispatch_rho < combined_redispatch_rho:
                        combined_redispatch_rho = current_combined_redispatch_rho
                        #                             print(redispatch_rho)
                        # A better solution is to convert the action into a vect and add every redispatch action gives a lower rho.
                        # To do that i have to check if the combined action is proper in simulate.
                        combined_redispatch_action = current_action
            except BaseException:
#                 print('combined actions error') 
                action_errors = action_errors + 1
    
        
    
        if redispatch_rho_1 != 1000 and redispatch_rho_2 !=1000:
            try:
                current_action = self.action_space()
                current_action = redispatch_action_1 + redispatch_action_2
                print("2+3",current_action)
                obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                observation._obs_env._reset_to_orig_state()
                if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        raise BaseException
                if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                    current_combined_redispatch_rho = np.max(obs_simulate.rho)
                    if current_combined_redispatch_rho < combined_redispatch_rho:
                        combined_redispatch_rho = current_combined_redispatch_rho
                        #                             print(redispatch_rho)
                        # A better solution is to convert the action into a vect and add every redispatch action gives a lower rho.
                        # To do that i have to check if the combined action is proper in simulate.
                        combined_redispatch_action = current_action
            except BaseException:
#                 print('combined actions error') 
                action_errors = action_errors + 1
    
        if redispatch_rho_1 != 1000 and redispatch_rho_3 !=1000:
            try:
                current_action = self.action_space()
                current_action = redispatch_action_1 + redispatch_action_3
                print("2+4",current_action)
                obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                observation._obs_env._reset_to_orig_state()
                if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        raise BaseException
                if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                    current_combined_redispatch_rho = np.max(obs_simulate.rho)
                    if current_combined_redispatch_rho < combined_redispatch_rho:
                        combined_redispatch_rho = current_combined_redispatch_rho
                        #                             print(redispatch_rho)
                        # A better solution is to convert the action into a vect and add every redispatch action gives a lower rho.
                        # To do that i have to check if the combined action is proper in simulate.
                        combined_redispatch_action = current_action
            except BaseException:
#                 print('combined actions error') 
                action_errors = action_errors + 1
        if redispatch_rho_1 != 1000 and redispatch_rho_4 !=1000:
            try:
                current_action = self.action_space()
                current_action = redispatch_action_1 + redispatch_action_4
                print("2+5",current_action)
                obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                observation._obs_env._reset_to_orig_state()
                if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        raise BaseException
                if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                    current_combined_redispatch_rho = np.max(obs_simulate.rho)
                    if current_combined_redispatch_rho < combined_redispatch_rho:
                        combined_redispatch_rho = current_combined_redispatch_rho
                        #                             print(redispatch_rho)
                        # A better solution is to convert the action into a vect and add every redispatch action gives a lower rho.
                        # To do that i have to check if the combined action is proper in simulate.
                        combined_redispatch_action = current_action
            except BaseException:
#                 print('combined actions error') 
                action_errors = action_errors + 1
    
        if redispatch_rho_2 != 1000 and redispatch_rho_3 !=1000:
            try:
                current_action = self.action_space()
                current_action = redispatch_action_2 + redispatch_action_3
                print("3+4",current_action)
                obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                observation._obs_env._reset_to_orig_state()
                if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        raise BaseException
                if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                    current_combined_redispatch_rho = np.max(obs_simulate.rho)
                    if current_combined_redispatch_rho < combined_redispatch_rho:
                        combined_redispatch_rho = current_combined_redispatch_rho
                        #                             print(redispatch_rho)
                        # A better solution is to convert the action into a vect and add every redispatch action gives a lower rho.
                        # To do that i have to check if the combined action is proper in simulate.
                        combined_redispatch_action = current_action
            except BaseException:
#                 print('combined actions error') 
                action_errors = action_errors + 1
    
        if redispatch_rho_2 != 1000 and redispatch_rho_4 !=1000:
            try:
                current_action = self.action_space()
                current_action = redispatch_action_2 + redispatch_action_4
                print("3+5",current_action)
                obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                observation._obs_env._reset_to_orig_state()
                if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        raise BaseException
                if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                    current_combined_redispatch_rho = np.max(obs_simulate.rho)
                    if current_combined_redispatch_rho < combined_redispatch_rho:
                        combined_redispatch_rho = current_combined_redispatch_rho
                        #                             print(redispatch_rho)
                        # A better solution is to convert the action into a vect and add every redispatch action gives a lower rho.
                        # To do that i have to check if the combined action is proper in simulate.
                        combined_redispatch_action = current_action
            except BaseException:
#                 print('combined actions error') 
                action_errors = action_errors + 1
    
        if redispatch_rho_3 != 1000 and redispatch_rho_4 !=1000:
            try:
                current_action = self.action_space()
                current_action = redispatch_action_3 + redispatch_action_4
                print("4+5",current_action)
                obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                observation._obs_env._reset_to_orig_state()
                if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        raise BaseException
                if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                    current_combined_redispatch_rho = np.max(obs_simulate.rho)
                    if current_combined_redispatch_rho < combined_redispatch_rho:
                        combined_redispatch_rho = current_combined_redispatch_rho
                        #                             print(redispatch_rho)
                        # A better solution is to convert the action into a vect and add every redispatch action gives a lower rho.
                        # To do that i have to check if the combined action is proper in simulate.
                        combined_redispatch_action = current_action
            except BaseException:
#                 print('combined actions error') 
                action_errors = action_errors + 1
    
        if combined_redispatch_rho < redispatch_rho:
            redispatch_rho = combined_redispatch_rho
            redispatch_action = combined_redispatch_action
    
        curtail_rho = 1000
        current_curtail_rho = 0
        curtail_action = self.action_space()
        
        # Curtail action if all the other actions gives an overflowed state
        ratio_curtailment = np.arange(0.05, 0.5, 0.05)#[ 0.15, 0.20, 0.25, 0.30]  # this is a ratio, between 0.0 and 1.0 
                                              # if not in range [0, 1.0] an "ambiguous action" will be raised when calling "env.step"
        if do_nothing_rho >= 1.0 and reconnect_action_rho >= 1.0 \
        and change_topology_rho >= 1.0 and redispatch_rho >= 1.0:
            print(do_nothing_rho, reconnect_action_rho, change_topology_rho, redispatch_rho)
            for ratio in ratio_curtailment:
                for id in range(22):
                    try:                   
                        current_action = self.action_space()
                        current_action = self.action_space({ "curtail": [(id, ratio)]})
                        obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                        observation._obs_env._reset_to_orig_state()
                        if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                            raise BaseException
                        if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                            current_curtail_rho = np.max(obs_simulate.rho)
                            if current_curtail_rho < curtail_rho and current_curtail_rho < 1.0:
                                curtail_rho = current_curtail_rho
                                curtail_action = current_action
                            if curtail_rho < 1.0:
                                print("Break")
                                break
                    except BaseException:
#                         print('curtail_action error')
                        action_errors = action_errors + 1
                if curtail_rho < 1.0:
                    print("Break")
                    break
                        
        combined_action = self.action_space()
        combined_action_rho = 1000
        current_combined_rho = 0
        
        # Try if the combination of the best action per type can cause better results.
        if reconnect_action_rho != 1000 and change_topology_rho !=1000:
            try:
                current_action = self.action_space()
                print(len(combined_actions_array))
                current_action = reconnect_action + change_topology_action
                obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                observation._obs_env._reset_to_orig_state()
                if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        raise BaseException
                if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                    current_combined_rho = np.max(obs_simulate.rho)
                    if current_combined_rho < combined_action_rho:
                        combined_action_rho = current_combined_rho
                        #                             print(redispatch_rho)
                        # A better solution is to convert the action into a vect and add every redispatch action gives a lower rho.
                        # To do that i have to check if the combined action is proper in simulate.
                        combined_action = current_action
            except BaseException:
#                 print('combined actions error') 
                action_errors = action_errors + 1
            
        if reconnect_action_rho != 1000 and redispatch_rho != 1000:
            try:
                current_action = self.action_space()
                current_action = reconnect_action + redispatch_action
                obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                observation._obs_env._reset_to_orig_state()
                if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        raise BaseException
                if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                    #                         print("I am not done with this redispatch action :", current_action)
                    current_combined_rho = np.max(obs_simulate.rho)
                    #                         print(current_redispatch_rho)
                    #                     print("Redispatch rho before checking :", current_redispatch_rho)
                    #                         if np.max(obs_simulate.rho) < 0.99 and current_redispatch_rho < redispatch_rho:
                    if current_combined_rho < combined_action_rho:
                        combined_action_rho = current_combined_rho
                        combined_action = current_action
            except BaseException:
#                 print('combined action error')
                action_errors = action_errors + 1
            
        if reconnect_action_rho != 1000 and curtail_rho != 1000:
            try:
                current_action = self.action_space()
                current_action = reconnect_action + curtail_action
                obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                observation._obs_env._reset_to_orig_state()
                if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        raise BaseException
                if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                    #                         print("I am not done with this redispatch action :", current_action)
                    current_combined_rho = np.max(obs_simulate.rho)
                    #                         print(current_redispatch_rho)
                    #                     print("Redispatch rho before checking :", current_redispatch_rho)
                    #                         if np.max(obs_simulate.rho) < 0.99 and current_redispatch_rho < redispatch_rho:
                    if current_combined_rho < combined_action_rho:
                        combined_action_rho = current_combined_rho
                        combined_action = current_action
            except BaseException:
#                 print('combined action error')
                action_errors = action_errors + 1
            
            
        if change_topology_rho != 1000 and redispatch_rho != 1000:
            try:
                current_action = self.action_space()
                current_action = change_topology_action + redispatch_action
                obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                observation._obs_env._reset_to_orig_state()
                if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        raise BaseException
                if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                    #                         print("I am not done with this redispatch action :", current_action)
                    current_combined_rho = np.max(obs_simulate.rho)
                    #                         print(current_redispatch_rho)
                    #                     print("Redispatch rho before checking :", current_redispatch_rho)
                    #                         if np.max(obs_simulate.rho) < 0.99 and current_redispatch_rho < redispatch_rho:
                    if current_combined_rho < combined_action_rho:
                        combined_action_rho = current_combined_rho
                        combined_action = current_action
            except BaseException:
#                 print('combined action error')
                action_errors = action_errors + 1
            
        if change_topology_rho != 1000 and curtail_rho != 1000:
            try:
                current_action = self.action_space()
                current_action = change_topology_action + curtail_action
                obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                observation._obs_env._reset_to_orig_state()
                if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        raise BaseException
                if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                    #                         print("I am not done with this redispatch action :", current_action)
                    current_combined_rho = np.max(obs_simulate.rho)
                    #                         print(current_redispatch_rho)
                    #                     print("Redispatch rho before checking :", current_redispatch_rho)
                    #                         if np.max(obs_simulate.rho) < 0.99 and current_redispatch_rho < redispatch_rho:
                    if current_combined_rho < combined_action_rho:
                        combined_action_rho = current_combined_rho
                        combined_action = current_action
            except BaseException:
#                 print('combined action error')
                action_errors = action_errors + 1
            
            
        if curtail_rho != 1000 and redispatch_rho != 1000:
            try:
                current_action = self.action_space()
                current_action = curtail_action + redispatch_action
                obs_simulate, reward_simulate, done_simulate, info_simulate = observation.simulate(current_action)
                observation._obs_env._reset_to_orig_state()
                if info_simulate['is_illegal'] or info_simulate['is_ambiguous']:
                        raise BaseException
                if not done_simulate and obs_simulate is not None and not any(np.isnan(obs_simulate.rho)):
                    #                         print("I am not done with this redispatch action :", current_action)
                    current_combined_rho = np.max(obs_simulate.rho)
                    if current_combined_rho < combined_action_rho:
                        combined_action_rho = current_combined_rho
                        combined_action = current_action
            except BaseException:
#                 print('combined action error')
                action_errors = action_errors + 1
            
        
        
#         print(combined_actions_array)

        
    
        
#         print("Do nothing rho :",do_nothing_rho)
#         print("Reconnect rho :",reconnect_action_rho)
#         print("Change topology rho :",change_topology_rho)
#         print("Redispatch rho : ", redispatch_rho)
#         print("Curtail rho : ", curtail_rho)
#         print("Combined rho : ", combined_action_rho)
        # After all simulations return the final action which includes all reconnect and topology changes
        if do_nothing_rho <= reconnect_action_rho and do_nothing_rho <= change_topology_rho \
        and do_nothing_rho <= redispatch_rho and do_nothing_rho <= curtail_rho and do_nothing_rho <= combined_action_rho:
            if do_nothing_rho >= 1.3 and self.alarm_overflow_flag = False:
                self.alarm_overflow_flag = True
            elif do_nothing_rho < 1.3:
                self.alarm_overflow_flag = False
            return do_nothing
        if reconnect_action_rho < do_nothing_rho and reconnect_action_rho <= change_topology_rho \
        and reconnect_action_rho < redispatch_rho and reconnect_action_rho <= curtail_rho and reconnect_action_rho <= combined_action_rho:
#             print(type(reconnect_action))
            print("Reconnect",reconnect_action)
            if reconnect_action_rho >= 1.3 and self.alarm_overflow_flag = False:
                self.alarm_overflow_flag = True
            elif reconnect_action_rho < 1.3:
                self.alarm_overflow_flag = False
            return reconnect_action
        if change_topology_rho < do_nothing_rho and change_topology_rho < reconnect_action_rho \
        and change_topology_rho < redispatch_rho and change_topology_rho <= curtail_rho and change_topology_rho <= combined_action_rho: 
            print("Change topology",change_topology_action)
            if reconnect_action_rho >= 1.3 and self.alarm_overflow_flag = False:
                self.alarm_overflow_flag = True
            elif reconnect_action_rho < 1.3:
                self.alarm_overflow_flag = False
            return change_topology_action
        if redispatch_rho < do_nothing_rho and redispatch_rho < reconnect_action_rho \
        and redispatch_rho < change_topology_rho  and redispatch_rho <= curtail_rho and redispatch_rho <= combined_action_rho:
            print("Redispatch action", redispatch_action)
            if redispatch_rho >= 1.3 and self.alarm_overflow_flag = False:
                self.alarm_overflow_flag = True
            elif redispatch_rho < 1.3:
                self.alarm_overflow_flag = False
            return redispatch_action
        if curtail_rho < do_nothing_rho and curtail_rho < reconnect_action_rho \
        and curtail_rho < change_topology_rho and curtail_rho < redispatch_rho and curtail_rho <= combined_action_rho:
            print("Curtail action", curtail_action)
            if curtail_rho >= 1.3 and self.alarm_overflow_flag = False:
                self.alarm_overflow_flag = True
            elif curtail_rho < 1.3:
                self.alarm_overflow_flag = False
            return curtail_action
        if combined_action_rho < do_nothing_rho and combined_action_rho < change_topology_rho \
        and combined_action_rho < redispatch_rho and combined_action_rho < reconnect_action_rho \
        and combined_action_rho < curtail_rho:
            print("Combined action", combined_action)
            return combined_action
        if do_nothing_rho == 1000 and do_nothing_rho == reconnect_action_rho \
        and do_nothing_rho == change_topology_rho and do_nothing_rho == redispatch_rho \
        and do_nothing_rho == curtail_rho:
            print("Game over")
            print("Action errors are : ", action_errors)
            return do_nothing
        
    
def make_agent(env, this_directory_path):
    my_agent = ClimberAgent(env.action_space)
    return my_agent