from enum import Enum


class ServerHealth(Enum):
    HEALTHY = 1
    STARTING = 2
    ERROR = 3
    OFFLINE = 4
    UNKNOWN = 5
    NULL = 99

class ClientHealth(Enum):
    HEALTHY = 1
    STARTING = 2
    ERROR = 3
    OFFLINE = 4
    UNKNOWN = 5
    NULL = 99

class AIHealth(Enum):
    HEALTHY = 1
    STARTING = 2
    ERROR = 3
    OFFLINE = 4
    UNKNOWN = 5
    NULL = 99

Health = {
    "Server": ServerHealth.UNKNOWN,
    "Client": ClientHealth.UNKNOWN,
    "AI": AIHealth.UNKNOWN,
}

class HealthWatcher:
    # def __init__(self, restart_server, restart_client, restart_ai):
    def __init__(self):
        # self.restart_server = restart_server
        # self.restart_client = restart_client
        # self.restart_ai = restart_ai
        pass
    
    def update_health(self, health: ServerHealth | ClientHealth | AIHealth):
        if isinstance(health, ServerHealth):
            Health["Server"] = health
        elif isinstance(health, ClientHealth):
            Health["Client"] = health
        else:
            Health["AI"] = health
        
        if health in (ServerHealth.ERROR, ClientHealth.ERROR, AIHealth.ERROR):
            pass
