from typing import Dict, List, Optional, Tuple, TypeVar, Union

from gymnasium import Wrapper
from gymnasium.envs.box2d import lunar_lander

from carl.context.selection import AbstractSelector
from carl.envs.carl_env import CARLEnv
from carl.utils.trial_logger import TrialLogger
from carl.utils.types import Context, Contexts

ObsType = TypeVar("ObsType")
ActType = TypeVar("ActType")

# import pyglet
# pyglet.options["shadow_window"] = False

# TODO debug/test this environment by looking at rendering!

DEFAULT_CONTEXT = {
    "FPS": 50,
    "SCALE": 30.0,  # affects how fast-paced the game is, forces should be adjusted as well
    # Engine powers
    "MAIN_ENGINE_POWER": 13.0,
    "SIDE_ENGINE_POWER": 0.6,
    # random force on lunar lander body on reset
    "INITIAL_RANDOM": 1000.0,  # Set 1500 to make game harder
    "GRAVITY_X": 0,
    "GRAVITY_Y": -10,
    # lunar lander body specification
    "LEG_AWAY": 20,
    "LEG_DOWN": 18,
    "LEG_W": 2,
    "LEG_H": 8,
    "LEG_SPRING_TORQUE": 40,
    "SIDE_ENGINE_HEIGHT": 14.0,
    "SIDE_ENGINE_AWAY": 12.0,
    # Size of world
    "VIEWPORT_W": 600,
    "VIEWPORT_H": 400,
}

CONTEXT_BOUNDS = {
    "FPS": (1, 500, float),
    "SCALE": (
        1,
        100,
        float,
    ),  # affects how fast-paced the game is, forces should be adjusted as well
    "MAIN_ENGINE_POWER": (0, 50, float),
    "SIDE_ENGINE_POWER": (0, 50, float),
    # random force on lunar lander body on reset
    "INITIAL_RANDOM": (0, 2000, float),  # Set 1500 to make game harder
    "GRAVITY_X": (-20, 20, float),  # unit: m/s²
    "GRAVITY_Y": (
        -20,
        -0.01,
        float,
    ),  # the y-component of gravity must be smaller than 0 because otherwise the
    # lunarlander leaves the frame by going up
    # lunar lander body specification
    "LEG_AWAY": (0, 50, float),
    "LEG_DOWN": (0, 50, float),
    "LEG_W": (1, 10, float),
    "LEG_H": (1, 20, float),
    "LEG_SPRING_TORQUE": (0, 100, float),
    "SIDE_ENGINE_HEIGHT": (1, 20, float),
    "SIDE_ENGINE_AWAY": (1, 20, float),
    # Size of world
    "VIEWPORT_W": (400, 1000, int),
    "VIEWPORT_H": (200, 800, int),
}


class LunarLanderEnv(Wrapper):
    def __init__(
        self,
        env: Optional[lunar_lander.LunarLander] = None,
        high_gameover_penalty: bool = False,
    ):
        if env is None:
            env = lunar_lander.LunarLander()
        super().__init__(env=env)

        self.high_gameover_penalty = high_gameover_penalty
        # self.active_seed = None

    def step(self, action: ActType) -> Tuple[ObsType, float, bool, bool, dict]:
        self.env: lunar_lander.LunarLander
        state, reward, terminated, truncated, info = self.env.step(action)

        if self.env.game_over and self.high_gameover_penalty:
            reward = -10000
        return state, reward, terminated, truncated, info

    """def seed(self, seed: Optional[int] = None) -> Optional[int]:
        seed_ = self.env.seed(seed)
        self.active_seed = seed_[0]
        return seed_"""


class CARLLunarLanderEnv(CARLEnv):
    def __init__(
        self,
        env: Optional[LunarLanderEnv] = None,
        contexts: Contexts = {},
        hide_context: bool = True,
        add_gaussian_noise_to_context: bool = False,
        gaussian_noise_std_percentage: float = 0.05,
        logger: Optional[TrialLogger] = None,
        scale_context_features: str = "no",
        default_context: Optional[Context] = DEFAULT_CONTEXT,
        state_context_features: Optional[List[str]] = None,
        context_mask: Optional[List[str]] = None,
        max_episode_length: int = 1000,
        high_gameover_penalty: bool = False,
        dict_observation_space: bool = False,
        context_selector: Optional[
            Union[AbstractSelector, type[AbstractSelector]]
        ] = None,
        context_selector_kwargs: Optional[Dict] = None,
    ):
        """

        Parameters
        ----------
        env: gym.Env, optional
            Defaults to classic control environment mountain car from gym (MountainCarEnv).
        contexts: List[Dict], optional
            Different contexts / different environment parameter settings.
        instance_mode: str, optional
        """
        if env is None:
            # env = lunar_lander.LunarLander()
            env = LunarLanderEnv(high_gameover_penalty=high_gameover_penalty)
        if not contexts:
            contexts = {0: DEFAULT_CONTEXT}
        super().__init__(
            env=env,
            contexts=contexts,
            hide_context=hide_context,
            add_gaussian_noise_to_context=add_gaussian_noise_to_context,
            gaussian_noise_std_percentage=gaussian_noise_std_percentage,
            logger=logger,
            scale_context_features=scale_context_features,
            default_context=default_context,
            state_context_features=state_context_features,
            max_episode_length=max_episode_length,
            dict_observation_space=dict_observation_space,
            context_selector=context_selector,
            context_selector_kwargs=context_selector_kwargs,
            context_mask=context_mask,
        )
        self.whitelist_gaussian_noise = list(
            DEFAULT_CONTEXT.keys()
        )  # allow to augment all values

    def _update_context(self) -> None:
        self.env: LunarLanderEnv
        lunar_lander.FPS = self.context["FPS"]
        lunar_lander.SCALE = self.context["SCALE"]
        lunar_lander.MAIN_ENGINE_POWER = self.context["MAIN_ENGINE_POWER"]
        lunar_lander.SIDE_ENGINE_POWER = self.context["SIDE_ENGINE_POWER"]

        lunar_lander.INITIAL_RANDOM = self.context["INITIAL_RANDOM"]

        lunar_lander.LEG_AWAY = self.context["LEG_AWAY"]
        lunar_lander.LEG_DOWN = self.context["LEG_DOWN"]
        lunar_lander.LEG_W = self.context["LEG_W"]
        lunar_lander.LEG_H = self.context["LEG_H"]
        lunar_lander.LEG_SPRING_TORQUE = self.context["LEG_SPRING_TORQUE"]
        lunar_lander.SIDE_ENGINE_HEIGHT = self.context["SIDE_ENGINE_HEIGHT"]
        lunar_lander.SIDE_ENGINE_AWAY = self.context["SIDE_ENGINE_AWAY"]

        lunar_lander.VIEWPORT_W = self.context["VIEWPORT_W"]
        lunar_lander.VIEWPORT_H = self.context["VIEWPORT_H"]

        gravity_x = self.context["GRAVITY_X"]
        gravity_y = self.context["GRAVITY_Y"]

        gravity = (gravity_x, gravity_y)
        self.env.world.gravity = gravity
