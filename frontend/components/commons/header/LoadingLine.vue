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
  <span class="loading-line" :style="{ minWidth: 100 }"></span>
</template>

<script></script>

<style lang="scss" scoped>
.loading-line {
  height: 2px;
  position: absolute;
  width: 100%;
  background: $brand-primary-color;
  animation: load 0.8s ease-in-out infinite;
}
@keyframes load {
  0% {
    width: 0%;
  }

  100% {
    width: 100%;
  }
}
</style>
