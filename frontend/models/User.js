/*
 * coding=utf-8
 * Copyright 2021-present, the Recognai S.L. team.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

const CURRENT_WORKSPACE_FIELD = "currentWorkspace";


function getUsername(auth) {
  return auth.user.username;
}

async function getCurrentWorkspace(auth) {
  return await auth.$storage.syncUniversal(
    CURRENT_WORKSPACE_FIELD,
    auth.user.username
  );
}

async function setCurrentWorkspace(auth, workspace) {
  auth.$storage.setUniversal(CURRENT_WORKSPACE_FIELD, workspace);
}

async function clearCurrentWorkspace(auth) {
  await auth.$storage.removeUniversal(CURRENT_WORKSPACE_FIELD);
}

export { getUsername, getCurrentWorkspace, setCurrentWorkspace, clearCurrentWorkspace };
