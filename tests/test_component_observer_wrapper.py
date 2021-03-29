
import numpy as np

from admiral.envs.components.agent import PositionAgent, LifeAgent, TeamAgent, SpeedAngleAgent, VelocityAgent
from admiral.envs.components.state import GridPositionState, LifeState, TeamState, ContinuousPositionState, SpeedAngleState, VelocityState
from admiral.envs.components.observer import HealthObserver, LifeObserver, PositionObserver, \
    RelativePositionObserver, SpeedObserver, AngleObserver, VelocityObserver, TeamObserver
from admiral.envs.components.wrappers.observer_wrapper import PositionRestrictedObservationWrapper

from admiral.envs.components.agent import AgentObservingAgent, VelocityObservingAgent, PositionObservingAgent, SpeedAngleObservingAgent, TeamObservingAgent, LifeObservingAgent, HealthObservingAgent
class AllObservingAgent(AgentObservingAgent, VelocityObservingAgent, PositionObservingAgent, SpeedAngleObservingAgent, TeamObservingAgent, LifeObservingAgent, HealthObservingAgent): pass
class NonViewAgent(VelocityObservingAgent, PositionObservingAgent, SpeedAngleObservingAgent, TeamObservingAgent, LifeObservingAgent, HealthObservingAgent): pass

class AllAgent(           AllObservingAgent, PositionAgent, LifeAgent, TeamAgent, SpeedAngleAgent, VelocityAgent): pass
class PositionlessAgent(  NonViewAgent,                     LifeAgent, TeamAgent, SpeedAngleAgent, VelocityAgent): pass
class LifelessAgent(      AllObservingAgent, PositionAgent,            TeamAgent, SpeedAngleAgent, VelocityAgent): pass
class TeamlessAgent(      AllObservingAgent, PositionAgent, LifeAgent,            SpeedAngleAgent, VelocityAgent): pass
class SpeedAnglelessAgent(AllObservingAgent, PositionAgent, LifeAgent, TeamAgent,                  VelocityAgent): pass
class VelocitylessAgent(  AllObservingAgent, PositionAgent, LifeAgent, TeamAgent, SpeedAngleAgent               ): pass

