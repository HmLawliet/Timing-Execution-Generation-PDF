import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import time 
from celeryconfig import Config_Run

def run() -> None:
    os.system(Config_Run.worker)
    os.system(Config_Run.beat)
    
def monitor() -> bool:
    worker_count = int(os.popen(Config_Run.monitor_worker).read().strip())
    beat_count = int(os.popen(Config_Run.monitor_beat).read().strip()) 
    return True if (worker_count>0 and beat_count>0) else False

def kill() -> None:
    if int(os.popen(Config_Run.monitor_worker).read().strip()) > 0:
        os.system(Config_Run.kill_worker)
    if int(os.popen(Config_Run.monitor_beat).read().strip()) > 0:
        os.system(Config_Run.kill_beat)
    if int(os.popen(Config_Run.monitor_defunct).read().strip()) > 0:
        os.system(Config_Run.kill_defunct)
    time.sleep(2) 
    
# 启动  监控
# beat worker 分别启动
class App:
    def app(self) -> None:
        while True:
            if not monitor():
                kill()
                run() 
            time.sleep(3600)
    
    def __del__(self) -> None:
        kill()

if __name__ == "__main__":
    App().app()
    pass