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

import { Context } from "@nuxt/types";
import { useResolve } from "ts-injecty";
import { LoadUserUseCase } from "~/v1/domain/usecases/load-user-use-case";

export default async ({ $auth }: Context) => {
  const useCase = useResolve(LoadUserUseCase);

  try {
    await useCase.execute();
  } catch (e) {
    if (e.response.status === 401) {
      await $auth.logout();

      $auth.redirect("login");
    }
  }
};
