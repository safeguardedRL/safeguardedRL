import shutil
from os.path import isdir

import pytest

from sample_factory.algo.utils.misc import ExperimentStatus
from sample_factory.train import run_rl
from sample_factory.utils.utils import log
from sf_examples.envpool.atari.train_envpool_atari import parse_atari_args
from sf_examples.envpool.envpool_utils import envpool_available
from tests.utils import clean_test_dir


@pytest.mark.skipif(not envpool_available(), reason="envpool not installed")
class TestEnvpoolAtariEnv:
    @pytest.fixture(scope="class", autouse=True)
    def register_atari_fixture(self):
        from sf_examples.envpool.atari.train_envpool_atari import register_atari_components

        register_atari_components()

    @staticmethod
    def _run_test_env(
        env: str = "atari_breakout",
        num_workers: int = 1,
        train_steps: int = 2048,
        batched_sampling: bool = True,
        serial_mode: bool = True,
        async_rl: bool = False,
        batch_size: int = 1024,
        env_agents: int = 32,
        num_envs_per_worker: int = 1,
        worker_num_splits: int = 1,
    ):
        log.debug(f"Testing with parameters {locals()}...")
        assert train_steps > batch_size, "We need sufficient number of steps to accumulate at least one batch"

        experiment_name = f"test_envpool_{num_workers}_{env}"

        cfg = parse_atari_args(argv=["--algo=APPO", f"--env={env}", f"--experiment={experiment_name}"])
        cfg.serial_mode = serial_mode
        cfg.async_rl = async_rl
        cfg.batched_sampling = batched_sampling
        cfg.num_workers = num_workers
        cfg.env_agents = env_agents
        cfg.num_envs_per_worker = num_envs_per_worker
        cfg.worker_num_splits = worker_num_splits
        cfg.train_for_env_steps = train_steps
        cfg.batch_size = batch_size
        cfg.seed = 0
        cfg.device = "cpu"

        directory = clean_test_dir(cfg)
        status = run_rl(cfg)
        assert status == ExperimentStatus.SUCCESS
        assert isdir(directory)
        shutil.rmtree(directory, ignore_errors=True)

    @pytest.mark.parametrize(
        "env_name",
        [
            "atari_montezuma",
            "atari_spaceinvaders",
            # probably no reason to test on all of them, as they are kind of the same
            # "atari_pong",
            # "atari_qbert",
            # "atari_breakout",
            # "atari_asteroids",
            # "atari_gravitar",
            # "atari_mspacman",
            # "atari_seaquest",
        ],
    )
    @pytest.mark.parametrize("batched_sampling", [True])
    def test_basic_envs(self, env_name, batched_sampling):
        self._run_test_env(env=env_name, num_workers=1, batched_sampling=batched_sampling)

    def test_batched_double_buffering(self):
        self._run_test_env(
            env="atari_pong",
            num_workers=1,
            batched_sampling=True,
            num_envs_per_worker=2,
            worker_num_splits=2,
            env_agents=16,
        )
