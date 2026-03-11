# scheduler.py
"""
Scheduler for periodic MPC action queries.
"""

from apscheduler.schedulers.background import BackgroundScheduler

from PythonLinearNonlinearControl.envs.cost import logger
from Server.registry import Registry


class Scheduler:
    """
    Handles periodic calls to the MPC system for greenhouse control.
    """

    def __init__(self, interval_seconds=300):
        """
        Initialize MPC system and scheduler.

        Args:
            args: configuration / arguments for MPC system
            interval_seconds: time between control actions
        """
        self.interval_seconds = interval_seconds
        self.scheduler = BackgroundScheduler()

    def start_scheduler(self):
        """
        Start the scheduler that periodically calls the control loop.
        """
        # Add job to run every interval_seconds
        self.scheduler.add_job(self.control_loop, 'interval', seconds=self.interval_seconds)

        # Start scheduler
        logger.info("Starting greenhouse MPC scheduler...")
        self.scheduler.start()

    def control_loop(self):
        """
        Fetch sensor states and compute the next action.
        """
        try:
            goal_state = self.mpc_system.get_goal_state()
            current_state = Registry.get_system_states(goal_state)
            history_x, history_u, history_g = self.mpc_system.get_action(current_state, goal_state)

            # Log results (or send actions to actuators)
            logger.info(f"MPC action: {history_u}, Planned goal: {history_g}")

        except Exception as e:
            logger.error(f"Error in control loop: {e}", exc_info=True)