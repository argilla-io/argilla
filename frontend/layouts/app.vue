<!--
  - coding=utf-8
  - Copyright 2021-present, the Recognai S.L. team.
  -
  - Licensed under the Apache License, Version 2.0 (the "License");
  - you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at
  -
  -     http://www.apache.org/licenses/LICENSE-2.0
  -
  - Unless required by applicable law or agreed to in writing, software
  - distributed under the License is distributed on an "AS IS" BASIS,
  - WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  - See the License for the specific language governing permissions and
  - limitations under the License.
  -->

<template>
  <div>
    <Nuxt v-if="!$slots.default" />
    <slot />
  </div>
</template>

<script>
import { Notification } from "@/models/Notifications";
export default {
  name: "Index",
  computed: {
    imOffline() {
      return this.$nuxt.isOffline;
    },
  },
  watch: {
    imOffline() {
      return Notification.dispatch("notify", {
        message: "You are offline",
        type: "error",
      });
    },
  },
};
</script>

<style></style>
