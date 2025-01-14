import copy

from gym.spaces import Box, Discrete, Tuple, Dict, MultiDiscrete, MultiBinary
import numpy as np

from .sar_wrapper import SARWrapper


def flatdim(space):
    """Return the number of dimensions a flattened equivalent of this space
    would have.

    Accepts a space and returns an integer. Raises TypeError if
    the space is not defined in gym.spaces.
    """
    if isinstance(space, Box):
        return int(np.prod(space.shape))
    elif isinstance(space, Discrete):
        return int(space.n)
    elif isinstance(space, Tuple):
        return int(sum([flatdim(s) for s in space.spaces]))
    elif isinstance(space, Dict):
        return int(sum([flatdim(s) for s in space.spaces.values()]))
    elif isinstance(space, MultiBinary):
        return int(space.n)
    elif isinstance(space, MultiDiscrete):
        return int(np.prod(space.shape))
    else:
        raise TypeError


def flatten(space, x):
    """Flatten a data point from a space.

    This is useful when e.g. points from spaces must be passed to a neural
    network, which only understands flat arrays of floats.

    Accepts a space and a point from that space. Always returns a 1D array.
    Raises TypeError if the space is not a gym space.
    """
    if isinstance(space, Box):
        return np.asarray(x, dtype=space.dtype).flatten()
    elif isinstance(space, Discrete):
        onehot = np.zeros(space.n, dtype=int)
        onehot[x] = 1
        return onehot
    elif isinstance(space, Tuple):
        return np.concatenate([flatten(s, x_part) for x_part, s in zip(x, space.spaces)])
    elif isinstance(space, Dict):
        return np.concatenate(
            [flatten(s, x[key]) for key, s in space.spaces.items()])
    elif isinstance(space, MultiBinary):
        return np.asarray(x, dtype=int).flatten()
    elif isinstance(space, MultiDiscrete):
        return np.asarray(x, dtype=int).flatten()
    else:
        raise TypeError('space must be instance of gym.spaces')


def unflatten(space, x):
    """Unflatten a data point from a space.

    This reverses the transformation applied by flatten(). You must ensure
    that the space argument is the same as for the flatten() call.

    Accepts a space and a flattened point. Returns a point with a structure
    that matches the space. Raises TypeError if the space is not
    defined in gym.spaces.
    """
    if isinstance(space, Box):
        return np.asarray(x, dtype=space.dtype).reshape(space.shape)
    elif isinstance(space, Discrete):
        return int(np.nonzero(x)[0][0])
    elif isinstance(space, Tuple):
        dims = [flatdim(s) for s in space.spaces]
        list_flattened = np.split(x, np.cumsum(dims)[:-1])
        list_unflattened = [
            unflatten(s, flattened)
            for flattened, s in zip(list_flattened, space.spaces)
        ]
        return tuple(list_unflattened)
    elif isinstance(space, Dict):
        dims = [flatdim(s) for s in space.spaces.values()]
        list_flattened = np.split(x, np.cumsum(dims)[:-1])
        list_unflattened = [
            (key, unflatten(s, flattened))
            for flattened, (key,
                            s) in zip(list_flattened, space.spaces.items())
        ]
        from collections import OrderedDict
        return OrderedDict(list_unflattened)
    elif isinstance(space, MultiBinary):
        return np.asarray(x, dtype=int).reshape(space.shape)
    elif isinstance(space, MultiDiscrete):
        return np.asarray(x, dtype=int).reshape(space.shape)
    else:
        raise TypeError


def flatten_space(space):
    """Flatten a space into a single Box.

    This is equivalent to flatten(), but operates on the space itself. The
    result always is a Box with flat boundaries. The box has exactly
    flatdim(space) dimensions. Flattening a sample of the original space
    has the same effect as taking a sample of the flattenend space.

    Raises TypeError if the space is not defined in gym.spaces.

    Example::

        >>> box = Box(0.0, 1.0, shape=(3, 4, 5))
        >>> box
        Box(3, 4, 5)
        >>> flatten_space(box)
        Box(60,)
        >>> flatten(box, box.sample()) in flatten_space(box)
        True

    Example that flattens a discrete space::

        >>> discrete = Discrete(5)
        >>> flatten_space(discrete)
        Box(5,)
        >>> flatten(box, box.sample()) in flatten_space(box)
        True

    Example that recursively flattens a dict::

        >>> space = Dict({"position": Discrete(2),
        ...               "velocity": Box(0, 1, shape=(2, 2))})
        >>> flatten_space(space)
        Box(6,)
        >>> flatten(space, space.sample()) in flatten_space(space)
        True
    """
    if isinstance(space, Box):
        return Box(space.low.flatten(), space.high.flatten(), dtype=space.dtype)
    if isinstance(space, Discrete):
        return Box(low=0, high=1, shape=(space.n, ), dtype=int)
    if isinstance(space, Tuple):
        space = [flatten_space(s) for s in space.spaces]
        encapsulating_type = int \
            if all([this_space.dtype == int for this_space in space]) \
            else float
        return Box(
            low=np.concatenate([s.low for s in space]),
            high=np.concatenate([s.high for s in space]),
            dtype=encapsulating_type
        )
    if isinstance(space, Dict):
        space = [flatten_space(s) for s in space.spaces.values()]
        encapsulating_type = int \
            if all([this_space.dtype == int for this_space in space]) \
            else float
        return Box(
            low=np.concatenate([s.low for s in space]),
            high=np.concatenate([s.high for s in space]),
            dtype=encapsulating_type
        )
    if isinstance(space, MultiBinary):
        return Box(low=0, high=1, shape=(space.n, ), dtype=int)
    if isinstance(space, MultiDiscrete):
        return Box(
            low=np.zeros_like(space.nvec),
            high=space.nvec,
            dtype=int
        )
    raise TypeError


class FlattenWrapper(SARWrapper):
    """
    Flattens all agents' action and observation spaces into continuous Boxes.
    """
    def __init__(self, sim):
        super().__init__(sim)
        for agent_id, wrapped_agent in self.sim.agents.items(): # Wrap the agents' spaces
            self.agents[agent_id].action_space = flatten_space(wrapped_agent.action_space)
            self.agents[agent_id].observation_space = flatten_space(
                wrapped_agent.observation_space
            )

    def wrap_observation(self, from_agent, observation):
        return flatten(from_agent.observation_space, observation)

    def unwrap_observation(self, from_agent, observation):
        return unflatten(from_agent.observation_space, observation)

    def wrap_action(self, from_agent, action):
        return unflatten(from_agent.action_space, action)

    def unwrap_action(self, from_agent, action):
        return flatten(from_agent.action_space, action)


class FlattenActionWrapper(SARWrapper):
    """
    Flattens all agents' action spaces into continuous Boxes.
    """
    def __init__(self, sim):
        super().__init__(sim)
        self.agents = copy.deepcopy(self.sim.agents)
        for agent_id, wrapped_agent in self.sim.agents.items():
            # Wrap the action spaces of the agents
            self.agents[agent_id].action_space = flatten_space(wrapped_agent.action_space)

    def wrap_action(self, from_agent, action):
        return unflatten(from_agent.action_space, action)

    def unwrap_action(self, from_agent, action):
        return flatten(from_agent.action_space, action)
