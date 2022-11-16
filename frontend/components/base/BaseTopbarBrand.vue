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
  <div class="topbar">
    <brand-icon class="brand-icon" color="white" />
    <slot />
  </div>
</template>

<script>
export default {
  data: () => ({}),
};
</script>

<style lang="scss" scoped>
.topbar {
  width: 100%;
  display: flex;
  align-items: center;
  min-height: $topbarHeight;
  position: relative;
  background: palette(grey, 100);
  color: palette(white);
  padding-top: 0;
  padding-bottom: 0;
  padding-right: 1.2em;
  padding-left: 4em;
  a {
    text-decoration: none;
  }
}
.brand-icon {
  width: 32px;
  height: auto;
}
</style>
