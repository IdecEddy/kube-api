from dataclasses import dataclass, field
from typing import List

@dataclass
class KubePod:
    _name: str = field(default="", init=False)
    _namespace: str = field(default="", init=False)
    _cpu: int | float = field(default=0, init=False)
    _cpu_limit: int | float = field(default=0, init=False)
    _memory: int | float = field(default=0, init=False)
    _memory_limit: int | float = field(default=0, init=False)
    
    def __init__(self):
        self.name = ""
        self.namespace = ""
        self.cpu = 0
        self.cpu_limit = 0
        self.memory = 0
        self.memory_limit = 0

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def namespace(self) -> str:
        return self._namespace

    @namespace.setter
    def namespace(self, value: str):
        self._namespace = value

    @property
    def cpu(self) -> int | float:
        return self._cpu

    @cpu.setter
    def cpu(self, value: int | float):
        self._cpu = value

    @property
    def cpu_limit(self) -> int | float:
        return self._cpu_limit

    @cpu_limit.setter
    def cpu_limit(self, value: int | float):
        self._cpu_limit = value

    @property
    def memory(self) -> int | float:
        return self._memory

    @memory.setter
    def memory(self, value: int | float):
        self._memory = value

    @property
    def memory_limit(self) -> int | float:
        return self._memory_limit

    @memory_limit.setter
    def memory_limit(self, value: int | float):
        self._memory_limit = value

@dataclass
class KubeNode:
    _name: str = field(default="", init=False)
    _cpu: int | float = field(default=0, init=False)
    _memory: int | float = field(default=0, init=False)
    _cpu_utilization: int | float = field(default=0, init=False)
    _memory_utilization: int | float = field(default=0, init=False)
    _cpu_allocated: int | float = field(default=0, init=False)
    _memory_allocated: int | float = field(default=0, init=False)
    _kube_pod_list: List[KubePod] = field(default_factory=list, init=False)

    def __post_init__(self):
        self.name = ""
        self.cpu = 0
        self.memory = 0
        self.cpu_utilization = 0
        self.memory_utilization = 0
        self.cpu_allocated = 0
        self.memory_allocated = 0
        self.kube_pod_list = []

    @property
    def list_of_pods(self) -> List[KubePod]:
        return self._kube_pod_list

    @list_of_pods.setter
    def list_of_pods(self, value: List[KubePod]):
        self._kube_pod_list = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def cpu(self) -> float:
        return self._cpu

    @cpu.setter
    def cpu(self, value: float):
        if value < 0:
            raise ValueError("CPU value cannot be negative")
        self._cpu = value

    @property
    def memory(self) -> float:
        return self._memory

    @memory.setter
    def memory(self, value: float):
        if value < 0:
            raise ValueError("Memory value cannot be negative")
        self._memory = value

    @property
    def cpu_utilization(self) -> float:
        return self._cpu_utilization

    @cpu_utilization.setter
    def cpu_utilization(self, value: float):
        if value < 0:
            raise ValueError("CPU utilization cannot be negative")
        self._cpu_utilization = value

    @property
    def memory_utilization(self) -> float:
        return self._memory_utilization

    @memory_utilization.setter
    def memory_utilization(self, value: float):
        if value < 0: 
            raise ValueError("Memory utilization cannot be negative")
        self._memory_utilization = value

    @property
    def cpu_allocated(self) -> float:
        return self._cpu_allocated

    @cpu_allocated.setter
    def cpu_allocated(self, value: float):
        if value < 0:
            raise ValueError("Allocated CPU value cannot be negative")
        self._cpu_allocated = value

    @property
    def memory_allocated(self) -> float:
        return self._memory_allocated

    @memory_allocated.setter
    def memory_allocated(self, value: float):
        if value < 0:
            raise ValueError("Allocated memory value cannot be negative")
        self._memory_allocated = value
