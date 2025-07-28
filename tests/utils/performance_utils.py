"""
Performance Testing Utilities

Advanced performance testing and benchmarking utilities for OpenMAS comprehensive testing.
Provides performance measurement, benchmarking, load testing, and performance regression detection.
"""

import asyncio
import time
import statistics
import logging
from typing import Any, Dict, List, Callable, Optional, Union, Awaitable
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import psutil
import gc

from tests.utils.test_supervisor import TestSupervisor


@dataclass
class PerformanceMetrics:
    """Container for performance measurement results."""
    operation_name: str
    execution_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    iterations: int = 1
    throughput_ops_per_sec: float = 0.0
    peak_memory_mb: float = 0.0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceBenchmark:
    """Performance benchmark configuration."""
    name: str
    target_function: Callable
    iterations: int = 100
    warmup_iterations: int = 10
    timeout_per_operation: float = 30.0
    memory_threshold_mb: float = 500.0
    cpu_threshold_percent: float = 80.0
    throughput_threshold_ops_per_sec: float = 10.0


class PerformanceMonitor:
    """Real-time performance monitoring during test execution."""
    
    def __init__(self, sample_interval: float = 0.1):
        self.sample_interval = sample_interval
        self.is_monitoring = False
        self.samples: List[Dict[str, float]] = []
        self.process = psutil.Process()
        self.logger = logging.getLogger("PerformanceMonitor")
    
    async def start_monitoring(self) -> None:
        """Start performance monitoring."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.samples.clear()
        
        asyncio.create_task(self._monitoring_loop())
        self.logger.debug("Performance monitoring started")
    
    async def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return aggregated metrics."""
        self.is_monitoring = False
        
        if not self.samples:
            return {}
        
        # Calculate aggregated metrics
        cpu_values = [s['cpu_percent'] for s in self.samples]
        memory_values = [s['memory_mb'] for s in self.samples]
        
        metrics = {
            'duration_seconds': len(self.samples) * self.sample_interval,
            'sample_count': len(self.samples),
            'cpu_percent': {
                'mean': statistics.mean(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values),
                'stddev': statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0.0
            },
            'memory_mb': {
                'mean': statistics.mean(memory_values),
                'max': max(memory_values),
                'min': min(memory_values),
                'stddev': statistics.stdev(memory_values) if len(memory_values) > 1 else 0.0
            }
        }
        
        self.logger.debug(f"Performance monitoring stopped. Collected {len(self.samples)} samples")
        return metrics
    
    async def _monitoring_loop(self) -> None:
        """Internal monitoring loop."""
        while self.is_monitoring:
            try:
                sample = {
                    'timestamp': time.time(),
                    'cpu_percent': self.process.cpu_percent(),
                    'memory_mb': self.process.memory_info().rss / 1024 / 1024
                }
                self.samples.append(sample)
                
                await asyncio.sleep(self.sample_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                break
    
    @asynccontextmanager
    async def monitor_context(self):
        """Context manager for automatic monitoring."""
        await self.start_monitoring()
        try:
            yield self
        finally:
            metrics = await self.stop_monitoring()
            return metrics


class PerformanceTester:
    """Comprehensive performance testing framework."""
    
    def __init__(self, supervisor: Optional[TestSupervisor] = None):
        self.supervisor = supervisor
        self.monitor = PerformanceMonitor()
        self.baseline_metrics: Dict[str, PerformanceMetrics] = {}
        self.logger = logging.getLogger("PerformanceTester")
    
    async def measure_operation(
        self,
        operation_name: str,
        operation: Callable[[], Awaitable[Any]],
        iterations: int = 1,
        warmup_iterations: int = 0
    ) -> PerformanceMetrics:
        """Measure performance of a single operation."""
        self.logger.debug(f"Measuring operation: {operation_name} ({iterations} iterations)")
        
        if self.supervisor:
            await self.supervisor._emit_event("performance_measurement_started", {
                "operation_name": operation_name,
                "iterations": iterations
            })
        
        # Warmup
        for _ in range(warmup_iterations):
            try:
                await operation()
            except Exception as e:
                self.logger.warning(f"Warmup iteration failed: {e}")
        
        # Force garbage collection before measurement
        gc.collect()
        
        # Start monitoring
        await self.monitor.start_monitoring()
        
        execution_times = []
        errors = []
        start_time = time.time()
        
        try:
            for i in range(iterations):
                iteration_start = time.time()
                
                try:
                    await operation()
                    iteration_time = time.time() - iteration_start
                    execution_times.append(iteration_time)
                    
                except Exception as e:
                    errors.append(f"Iteration {i}: {str(e)}")
                    self.logger.error(f"Operation failed in iteration {i}: {e}")
            
            total_time = time.time() - start_time
            
        finally:
            monitoring_metrics = await self.monitor.stop_monitoring()
        
        # Calculate metrics
        if execution_times:
            avg_execution_time = statistics.mean(execution_times)
            throughput = len(execution_times) / total_time if total_time > 0 else 0.0
        else:
            avg_execution_time = 0.0
            throughput = 0.0
        
        metrics = PerformanceMetrics(
            operation_name=operation_name,
            execution_time=avg_execution_time,
            memory_usage_mb=monitoring_metrics.get('memory_mb', {}).get('mean', 0.0),
            cpu_usage_percent=monitoring_metrics.get('cpu_percent', {}).get('mean', 0.0),
            iterations=iterations,
            throughput_ops_per_sec=throughput,
            peak_memory_mb=monitoring_metrics.get('memory_mb', {}).get('max', 0.0),
            errors=errors,
            metadata={
                'execution_times': execution_times,
                'monitoring_metrics': monitoring_metrics,
                'total_time': total_time
            }
        )
        
        if self.supervisor:
            await self.supervisor._emit_event("performance_measurement_completed", {
                "operation_name": operation_name,
                "avg_execution_time": avg_execution_time,
                "throughput": throughput,
                "error_count": len(errors)
            })
        
        return metrics
    
    async def run_benchmark(self, benchmark: PerformanceBenchmark) -> PerformanceMetrics:
        """Run a comprehensive performance benchmark."""
        self.logger.info(f"Running benchmark: {benchmark.name}")
        
        # Prepare operation function
        if asyncio.iscoroutinefunction(benchmark.target_function):
            operation = benchmark.target_function
        else:
            async def async_wrapper():
                return benchmark.target_function()
            operation = async_wrapper
        
        # Run measurement
        metrics = await self.measure_operation(
            operation_name=benchmark.name,
            operation=operation,
            iterations=benchmark.iterations,
            warmup_iterations=benchmark.warmup_iterations
        )
        
        # Check against thresholds
        performance_issues = []
        
        if metrics.memory_usage_mb > benchmark.memory_threshold_mb:
            performance_issues.append(f"Memory usage {metrics.memory_usage_mb:.1f}MB exceeds threshold {benchmark.memory_threshold_mb}MB")
        
        if metrics.cpu_usage_percent > benchmark.cpu_threshold_percent:
            performance_issues.append(f"CPU usage {metrics.cpu_usage_percent:.1f}% exceeds threshold {benchmark.cpu_threshold_percent}%")
        
        if metrics.throughput_ops_per_sec < benchmark.throughput_threshold_ops_per_sec:
            performance_issues.append(f"Throughput {metrics.throughput_ops_per_sec:.1f} ops/sec below threshold {benchmark.throughput_threshold_ops_per_sec}")
        
        if performance_issues:
            self.logger.warning(f"Performance issues detected in {benchmark.name}: {performance_issues}")
            metrics.errors.extend(performance_issues)
        
        return metrics
    
    async def compare_with_baseline(
        self,
        current_metrics: PerformanceMetrics,
        baseline_metrics: PerformanceMetrics,
        tolerance_percent: float = 10.0
    ) -> Dict[str, Any]:
        """Compare current metrics with baseline for regression detection."""
        comparison = {
            'operation_name': current_metrics.operation_name,
            'regression_detected': False,
            'improvements': [],
            'regressions': [],
            'metrics_comparison': {}
        }
        
        # Compare execution time
        time_change_percent = ((current_metrics.execution_time - baseline_metrics.execution_time) / baseline_metrics.execution_time) * 100
        comparison['metrics_comparison']['execution_time'] = {
            'current': current_metrics.execution_time,
            'baseline': baseline_metrics.execution_time,
            'change_percent': time_change_percent
        }
        
        if time_change_percent > tolerance_percent:
            comparison['regressions'].append(f"Execution time increased by {time_change_percent:.1f}%")
            comparison['regression_detected'] = True
        elif time_change_percent < -tolerance_percent:
            comparison['improvements'].append(f"Execution time improved by {abs(time_change_percent):.1f}%")
        
        # Compare memory usage
        memory_change_percent = ((current_metrics.memory_usage_mb - baseline_metrics.memory_usage_mb) / baseline_metrics.memory_usage_mb) * 100 if baseline_metrics.memory_usage_mb > 0 else 0
        comparison['metrics_comparison']['memory_usage'] = {
            'current': current_metrics.memory_usage_mb,
            'baseline': baseline_metrics.memory_usage_mb,
            'change_percent': memory_change_percent
        }
        
        if memory_change_percent > tolerance_percent:
            comparison['regressions'].append(f"Memory usage increased by {memory_change_percent:.1f}%")
            comparison['regression_detected'] = True
        elif memory_change_percent < -tolerance_percent:
            comparison['improvements'].append(f"Memory usage improved by {abs(memory_change_percent):.1f}%")
        
        # Compare throughput
        throughput_change_percent = ((current_metrics.throughput_ops_per_sec - baseline_metrics.throughput_ops_per_sec) / baseline_metrics.throughput_ops_per_sec) * 100 if baseline_metrics.throughput_ops_per_sec > 0 else 0
        comparison['metrics_comparison']['throughput'] = {
            'current': current_metrics.throughput_ops_per_sec,
            'baseline': baseline_metrics.throughput_ops_per_sec,
            'change_percent': throughput_change_percent
        }
        
        if throughput_change_percent < -tolerance_percent:
            comparison['regressions'].append(f"Throughput decreased by {abs(throughput_change_percent):.1f}%")
            comparison['regression_detected'] = True
        elif throughput_change_percent > tolerance_percent:
            comparison['improvements'].append(f"Throughput improved by {throughput_change_percent:.1f}%")
        
        return comparison
    
    def save_baseline(self, metrics: PerformanceMetrics) -> None:
        """Save metrics as baseline for future comparisons."""
        self.baseline_metrics[metrics.operation_name] = metrics
        self.logger.info(f"Saved baseline for {metrics.operation_name}")
    
    def get_baseline(self, operation_name: str) -> Optional[PerformanceMetrics]:
        """Get baseline metrics for an operation."""
        return self.baseline_metrics.get(operation_name)


class LoadTester:
    """Load testing utilities for multi-agent and protocol testing."""
    
    def __init__(self, supervisor: Optional[TestSupervisor] = None):
        self.supervisor = supervisor
        self.logger = logging.getLogger("LoadTester")
    
    async def run_concurrent_load_test(
        self,
        operation_factory: Callable[[], Awaitable[Any]],
        concurrent_users: int = 10,
        operations_per_user: int = 10,
        ramp_up_time: float = 5.0
    ) -> Dict[str, Any]:
        """Run concurrent load test with multiple simulated users."""
        self.logger.info(f"Starting load test: {concurrent_users} users, {operations_per_user} ops/user")
        
        if self.supervisor:
            await self.supervisor._emit_event("load_test_started", {
                "concurrent_users": concurrent_users,
                "operations_per_user": operations_per_user
            })
        
        results = {
            'total_operations': concurrent_users * operations_per_user,
            'successful_operations': 0,
            'failed_operations': 0,
            'execution_times': [],
            'errors': [],
            'throughput_ops_per_sec': 0.0,
            'avg_response_time': 0.0
        }
        
        async def user_simulation(user_id: int):
            """Simulate a single user's operations."""
            user_results = {
                'successful': 0,
                'failed': 0,
                'execution_times': [],
                'errors': []
            }
            
            for op_id in range(operations_per_user):
                start_time = time.time()
                
                try:
                    await operation_factory()
                    execution_time = time.time() - start_time
                    user_results['execution_times'].append(execution_time)
                    user_results['successful'] += 1
                    
                except Exception as e:
                    user_results['errors'].append(f"User {user_id}, Op {op_id}: {str(e)}")
                    user_results['failed'] += 1
            
            return user_results
        
        # Create user tasks with ramp-up
        user_tasks = []
        start_time = time.time()
        
        for user_id in range(concurrent_users):
            # Stagger user start times for ramp-up
            delay = (user_id / concurrent_users) * ramp_up_time
            
            async def delayed_user(uid=user_id, d=delay):
                await asyncio.sleep(d)
                return await user_simulation(uid)
            
            user_tasks.append(asyncio.create_task(delayed_user()))
        
        # Wait for all users to complete
        user_results = await asyncio.gather(*user_tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Aggregate results
        for user_result in user_results:
            if isinstance(user_result, Exception):
                results['errors'].append(f"User task failed: {str(user_result)}")
                continue
            
            results['successful_operations'] += user_result['successful']
            results['failed_operations'] += user_result['failed']
            results['execution_times'].extend(user_result['execution_times'])
            results['errors'].extend(user_result['errors'])
        
        # Calculate final metrics
        if results['execution_times']:
            results['avg_response_time'] = statistics.mean(results['execution_times'])
        
        results['throughput_ops_per_sec'] = results['successful_operations'] / total_time if total_time > 0 else 0.0
        
        if self.supervisor:
            await self.supervisor._emit_event("load_test_completed", {
                "successful_operations": results['successful_operations'],
                "failed_operations": results['failed_operations'],
                "throughput": results['throughput_ops_per_sec']
            })
        
        return results


# Utility functions for common performance testing patterns

async def measure_agent_startup_time(agent_factory: Callable, iterations: int = 10) -> PerformanceMetrics:
    """Measure agent startup performance."""
    async def startup_operation():
        agent = agent_factory()
        start_time = time.time()
        await agent.start()
        startup_time = time.time() - start_time
        await agent.stop()
        return startup_time
    
    tester = PerformanceTester()
    return await tester.measure_operation("agent_startup", startup_operation, iterations)


async def measure_message_processing_throughput(
    agent: Any,
    message_factory: Callable,
    message_count: int = 100
) -> PerformanceMetrics:
    """Measure message processing throughput."""
    messages = [message_factory() for _ in range(message_count)]
    
    async def processing_operation():
        start_time = time.time()
        for message in messages:
            await agent.handle_message(message)
        return time.time() - start_time
    
    tester = PerformanceTester()
    return await tester.measure_operation("message_processing", processing_operation, iterations=1)


async def measure_protocol_adapter_performance(
    adapter: Any,
    message_factory: Callable,
    iterations: int = 50
) -> PerformanceMetrics:
    """Measure protocol adapter performance."""
    async def adapter_operation():
        message = message_factory()
        await adapter.send_message(message)
    
    tester = PerformanceTester()
    return await tester.measure_operation("protocol_adapter", adapter_operation, iterations)


def create_performance_benchmark_suite() -> List[PerformanceBenchmark]:
    """Create standard performance benchmark suite for OpenMAS."""
    return [
        PerformanceBenchmark(
            name="agent_creation",
            target_function=lambda: None,  # To be replaced with actual agent factory
            iterations=50,
            memory_threshold_mb=100.0,
            throughput_threshold_ops_per_sec=5.0
        ),
        PerformanceBenchmark(
            name="message_routing",
            target_function=lambda: None,  # To be replaced with message routing test
            iterations=100,
            memory_threshold_mb=50.0,
            throughput_threshold_ops_per_sec=20.0
        ),
        PerformanceBenchmark(
            name="protocol_communication",
            target_function=lambda: None,  # To be replaced with protocol test
            iterations=75,
            memory_threshold_mb=75.0,
            throughput_threshold_ops_per_sec=15.0
        )
    ]
