"""Remote computation module for pyT5.

This module provides classes for executing Tripoli-5 simulations
on remote computing resources.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union


class RemoteCompute:
    """Manages remote execution of Tripoli-5 simulations.

    This class handles submission, monitoring, and retrieval of
    simulations on remote computing resources (HPC clusters, cloud).

    Attributes:
        name: Unique identifier for the remote configuration.
        host: Remote host address.
        username: Username for authentication.
        scheduler: Job scheduler type ('slurm', 'pbs', 'sge', etc.).
        queue: Queue/partition name.
        walltime: Maximum job walltime in hours.
        nodes: Number of compute nodes.
        cores_per_node: Number of cores per node.

    Examples:
        >>> remote = RemoteCompute(
        ...     name="hpc_cluster",
        ...     host="cluster.example.com",
        ...     username="user",
        ...     scheduler="slurm",
        ...     queue="standard",
        ...     walltime=24.0,
        ...     nodes=2,
        ...     cores_per_node=32
        ... )
        >>> job_id = remote.submit_job(simulation)
        >>> status = remote.check_status(job_id)
    """

    def __init__(
        self,
        name: str,
        host: str,
        username: str,
        scheduler: str = "slurm",
        queue: str = "standard",
        walltime: float = 24.0,
        nodes: int = 1,
        cores_per_node: int = 32,
    ) -> None:
        """Initialize RemoteCompute object.

        Args:
            name: Unique identifier for the remote configuration.
            host: Remote host address (e.g., 'cluster.example.com').
            username: Username for authentication.
            scheduler: Job scheduler type. One of 'slurm', 'pbs', 'sge',
                'lsf'. Defaults to 'slurm'.
            queue: Queue/partition name. Defaults to 'standard'.
            walltime: Maximum job walltime in hours. Defaults to 24.0.
            nodes: Number of compute nodes. Defaults to 1.
            cores_per_node: Number of cores per node. Defaults to 32.

        Raises:
            ValueError: If scheduler is invalid or resource parameters
                are non-positive.
        """
        valid_schedulers = ("slurm", "pbs", "sge", "lsf")
        if scheduler not in valid_schedulers:
            raise ValueError(
                f"Invalid scheduler '{scheduler}', must be one of {valid_schedulers}"
            )

        if walltime <= 0:
            raise ValueError(f"walltime must be positive, got {walltime}")
        if nodes <= 0:
            raise ValueError(f"nodes must be positive, got {nodes}")
        if cores_per_node <= 0:
            raise ValueError(f"cores_per_node must be positive, got {cores_per_node}")

        self.name = name
        self.host = host
        self.username = username
        self.scheduler = scheduler
        self.queue = queue
        self.walltime = walltime
        self.nodes = nodes
        self.cores_per_node = cores_per_node
        self._ssh_key_path: Optional[Path] = None

    def set_ssh_key(self, key_path: Union[str, Path]) -> None:
        """Set path to SSH private key for authentication.

        Args:
            key_path: Path to SSH private key file.

        Raises:
            FileNotFoundError: If key file does not exist.
        """
        key_path = Path(key_path)
        if not key_path.exists():
            raise FileNotFoundError(f"SSH key not found: {key_path}")
        self._ssh_key_path = key_path

    def set_walltime(self, walltime: float) -> None:
        """Set the job walltime.

        Args:
            walltime: Walltime in hours.

        Raises:
            ValueError: If walltime is non-positive.
        """
        if walltime <= 0:
            raise ValueError(f"walltime must be positive, got {walltime}")
        self.walltime = walltime

    def set_resources(self, nodes: int, cores_per_node: int) -> None:
        """Set compute resource allocation.

        Args:
            nodes: Number of compute nodes.
            cores_per_node: Number of cores per node.

        Raises:
            ValueError: If parameters are non-positive.
        """
        if nodes <= 0:
            raise ValueError(f"nodes must be positive, got {nodes}")
        if cores_per_node <= 0:
            raise ValueError(f"cores_per_node must be positive, got {cores_per_node}")
        self.nodes = nodes
        self.cores_per_node = cores_per_node

    def submit_job(
        self,
        simulation: "Simulation",  # type: ignore # noqa: F821
        working_dir: Optional[Union[str, Path]] = None,
    ) -> str:
        """Submit a simulation job to the remote resource.

        Args:
            simulation: Simulation object to execute.
            working_dir: Remote working directory. If None, uses home
                directory. Defaults to None.

        Returns:
            Job ID string assigned by the scheduler.

        Raises:
            RuntimeError: If job submission fails.
        """
        # Placeholder implementation - would use SSH/scheduler API
        print(f"Submitting job '{simulation.name}' to {self.host}...")
        print(f"  Scheduler: {self.scheduler}")
        print(f"  Resources: {self.nodes} nodes x {self.cores_per_node} cores")
        print(f"  Walltime: {self.walltime} hours")

        # In real implementation, would:
        # 1. Transfer input files to remote host
        # 2. Generate job script for scheduler
        # 3. Submit job via scheduler command
        # 4. Return job ID

        return "12345"  # Placeholder job ID

    def check_status(self, job_id: str) -> str:
        """Check the status of a submitted job.

        Args:
            job_id: Job ID returned by submit_job.

        Returns:
            Job status string ('pending', 'running', 'completed', 'failed').

        Raises:
            RuntimeError: If status check fails.
        """
        # Placeholder implementation - would query scheduler
        print(f"Checking status of job {job_id} on {self.host}...")

        # In real implementation, would query scheduler for job status
        return "running"

    def cancel_job(self, job_id: str) -> None:
        """Cancel a submitted job.

        Args:
            job_id: Job ID to cancel.

        Raises:
            RuntimeError: If cancellation fails.
        """
        # Placeholder implementation - would use scheduler API
        print(f"Cancelling job {job_id} on {self.host}...")

        # In real implementation, would use scheduler cancel command

    def retrieve_results(
        self,
        job_id: str,
        local_dir: Optional[Union[str, Path]] = None,
    ) -> Path:
        """Retrieve results from a completed job.

        Args:
            job_id: Job ID to retrieve results from.
            local_dir: Local directory to store results. If None, uses
                current directory. Defaults to None.

        Returns:
            Path to local directory containing results.

        Raises:
            RuntimeError: If retrieval fails or job not completed.
        """
        # Placeholder implementation - would use SCP/SFTP
        local_dir = Path(local_dir) if local_dir else Path.cwd()
        print(f"Retrieving results for job {job_id} from {self.host}...")
        print(f"  Saving to: {local_dir}")

        # In real implementation, would:
        # 1. Check job is completed
        # 2. Transfer output files to local directory
        # 3. Return path to results

        return local_dir

    def __repr__(self) -> str:
        """Return string representation of RemoteCompute object."""
        return (
            f"RemoteCompute(name='{self.name}', host='{self.host}', "
            f"scheduler='{self.scheduler}', nodes={self.nodes})"
        )
