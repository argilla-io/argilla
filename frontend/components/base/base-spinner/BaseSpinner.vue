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
  <div class="spinner"></div>
</template>

<script>
export default {
  name: "BaseSpinnerComponent",
};
</script>

<style lang="scss" scoped>
.spinner {
  width: $base-space * 4;
  height: $base-space * 4;
  border-radius: 50%;
  border: 5px solid palette(apricot);
  border-top-color: transparent;
  animation-name: spin;
  animation-iteration-count: infinite;
  animation-timing-function: linear;
  animation-duration: 1s;
}
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