def test_position_restricted_observer_wrapper():
    agents = {
        'agent0': AllAgent(           id='agent0', agent_view=2, initial_position=np.array([2, 2]), initial_health=0.67, team=0, max_speed=1, initial_speed=0.30, initial_banking_angle=7,  initial_ground_angle=123, initial_velocity=np.array([-0.3, 0.8])),
        'agent1': AllAgent(           id='agent1', agent_view=1, initial_position=np.array([4, 4]), initial_health=0.54, team=1, max_speed=2, initial_speed=0.00, initial_banking_angle=0,  initial_ground_angle=126, initial_velocity=np.array([-0.2, 0.7])),
        'agent2': AllAgent(           id='agent2', agent_view=1, initial_position=np.array([4, 3]), initial_health=0.36, team=1, max_speed=1, initial_speed=0.12, initial_banking_angle=30, initial_ground_angle=180, initial_velocity=np.array([-0.1, 0.6])),
        'agent3': AllAgent(           id='agent3', agent_view=1, initial_position=np.array([4, 2]), initial_health=0.24, team=1, max_speed=4, initial_speed=0.05, initial_banking_angle=13, initial_ground_angle=46,  initial_velocity=np.array([0.0,  0.5])),
        'agent4': LifelessAgent(      id='agent4', agent_view=1, initial_position=np.array([4, 1]),                      team=2, max_speed=3, initial_speed=0.17, initial_banking_angle=15, initial_ground_angle=212, initial_velocity=np.array([0.1,  0.4])),
        'agent5': TeamlessAgent(      id='agent5', agent_view=1, initial_position=np.array([4, 0]), initial_health=0.89,         max_speed=2, initial_speed=0.21, initial_banking_angle=23, initial_ground_angle=276, initial_velocity=np.array([0.2,  0.3])),
        'agent6': SpeedAnglelessAgent(id='agent6', agent_view=0, initial_position=np.array([1, 1]), initial_health=0.53, team=0, max_speed=1,                                                                         initial_velocity=np.array([0.3,  0.2])),
        'agent7': VelocitylessAgent(  id='agent7', agent_view=5, initial_position=np.array([0, 4]), initial_health=0.50, team=1, max_speed=1, initial_speed=0.36, initial_banking_angle=24, initial_ground_angle=0                                          ),
        'agent8': PositionlessAgent(  id='agent8',                                                  initial_health=0.26, team=0, max_speed=2, initial_speed=0.06, initial_banking_angle=16, initial_ground_angle=5,   initial_velocity=np.array([0.5,  0.0])),
        'agent9': PositionlessAgent(  id='agent9',                                                  initial_health=0.08, team=2, max_speed=0, initial_speed=0.24, initial_banking_angle=30, initial_ground_angle=246, initial_velocity=np.array([0.6, -0.1])),
    }

    def linear_drop_off(distance, view):
        return 1. - 1. / (view+1) * distance

    np.random.seed(12)
    position_state = GridPositionState(agents=agents, region=5)
    life_state = LifeState(agents=agents)
    team_state = TeamState(agents=agents, number_of_teams=3)
    speed_state = SpeedAngleState(agents=agents)
    angle_state = SpeedAngleState(agents=agents)
    velocity_state = VelocityState(agents=agents)

    position_observer = PositionObserver(position=position_state, agents=agents)
    relative_position_observer = RelativePositionObserver(position=position_state, agents=agents)
    health_observer = HealthObserver(agents=agents)
    life_observer = LifeObserver(agents=agents)
    team_observer = TeamObserver(team=team_state, agents=agents)
    speed_observer = SpeedObserver(agents=agents)
    angle_observer = AngleObserver(agents=agents)
    velocity_observer = VelocityObserver(agents=agents)

    position_state.reset()
    life_state.reset()
    speed_state.reset()
    angle_state.reset()
    velocity_state.reset()

    wrapped_observer = PositionRestrictedObservationWrapper(
        [
            position_observer,
            relative_position_observer,
            health_observer,
            life_observer,
            team_observer,
            speed_observer,
            angle_observer,
            velocity_observer
        ],
        obs_filter=linear_drop_off,
        agents=agents
    )

    obs = wrapped_observer.get_obs(agents['agent0'])
    assert obs['health'] == {
        'agent0': 0.67,
        'agent1': -1, 
        'agent2': 0.36,
        'agent3': -1,
        'agent4': -1,
        'agent5': -1,
        'agent6': -1,
        'agent7': 0.5, 
        'agent8': 0.26,
        'agent9': 0.08,
    }
    assert obs['life'] == {
        'agent0': True,
        'agent1': -1,
        'agent2': True,
        'agent3': -1,
        'agent4': -1,
        'agent5': -1,
        'agent6': -1,
        'agent7': True,
        'agent8': True,
        'agent9': True,
    }
    assert obs['team'] == {
        'agent0': 0,
        'agent1': -1,
        'agent2': 1,
        'agent3': -1,
        'agent4': 2,
        'agent5': -1,
        'agent6': -1,
        'agent7': 1,
        'agent8': 0,
        'agent9': 2,
    }
    np.testing.assert_array_equal(obs['position']['agent0'], np.array([2, 2]))
    np.testing.assert_array_equal(obs['position']['agent1'], np.array([-1, -1]))
    np.testing.assert_array_equal(obs['position']['agent2'], np.array([4, 3]))
    np.testing.assert_array_equal(obs['position']['agent3'], np.array([-1, -1]))
    np.testing.assert_array_equal(obs['position']['agent4'], np.array([4, 1]))
    np.testing.assert_array_equal(obs['position']['agent5'], np.array([-1, -1]))
    np.testing.assert_array_equal(obs['position']['agent6'], np.array([-1, -1]))
    np.testing.assert_array_equal(obs['position']['agent7'], np.array([0, 4]))
    np.testing.assert_array_equal(obs['position']['agent8'], np.array([-1, -1]))
    np.testing.assert_array_equal(obs['position']['agent9'], np.array([-1, -1]))
    np.testing.assert_array_equal(obs['relative_position']['agent0'], np.array([0, 0]))
    np.testing.assert_array_equal(obs['relative_position']['agent1'], np.array([-5, -5]))
    np.testing.assert_array_equal(obs['relative_position']['agent2'], np.array([2, 1]))
    np.testing.assert_array_equal(obs['relative_position']['agent3'], np.array([-5, -5]))
    np.testing.assert_array_equal(obs['relative_position']['agent4'], np.array([2, -1]))
    np.testing.assert_array_equal(obs['relative_position']['agent5'], np.array([-5, -5]))
    np.testing.assert_array_equal(obs['relative_position']['agent6'], np.array([-5, -5]))
    np.testing.assert_array_equal(obs['relative_position']['agent7'], np.array([-2, 2]))
    np.testing.assert_array_equal(obs['relative_position']['agent8'], np.array([-5, -5]))
    np.testing.assert_array_equal(obs['relative_position']['agent9'], np.array([-5, -5]))
    assert obs['mask'] == {
        'agent0': 1,
        'agent1': 0,
        'agent2': 1,
        'agent3': 0,
        'agent4': 1,
        'agent5': 0,
        'agent6': 0,
        'agent7': 1,
        'agent8': 1,
        'agent9': 1,
    }
    assert obs['speed'] == {
        'agent0': 0.3,
        'agent1': -1,
        'agent2': 0.12,
        'agent3': -1,
        'agent4': 0.17,
        'agent5': -1,
        'agent6': -1,
        'agent7': 0.36,
        'agent8': 0.06,
        'agent9': 0.24,
    }
    assert obs['ground_angle'] == {
        'agent0': 123,
        'agent1': -1,
        'agent2': 180,
        'agent3': -1,
        'agent4': 212,
        'agent5': -1,
        'agent6': -1,
        'agent7': 0,
        'agent8': 5,
        'agent9': 246
    }
    np.testing.assert_array_equal(obs['velocity']['agent0'], np.array([-0.3, 0.8]))
    np.testing.assert_array_equal(obs['velocity']['agent1'], np.array([0.0, 0.0]))
    np.testing.assert_array_equal(obs['velocity']['agent2'], np.array([-0.1, 0.6]))
    np.testing.assert_array_equal(obs['velocity']['agent3'], np.array([0.0, 0.0]))
    np.testing.assert_array_equal(obs['velocity']['agent4'], np.array([0.1, 0.4]))
    np.testing.assert_array_equal(obs['velocity']['agent5'], np.array([0.0, 0.0]))
    np.testing.assert_array_equal(obs['velocity']['agent6'], np.array([0.0, 0.0]))
    np.testing.assert_array_equal(obs['velocity']['agent7'], np.array([0.0, 0.0]))
    np.testing.assert_array_equal(obs['velocity']['agent8'], np.array([0.5, 0.0]))
    np.testing.assert_array_equal(obs['velocity']['agent9'], np.array([0.6, -0.1]))


    obs = wrapped_observer.get_obs(agents['agent1'])
    assert obs['health'] == {
        'agent0': -1,
        'agent1': 0.54,
        'agent2': 0.36,
        'agent3': -1,
        'agent4': -1,
        'agent5': -1,
        'agent6': -1,
        'agent7': -1,
        'agent8': 0.26,
        'agent9': 0.08,
    }
    assert obs['life'] == {
        'agent0': -1,
        'agent1': True,
        'agent2': True,
        'agent3': -1,
        'agent4': -1,
        'agent5': -1,
        'agent6': -1,
        'agent7': -1,
        'agent8': True,
        'agent9': True,
    }
    assert obs['team'] == {
        'agent0': -1,
        'agent1': 1,
        'agent2': 1,
        'agent3': -1,
        'agent4': -1,
        'agent5': -1,
        'agent6': -1,
        'agent7': -1,
        'agent8': 0,
        'agent9': 2,
    }
    np.testing.assert_array_equal(obs['position']['agent0'], np.array([-1, -1]))
    np.testing.assert_array_equal(obs['position']['agent1'], np.array([4, 4]))
    np.testing.assert_array_equal(obs['position']['agent2'], np.array([4, 3]))
    np.testing.assert_array_equal(obs['position']['agent3'], np.array([-1, -1]))
    np.testing.assert_array_equal(obs['position']['agent4'], np.array([-1, -1]))
    np.testing.assert_array_equal(obs['position']['agent5'], np.array([-1, -1]))
    np.testing.assert_array_equal(obs['position']['agent6'], np.array([-1, -1]))
    np.testing.assert_array_equal(obs['position']['agent7'], np.array([-1, -1]))
    np.testing.assert_array_equal(obs['position']['agent8'], np.array([-1, -1]))
    np.testing.assert_array_equal(obs['position']['agent9'], np.array([-1, -1]))
    np.testing.assert_array_equal(obs['relative_position']['agent0'], np.array([-5, -5]))
    np.testing.assert_array_equal(obs['relative_position']['agent1'], np.array([0, 0]))
    np.testing.assert_array_equal(obs['relative_position']['agent2'], np.array([0, -1]))
    np.testing.assert_array_equal(obs['relative_position']['agent3'], np.array([-5, -5]))
    np.testing.assert_array_equal(obs['relative_position']['agent4'], np.array([-5, -5]))
    np.testing.assert_array_equal(obs['relative_position']['agent5'], np.array([-5, -5]))
    np.testing.assert_array_equal(obs['relative_position']['agent6'], np.array([-5, -5]))
    np.testing.assert_array_equal(obs['relative_position']['agent7'], np.array([-5, -5]))
    np.testing.assert_array_equal(obs['relative_position']['agent8'], np.array([-5, -5]))
    np.testing.assert_array_equal(obs['relative_position']['agent9'], np.array([-5, -5]))
    assert obs['mask'] == {
        'agent0': 0,
        'agent1': 1,
        'agent2': 1,
        'agent3': 0,
        'agent4': 0,
        'agent5': 0,
        'agent6': 0,
        'agent7': 0,
        'agent8': 1,
        'agent9': 1,
    }
    assert obs['speed'] == {
        'agent0': -1,
        'agent1': 0.0,
        'agent2': 0.12,
        'agent3': -1,
        'agent4': -1,
        'agent5': -1,
        'agent6': -1,
        'agent7': -1,
        'agent8': 0.06,
        'agent9': 0.24,
    }
    assert obs['ground_angle'] == {
        'agent0': -1,
        'agent1': 126,
        'agent2': 180,
        'agent3': -1,
        'agent4': -1,
        'agent5': -1,
        'agent6': -1,
        'agent7': -1,
        'agent8': 5,
        'agent9': 246
    }
    np.testing.assert_array_equal(obs['velocity']['agent0'], np.array([0.0, 0.0]))
    np.testing.assert_array_equal(obs['velocity']['agent1'], np.array([-0.2, 0.7]))
    np.testing.assert_array_equal(obs['velocity']['agent2'], np.array([-0.1, 0.6]))
    np.testing.assert_array_equal(obs['velocity']['agent3'], np.array([0.0, 0.0]))
    np.testing.assert_array_equal(obs['velocity']['agent4'], np.array([0.0, 0.0]))
    np.testing.assert_array_equal(obs['velocity']['agent5'], np.array([0.0, 0.0]))
    np.testing.assert_array_equal(obs['velocity']['agent6'], np.array([0.0, 0.0]))
    np.testing.assert_array_equal(obs['velocity']['agent7'], np.array([0.0, 0.0]))
    np.testing.assert_array_equal(obs['velocity']['agent8'], np.array([0.5, 0.0]))
    np.testing.assert_array_equal(obs['velocity']['agent9'], np.array([0.6, -0.1]))


    obs = wrapped_observer.get_obs(agents['agent9'])
    assert obs['health'] == {
        'agent0': 0.67,
        'agent1': 0.54,
        'agent2': 0.36,
        'agent3': 0.24,
        'agent4': -1,
        'agent5': 0.89,
        'agent6': 0.53,
        'agent7': 0.5,
        'agent8': 0.26,
        'agent9': 0.08,
    }
    assert obs['life'] == {
        'agent0': True,
        'agent1': True,
        'agent2': True,
        'agent3': True,
        'agent4': -1,
        'agent5': True,
        'agent6': True,
        'agent7': True,
        'agent8': True,
        'agent9': True,
    }
    assert obs['team'] == {
        'agent0': 0,
        'agent1': 1,
        'agent2': 1,
        'agent3': 1,
        'agent4': 2,
        'agent5': -1,
        'agent6': 0,
        'agent7': 1,
        'agent8': 0,
        'agent9': 2,
    }
    np.testing.assert_array_equal(obs['position']['agent0'], np.array([2, 2]))
    np.testing.assert_array_equal(obs['position']['agent1'], np.array([4, 4]))
    np.testing.assert_array_equal(obs['position']['agent2'], np.array([4, 3]))
    np.testing.assert_array_equal(obs['position']['agent3'], np.array([4, 2]))
    np.testing.assert_array_equal(obs['position']['agent4'], np.array([4, 1]))
    np.testing.assert_array_equal(obs['position']['agent5'], np.array([4, 0]))
    np.testing.assert_array_equal(obs['position']['agent6'], np.array([1, 1]))
    np.testing.assert_array_equal(obs['position']['agent7'], np.array([0, 4]))
    np.testing.assert_array_equal(obs['position']['agent8'], np.array([-1, -1]))
    np.testing.assert_array_equal(obs['position']['agent9'], np.array([-1, -1]))
    assert obs['mask'] == {
        'agent0': 1,
        'agent1': 1,
        'agent2': 1,
        'agent3': 1,
        'agent4': 1,
        'agent5': 1,
        'agent6': 1,
        'agent7': 1,
        'agent8': 1,
        'agent9': 1,
    }
    assert obs['speed'] == {
        'agent0': 0.3,
        'agent1': 0.0,
        'agent2': 0.12,
        'agent3': 0.05,
        'agent4': 0.17,
        'agent5': 0.21,
        'agent6': -1,
        'agent7': 0.36,
        'agent8': 0.06,
        'agent9': 0.24,
    }
    assert obs['ground_angle'] == {
        'agent0': 123,
        'agent1': 126,
        'agent2': 180,
        'agent3': 46,
        'agent4': 212,
        'agent5': 276,
        'agent6': -1,
        'agent7': 0,
        'agent8': 5,
        'agent9': 246
    }
    np.testing.assert_array_equal(obs['velocity']['agent0'], np.array([-0.3, 0.8]))
    np.testing.assert_array_equal(obs['velocity']['agent1'], np.array([-0.2, 0.7]))
    np.testing.assert_array_equal(obs['velocity']['agent2'], np.array([-0.1, 0.6]))
    np.testing.assert_array_equal(obs['velocity']['agent3'], np.array([0.0, 0.5]))
    np.testing.assert_array_equal(obs['velocity']['agent4'], np.array([0.1, 0.4]))
    np.testing.assert_array_equal(obs['velocity']['agent5'], np.array([0.2, 0.3]))
    np.testing.assert_array_equal(obs['velocity']['agent6'], np.array([0.3, 0.2]))
    np.testing.assert_array_equal(obs['velocity']['agent7'], np.array([0.0, 0.0]))
    np.testing.assert_array_equal(obs['velocity']['agent8'], np.array([0.5, 0.0]))
    np.testing.assert_array_equal(obs['velocity']['agent9'], np.array([0.6, -0.1]))