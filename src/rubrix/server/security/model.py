#  coding=utf-8
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

from typing import List, Optional

from pydantic import BaseModel

from rubrix.server.commons.errors import ForbiddenOperationError


class User(BaseModel):
    """Base user model"""

    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    teams: Optional[List[str]] = None

    @property
    def default_team(self) -> Optional[str]:
        if self.teams is None:
            return None
        return self.username

    def check_teams(self, teams: List[str]) -> List[str]:
        """
        Given a list of teams, apply a belongs to validation for each team. Then, return
        original list if any, else user teams (including personal/default one)

        Parameters
        ----------
        teams:
            A list of team names

        Returns
        -------
            Original team names if user belongs to them

        """
        if teams:
            for team in teams:
                self.check_team(team)
            return teams

        if self.teams is None:
            return []
        return self.teams + [self.default_team]



    def check_team(self, team: str) -> str:
        """
        Given a team name, check if user belongs to it, raising a error if not.

        Parameters
        ----------
        team

        Returns
        -------
            The original team name if user belongs to it

        """
        if not team:
            return self.default_team
        if team not in self.teams:
            raise ForbiddenOperationError(f"Missing or protected team {team}")
        return team


class Token(BaseModel):
    """Token response model"""

    access_token: str
    token_type: str = "bearer"
