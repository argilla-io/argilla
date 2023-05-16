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


import typer
import uvicorn

app = typer.Typer(invoke_without_command=True)


# using callback to ensure it is used as sole command
@app.callback(help="Starts the Argilla FastAPI server.", invoke_without_command=True)
def server(port: int = 6900, host: str = "0.0.0.0", access_log: bool = True):
    uvicorn.run(
        "argilla:app",
        port=port,
        host=host,
        access_log=access_log,
    )


if __name__ == "__main__":
    app()
