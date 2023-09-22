#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from abc import ABC, abstractmethod
from multiprocessing import Pool
from multiprocessing.connection import Client, Listener
from typing import Optional, Type

from pydantic import BaseModel


class BackgroundTasksExecutor(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def register_tasks(self, tasks):
        pass

    @abstractmethod
    def execute(self, name: str, **kwargs):
        pass


class IPCBackgroundTasksExecutor(BackgroundTasksExecutor):
    def __init__(self, address=None, num_processes: int = 1) -> None:
        self.address = address if address is not None else ("localhost", 6901)
        self.num_processes = num_processes
        self.tasks = {}

    def handle_conn(self, pool, conn):
        try:
            name, params = conn.recv()
            pool.apply_async(self.tasks[name], tuple(params.values()))
        except Exception as e:
            print(e)
        finally:
            conn.close()

    def start(self):
        listener = Listener(address=self.address)

        pool = Pool(processes=self.num_processes)

        try:
            while True:
                conn = listener.accept()
                self.handle_conn(pool, conn)
        except KeyboardInterrupt:
            print("Shutting down listener...")
        finally:
            listener.close()
            pool.close()
            pool.join()

    def register_tasks(self, tasks):
        self.tasks = tasks

    def execute(self, name: str, **kwargs):
        client = Client(address=("localhost", 6901))
        client.send((name, kwargs))
        client.close()


class BackgroundTasks:
    _TASKS = {}

    def __init__(self, executor: BackgroundTasksExecutor) -> None:
        self.executor = executor

    @classmethod
    def task(cls, name: str, args_validator: Optional[Type[BaseModel]] = None):
        def decorator(func):
            cls._TASKS[name] = (func, args_validator)
            return func

        return decorator

    def start(self):
        print("Running background tasks")
        self.executor.register_tasks({name: func for name, (func, _) in self._TASKS.items()})
        self.executor.start()

    def execute(self, name: str, **kwargs):
        if name not in self._TASKS:
            raise ValueError(f"Task {name} not found")

        _, args_validator = self._TASKS[name]

        if args_validator:
            try:
                args_validator(**kwargs)
            except Exception as e:
                raise Exception(f"Invalid parameters for task {name}")

        self.executor.execute(name, **kwargs)
