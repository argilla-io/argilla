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
  <div class="loading">
    <span class="line" :style="{ minWidth: 100 }"></span>
    <div v-for="i in size" :key="i">
      <div class="record"></div>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    size: {
      type: Number,
      default: 0,
    },
  },
};
</script>
<style lang="scss" scoped>
.loading {
  position: relative;
}
.line {
  height: 2px;
  position: absolute;
  top: 0;
  left: 0;
  background: $primary-color;
  animation: load 0.8s ease-in-out infinite;
}
.record {
  min-height: 150px;
  display: block;
  width: 100%;
  background: white;
  margin-bottom: 10px;
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
