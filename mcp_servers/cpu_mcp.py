#!/usr/bin/env python3
"""
SoulCoreHub CPU MCP Server
-------------------------
This MCP server specializes in operating systems, CPU behavior, threading, and memory management.
"""

import json
import logging
import platform
import os
import psutil
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CPUMCP")

# Try to import psutil, install if not available
try:
    import psutil
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "psutil"])
    import psutil

# Constants
PORT = 8706
SERVER_NAME = "cpu_mcp"
SPECIALTIES = ["operating systems", "CPU behavior", "threading", "memory management", "low-level programming"]
TOOLS = {
    "system_info": {
        "description": "Provides detailed information about the system",
        "parameters": {
            "info_type": "Type of information (cpu, memory, os, all)"
        }
    },
    "process_analysis": {
        "description": "Analyzes process behavior and resource usage",
        "parameters": {
            "process_name": "Name of the process to analyze",
            "detail_level": "Level of detail (basic, detailed)"
        }
    },
    "threading_guide": {
        "description": "Provides guidance on threading and concurrency",
        "parameters": {
            "language": "Programming language",
            "use_case": "Use case description"
        }
    }
}

class MCPHandler(BaseHTTPRequestHandler):
    """Handler for MCP server requests."""
    
    def _set_headers(self, content_type="application/json"):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests - primarily for server info and health checks."""
        if self.path == "/":
            self._set_headers()
            server_info = {
                "name": SERVER_NAME,
                "status": "active",
                "specialties": SPECIALTIES,
                "tools": list(TOOLS.keys()),
                "version": "1.0.0"
            }
            self.wfile.write(json.dumps(server_info).encode())
        elif self.path == "/health":
            self._set_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests for tool invocation."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            request = json.loads(post_data.decode('utf-8'))
            
            if self.path == "/invoke":
                tool_name = request.get("tool")
                parameters = request.get("parameters", {})
                
                if tool_name not in TOOLS:
                    self._set_headers()
                    self.wfile.write(json.dumps({
                        "error": f"Tool '{tool_name}' not found",
                        "available_tools": list(TOOLS.keys())
                    }).encode())
                    return
                
                # Process the tool request
                result = self._process_tool(tool_name, parameters)
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            
            elif self.path == "/context":
                # Process context request
                query = request.get("query", "")
                context = self._generate_context(query)
                self._set_headers()
                self.wfile.write(json.dumps({"context": context}).encode())
            
            else:
                self.send_response(404)
                self.end_headers()
        
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
    
    def _process_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process a tool invocation request."""
        logger.info(f"Processing tool: {tool_name} with parameters: {parameters}")
        
        if tool_name == "system_info":
            return self._get_system_info(
                parameters.get("info_type", "all")
            )
        
        elif tool_name == "process_analysis":
            return self._analyze_process(
                parameters.get("process_name", ""),
                parameters.get("detail_level", "basic")
            )
        
        elif tool_name == "threading_guide":
            return self._provide_threading_guide(
                parameters.get("language", ""),
                parameters.get("use_case", "")
            )
        
        return {"error": f"Tool implementation for '{tool_name}' not found"}
    
    def _get_system_info(self, info_type: str) -> Dict[str, Any]:
        """Provide detailed information about the system."""
        info_type_lower = info_type.lower()
        system_info = {}
        
        # CPU information
        if info_type_lower in ["cpu", "all"]:
            cpu_info = {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "current_frequency": psutil.cpu_freq().current if psutil.cpu_freq() else "Unknown",
                "max_frequency": psutil.cpu_freq().max if psutil.cpu_freq() else "Unknown",
                "architecture": platform.machine(),
                "current_usage_percent": psutil.cpu_percent(interval=1),
                "per_core_usage": psutil.cpu_percent(interval=1, percpu=True)
            }
            system_info["cpu"] = cpu_info
        
        # Memory information
        if info_type_lower in ["memory", "all"]:
            memory = psutil.virtual_memory()
            memory_info = {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent_used": memory.percent,
                "swap_total": psutil.swap_memory().total,
                "swap_used": psutil.swap_memory().used,
                "swap_percent": psutil.swap_memory().percent
            }
            system_info["memory"] = memory_info
        
        # OS information
        if info_type_lower in ["os", "all"]:
            os_info = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "hostname": platform.node(),
                "uptime_seconds": int(psutil.boot_time())
            }
            system_info["os"] = os_info
        
        # Disk information
        if info_type_lower in ["disk", "all"]:
            disk_info = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "filesystem_type": partition.fstype,
                        "total_size": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent_used": usage.percent
                    })
                except PermissionError:
                    # Some mountpoints may not be accessible
                    pass
            system_info["disk"] = disk_info
        
        # Network information
        if info_type_lower in ["network", "all"]:
            network_info = {
                "interfaces": list(psutil.net_if_addrs().keys()),
                "io_counters": {
                    "bytes_sent": psutil.net_io_counters().bytes_sent,
                    "bytes_recv": psutil.net_io_counters().bytes_recv,
                    "packets_sent": psutil.net_io_counters().packets_sent,
                    "packets_recv": psutil.net_io_counters().packets_recv
                }
            }
            system_info["network"] = network_info
        
        return {
            "system_info": system_info
        }
    
    def _analyze_process(self, process_name: str, detail_level: str) -> Dict[str, Any]:
        """Analyze process behavior and resource usage."""
        if not process_name:
            return {"error": "No process name provided"}
        
        # Find processes matching the name
        matching_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            if process_name.lower() in proc.info['name'].lower():
                matching_processes.append(proc)
        
        if not matching_processes:
            return {"error": f"No processes found matching '{process_name}'"}
        
        # Analyze each matching process
        process_analyses = []
        for proc in matching_processes:
            try:
                # Basic process info
                process_info = {
                    "pid": proc.pid,
                    "name": proc.name(),
                    "username": proc.username(),
                    "status": proc.status(),
                    "created_time": proc.create_time(),
                    "cpu_percent": proc.cpu_percent(interval=0.1),
                    "memory_percent": proc.memory_percent(),
                    "memory_info": {
                        "rss": proc.memory_info().rss,  # Resident Set Size
                        "vms": proc.memory_info().vms   # Virtual Memory Size
                    }
                }
                
                # Detailed process info
                if detail_level.lower() == "detailed":
                    try:
                        process_info.update({
                            "num_threads": proc.num_threads(),
                            "threads": [{"id": t.id, "user_time": t.user_time, "system_time": t.system_time} 
                                      for t in proc.threads()],
                            "open_files": [f.path for f in proc.open_files()],
                            "connections": [{"local_addr": c.laddr, "remote_addr": c.raddr, "status": c.status} 
                                          for c in proc.connections()],
                            "io_counters": {
                                "read_count": proc.io_counters().read_count if proc.io_counters() else 0,
                                "write_count": proc.io_counters().write_count if proc.io_counters() else 0,
                                "read_bytes": proc.io_counters().read_bytes if proc.io_counters() else 0,
                                "write_bytes": proc.io_counters().write_bytes if proc.io_counters() else 0
                            },
                            "cpu_affinity": proc.cpu_affinity() if hasattr(proc, 'cpu_affinity') else [],
                            "nice": proc.nice(),
                            "ionice": proc.ionice() if hasattr(proc, 'ionice') else None,
                            "num_ctx_switches": {
                                "voluntary": proc.num_ctx_switches().voluntary if proc.num_ctx_switches() else 0,
                                "involuntary": proc.num_ctx_switches().involuntary if proc.num_ctx_switches() else 0
                            }
                        })
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        process_info["detailed_info_error"] = "Access denied or process no longer exists"
                
                process_analyses.append(process_info)
            
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process might have terminated or access might be denied
                pass
        
        # Generate analysis summary
        summary = {
            "process_name": process_name,
            "processes_found": len(process_analyses),
            "total_cpu_percent": sum(p.get("cpu_percent", 0) for p in process_analyses),
            "total_memory_percent": sum(p.get("memory_percent", 0) for p in process_analyses),
            "processes": process_analyses
        }
        
        return {
            "process_analysis": summary
        }
    
    def _provide_threading_guide(self, language: str, use_case: str) -> Dict[str, Any]:
        """Provide guidance on threading and concurrency."""
        if not language:
            return {"error": "No programming language provided"}
        
        if not use_case:
            return {"error": "No use case provided"}
        
        # Threading patterns by language
        threading_patterns = {
            "python": {
                "io_bound": {
                    "recommended_approach": "asyncio",
                    "alternatives": ["threading", "multiprocessing"],
                    "example_code": """
import asyncio

async def fetch_data(url):
    # Simulating an I/O operation
    await asyncio.sleep(1)  # Non-blocking sleep
    return f"Data from {url}"

async def main():
    # Gather multiple I/O tasks to run concurrently
    urls = ["url1", "url2", "url3"]
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    print(results)

# Run the event loop
asyncio.run(main())
"""
                },
                "cpu_bound": {
                    "recommended_approach": "multiprocessing",
                    "alternatives": ["concurrent.futures.ProcessPoolExecutor"],
                    "example_code": """
from multiprocessing import Pool

def cpu_intensive_task(n):
    # Simulating a CPU-intensive calculation
    return sum(i * i for i in range(n))

if __name__ == "__main__":
    # Create a pool of worker processes
    with Pool(processes=4) as pool:
        numbers = [10000000, 20000000, 30000000, 40000000]
        results = pool.map(cpu_intensive_task, numbers)
        print(results)
"""
                },
                "mixed": {
                    "recommended_approach": "concurrent.futures",
                    "alternatives": ["asyncio with ProcessPoolExecutor"],
                    "example_code": """
import concurrent.futures

def process_item(item):
    # Mixed I/O and CPU operations
    # ...
    return result

# For mixed workloads, choose the appropriate executor
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    items = ["item1", "item2", "item3", "item4"]
    results = list(executor.map(process_item, items))
    print(results)
"""
                }
            },
            "java": {
                "io_bound": {
                    "recommended_approach": "CompletableFuture",
                    "alternatives": ["ExecutorService with Callable", "Virtual Threads (Java 19+)"],
                    "example_code": """
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;
import java.util.List;

public class AsyncExample {
    public static void main(String[] args) {
        List<String> urls = List.of("url1", "url2", "url3");
        
        // Create CompletableFuture for each URL
        List<CompletableFuture<String>> futures = urls.stream()
            .map(url -> CompletableFuture.supplyAsync(() -> fetchData(url)))
            .collect(Collectors.toList());
        
        // Combine all futures and wait for completion
        CompletableFuture<Void> allFutures = CompletableFuture.allOf(
            futures.toArray(new CompletableFuture[0])
        );
        
        // Get results when all complete
        allFutures.thenRun(() -> {
            List<String> results = futures.stream()
                .map(CompletableFuture::join)
                .collect(Collectors.toList());
            System.out.println(results);
        });
        
        // Wait for completion
        allFutures.join();
    }
    
    private static String fetchData(String url) {
        // Simulating I/O operation
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return "Data from " + url;
    }
}
"""
                },
                "cpu_bound": {
                    "recommended_approach": "ForkJoinPool",
                    "alternatives": ["ExecutorService with fixed thread pool"],
                    "example_code": """
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveTask;

public class ParallelComputation {
    public static void main(String[] args) {
        ForkJoinPool forkJoinPool = new ForkJoinPool();
        long result = forkJoinPool.invoke(new SumTask(1, 1000000));
        System.out.println("Sum: " + result);
    }
    
    static class SumTask extends RecursiveTask<Long> {
        private final long from;
        private final long to;
        private static final long THRESHOLD = 10000;
        
        SumTask(long from, long to) {
            this.from = from;
            this.to = to;
        }
        
        @Override
        protected Long compute() {
            if (to - from <= THRESHOLD) {
                // Sequential computation for small ranges
                long sum = 0;
                for (long i = from; i <= to; i++) {
                    sum += i;
                }
                return sum;
            } else {
                // Split the task for parallel computation
                long mid = (from + to) / 2;
                SumTask leftTask = new SumTask(from, mid);
                SumTask rightTask = new SumTask(mid + 1, to);
                
                leftTask.fork(); // Submit left task
                long rightResult = rightTask.compute(); // Compute right task
                long leftResult = leftTask.join(); // Wait for left task
                
                return leftResult + rightResult;
            }
        }
    }
}
"""
                }
            },
            "javascript": {
                "io_bound": {
                    "recommended_approach": "Promises",
                    "alternatives": ["async/await", "Observables (RxJS)"],
                    "example_code": """
// Using async/await with Promise.all for concurrent I/O operations
async function fetchData(url) {
    // Simulating an API call
    return new Promise(resolve => {
        setTimeout(() => {
            resolve(`Data from ${url}`);
        }, 1000);
    });
}

async function main() {
    const urls = ['url1', 'url2', 'url3'];
    
    // Fetch all data concurrently
    const promises = urls.map(url => fetchData(url));
    const results = await Promise.all(promises);
    
    console.log(results);
}

main().catch(console.error);
"""
                },
                "cpu_bound": {
                    "recommended_approach": "Web Workers",
                    "alternatives": ["Worker Threads (Node.js)"],
                    "example_code": """
// Main thread code
// Create a new worker
const worker = new Worker('worker.js');

// Send data to the worker
worker.postMessage({
    task: 'compute',
    data: { start: 1, end: 10000000 }
});

// Receive results from the worker
worker.onmessage = function(event) {
    console.log('Result:', event.data.result);
};

// worker.js content:
/*
self.onmessage = function(event) {
    if (event.data.task === 'compute') {
        const { start, end } = event.data.data;
        let sum = 0;
        
        // CPU-intensive calculation
        for (let i = start; i <= end; i++) {
            sum += i * i;
        }
        
        // Send the result back to the main thread
        self.postMessage({ result: sum });
    }
};
*/
"""
                }
            }
        }
        
        # Determine workload type from use case
        use_case_lower = use_case.lower()
        workload_type = "mixed"  # Default
        
        if any(term in use_case_lower for term in ["io", "network", "file", "database", "api", "http", "request"]):
            workload_type = "io_bound"
        elif any(term in use_case_lower for term in ["cpu", "compute", "calculation", "processing", "algorithm"]):
            workload_type = "cpu_bound"
        
        # Get threading pattern for the language and workload type
        language_lower = language.lower()
        if language_lower not in threading_patterns:
            # Default to Python if language not supported
            language_lower = "python"
        
        language_patterns = threading_patterns[language_lower]
        if workload_type not in language_patterns:
            # Default to mixed if workload type not found
            workload_type = list(language_patterns.keys())[0]
        
        pattern = language_patterns[workload_type]
        
        # General threading best practices
        best_practices = [
            "Minimize shared state between threads to avoid race conditions",
            "Use thread-safe data structures and synchronization primitives",
            "Be aware of thread creation overhead - reuse threads when possible",
            "Avoid blocking the main/UI thread",
            "Consider the number of CPU cores when determining thread pool size",
            "Monitor thread performance and adjust as needed",
            "Be careful with thread termination to avoid resource leaks"
        ]
        
        # Language-specific best practices
        if language_lower == "python":
            best_practices.extend([
                "Remember the Global Interpreter Lock (GIL) limits true parallelism for CPU-bound tasks",
                "Use multiprocessing for CPU-bound tasks to bypass the GIL",
                "Consider asyncio for I/O-bound tasks for better performance than threading",
                "Use ThreadPoolExecutor for simple thread pool management"
            ])
        elif language_lower == "java":
            best_practices.extend([
                "Prefer higher-level concurrency utilities over raw threads",
                "Use synchronized blocks sparingly and keep them small",
                "Consider using java.util.concurrent collections for thread safety",
                "Be aware of memory visibility issues - use volatile or AtomicReference when needed",
                "Consider using CompletableFuture for asynchronous programming"
            ])
        elif language_lower == "javascript":
            best_practices.extend([
                "JavaScript is single-threaded in the browser - use asynchronous patterns",
                "In Node.js, use the cluster module for multi-core utilization",
                "Web Workers run in separate threads but have limited communication",
                "Avoid blocking the event loop with long-running operations",
                "Use microtasks (Promises) and macrotasks (setTimeout) appropriately"
            ])
        
        # Generate guide
        guide = {
            "language": language,
            "workload_type": workload_type,
            "use_case": use_case,
            "recommended_approach": pattern["recommended_approach"],
            "alternative_approaches": pattern["alternatives"],
            "example_code": pattern["example_code"],
            "best_practices": best_practices
        }
        
        return {
            "threading_guide": guide
        }
    
    def _generate_context(self, query: str) -> List[Dict[str, Any]]:
        """Generate context information based on the query."""
        context_items = []
        
        # Add system domain specific context if detected
        domains = ["cpu", "memory", "thread", "process", "operating system", "kernel", "assembly", "hardware", "cache"]
        for domain in domains:
            if domain.lower() in query.lower():
                context_items.append({
                    "type": "domain_context",
                    "domain": domain,
                    "focus": "system"
                })
        
        # Add general system context
        context_items.append({
            "type": "specialty_context",
            "specialty": "cpu_systems",
            "description": "This MCP server specializes in operating systems, CPU behavior, threading, and memory management."
        })
        
        return context_items

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    pass

def run_server():
    """Run the MCP server."""
    server_address = ('', PORT)
    httpd = ThreadedHTTPServer(server_address, MCPHandler)
    logger.info(f"Starting {SERVER_NAME} on port {PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
