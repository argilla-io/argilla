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
  <div v-if="items && items < total" class="show-more-data">
    <p>{{ items }} of {{ total }} records</p>
    <ReProgress
      class="re-progress--minimal"
      re-mode="determinate"
      :progress="shownRecordsProgress"
    />
    <ReButton class="button-tertiary--outline" @click="$emit('moredata')">
      Next {{ moreDataSize }} records
    </ReButton>
  </div>
</template>

<script>
export default {
  props: {
    items: {
      default: undefined,
      type: Number,
    },
    total: {
      default: undefined,
      type: Number,
    },
    moreDataSize: {
      type: Number,
      default: 5,
    },
  },
  data: () => ({}),
  computed: {
    shownRecordsProgress() {
      const progress = (100 * this.items) / this.total;
      return progress;
    },
  },
};
</script>
<style lang="scss" scoped>
.show-more-data {
  padding-top: 1em;
  text-align: center;
  display: block;
  margin-bottom: 2em;
  @include font-size(13px);
  .re-progress {
    width: 300px;
    margin: 1.5em auto;
    background: $line-smooth-color;
  }
  .re-button {
    margin-bottom: 0;
  }
}
</style>
