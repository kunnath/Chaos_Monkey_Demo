#!/usr/bin/env python3
"""
Chaos Monkey - A simple chaos engineering tool to test system resilience
This implementation simulates various failure scenarios to test application robustness.
"""

import random
import time
import threading
import logging
import psutil
import requests
import os
import signal
from typing import List, Dict, Callable
from dataclasses import dataclass
from enum import Enum


class ChaosType(Enum):
    """Different types of chaos experiments"""
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    NETWORK_LATENCY = "network_latency"
    SERVICE_KILL = "service_kill"
    DISK_FILL = "disk_fill"
    PROCESS_HANG = "process_hang"


@dataclass
class ChaosExperiment:
    """Represents a chaos experiment configuration"""
    name: str
    chaos_type: ChaosType
    duration: int  # seconds
    probability: float  # 0.0 to 1.0
    target: str = None
    parameters: Dict = None


class ChaosMonkey:
    """
    Main Chaos Monkey class that orchestrates chaos experiments
    """
    
    def __init__(self, config_file: str = None):
        self.experiments: List[ChaosExperiment] = []
        self.running = False
        self.threads: List[threading.Thread] = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('chaos_monkey.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def add_experiment(self, experiment: ChaosExperiment):
        """Add a chaos experiment to the queue"""
        self.experiments.append(experiment)
        self.logger.info(f"Added experiment: {experiment.name}")
    
    def start(self, interval: int = 30):
        """Start the chaos monkey with specified interval between experiments"""
        self.running = True
        self.logger.info("🐒 Chaos Monkey started!")
        
        try:
            while self.running:
                if self.experiments:
                    experiment = random.choice(self.experiments)
                    if random.random() < experiment.probability:
                        self.logger.info(f"🔥 Executing chaos experiment: {experiment.name}")
                        self._execute_experiment(experiment)
                    else:
                        self.logger.info(f"⚡ Skipping experiment {experiment.name} (probability check)")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Chaos Monkey stopped by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the chaos monkey and cleanup"""
        self.running = False
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)
        self.logger.info("🐒 Chaos Monkey stopped")
    
    def _execute_experiment(self, experiment: ChaosExperiment):
        """Execute a specific chaos experiment"""
        try:
            if experiment.chaos_type == ChaosType.CPU_STRESS:
                self._cpu_stress(experiment)
            elif experiment.chaos_type == ChaosType.MEMORY_STRESS:
                self._memory_stress(experiment)
            elif experiment.chaos_type == ChaosType.NETWORK_LATENCY:
                self._network_latency(experiment)
            elif experiment.chaos_type == ChaosType.SERVICE_KILL:
                self._service_kill(experiment)
            elif experiment.chaos_type == ChaosType.DISK_FILL:
                self._disk_fill(experiment)
            elif experiment.chaos_type == ChaosType.PROCESS_HANG:
                self._process_hang(experiment)
            else:
                self.logger.warning(f"Unknown chaos type: {experiment.chaos_type}")
                
        except Exception as e:
            self.logger.error(f"Error executing experiment {experiment.name}: {str(e)}")
    
    def _cpu_stress(self, experiment: ChaosExperiment):
        """Simulate high CPU usage"""
        self.logger.info(f"🔥 Starting CPU stress for {experiment.duration} seconds")
        
        def cpu_burn():
            end_time = time.time() + experiment.duration
            while time.time() < end_time and self.running:
                # Busy wait to consume CPU
                for _ in range(1000000):
                    pass
        
        # Start multiple threads to stress CPU
        num_cores = experiment.parameters.get('cores', 2) if experiment.parameters else 2
        threads = []
        
        for _ in range(num_cores):
            thread = threading.Thread(target=cpu_burn)
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        self.logger.info("✅ CPU stress experiment completed")
    
    def _memory_stress(self, experiment: ChaosExperiment):
        """Simulate high memory usage"""
        mb_to_allocate = experiment.parameters.get('mb', 100) if experiment.parameters else 100
        self.logger.info(f"🧠 Allocating {mb_to_allocate}MB of memory for {experiment.duration} seconds")
        
        # Allocate memory
        memory_hog = []
        try:
            for _ in range(mb_to_allocate):
                # Allocate 1MB chunks
                chunk = bytearray(1024 * 1024)
                memory_hog.append(chunk)
            
            time.sleep(experiment.duration)
            
        finally:
            # Clean up memory
            memory_hog.clear()
            self.logger.info("✅ Memory stress experiment completed")
    
    def _network_latency(self, experiment: ChaosExperiment):
        """Simulate network latency (mock implementation)"""
        latency_ms = experiment.parameters.get('latency_ms', 1000) if experiment.parameters else 1000
        self.logger.info(f"🌐 Simulating {latency_ms}ms network latency for {experiment.duration} seconds")
        
        # In a real implementation, this would inject latency into network calls
        # For demo purposes, we'll just simulate the delay
        time.sleep(experiment.duration)
        self.logger.info("✅ Network latency experiment completed")
    
    def _service_kill(self, experiment: ChaosExperiment):
        """Kill a specific service/process (mock implementation)"""
        service_name = experiment.target or "demo_service"
        self.logger.info(f"💀 Killing service: {service_name}")
        
        # In a real implementation, this would actually kill processes
        # For demo purposes, we'll just log the action
        self.logger.warning(f"🔥 Service {service_name} would be terminated here")
        time.sleep(2)  # Simulate service restart time
        self.logger.info(f"🔄 Service {service_name} restarted")
    
    def _disk_fill(self, experiment: ChaosExperiment):
        """Fill disk space (safe mock implementation)"""
        size_mb = experiment.parameters.get('size_mb', 10) if experiment.parameters else 10
        self.logger.info(f"💾 Creating temporary file of {size_mb}MB for {experiment.duration} seconds")
        
        temp_file = "/tmp/chaos_monkey_temp.dat"
        try:
            # Create a temporary file
            with open(temp_file, "wb") as f:
                f.write(b"0" * (size_mb * 1024 * 1024))
            
            time.sleep(experiment.duration)
            
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
            self.logger.info("✅ Disk fill experiment completed")
    
    def _process_hang(self, experiment: ChaosExperiment):
        """Simulate process hanging"""
        self.logger.info(f"⏸️ Simulating process hang for {experiment.duration} seconds")
        
        # Simulate a hanging process
        time.sleep(experiment.duration)
        self.logger.info("✅ Process hang experiment completed")


def create_sample_experiments() -> List[ChaosExperiment]:
    """Create sample chaos experiments for demonstration"""
    experiments = [
        ChaosExperiment(
            name="Light CPU Stress",
            chaos_type=ChaosType.CPU_STRESS,
            duration=10,
            probability=0.3,
            parameters={"cores": 2}
        ),
        ChaosExperiment(
            name="Memory Allocation Test",
            chaos_type=ChaosType.MEMORY_STRESS,
            duration=15,
            probability=0.2,
            parameters={"mb": 50}
        ),
        ChaosExperiment(
            name="Network Latency Simulation",
            chaos_type=ChaosType.NETWORK_LATENCY,
            duration=8,
            probability=0.4,
            parameters={"latency_ms": 500}
        ),
        ChaosExperiment(
            name="Service Kill Test",
            chaos_type=ChaosType.SERVICE_KILL,
            duration=5,
            probability=0.1,
            target="web_service"
        ),
        ChaosExperiment(
            name="Temporary Disk Fill",
            chaos_type=ChaosType.DISK_FILL,
            duration=12,
            probability=0.2,
            parameters={"size_mb": 20}
        ),
        ChaosExperiment(
            name="Process Hang Simulation",
            chaos_type=ChaosType.PROCESS_HANG,
            duration=6,
            probability=0.3
        )
    ]
    return experiments


if __name__ == "__main__":
    # Create and configure Chaos Monkey
    monkey = ChaosMonkey()
    
    # Add sample experiments
    experiments = create_sample_experiments()
    for experiment in experiments:
        monkey.add_experiment(experiment)
    
    print("🐒 Chaos Monkey Demo")
    print("=" * 50)
    print(f"Loaded {len(experiments)} chaos experiments")
    print("Press Ctrl+C to stop the chaos monkey")
    print("=" * 50)
    
    # Start chaos monkey with 20 second intervals
    monkey.start(interval=20)
