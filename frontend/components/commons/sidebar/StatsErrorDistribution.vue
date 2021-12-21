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
    <PieChart :percent="KoPercent" class="pie-chart" />
    <div class="info total">
      <label>Total records</label>
      <span class="records-number">
        {{ total | formatNumber }}
      </span>
    </div>
    <div class="info">
      <span class="color-bullet ok"></span>
      <label>Predicted ok</label>
      <span class="records-number">
        {{ predicted.ok | formatNumber }}
      </span>
    </div>
    <div class="info">
      <span class="color-bullet ko"></span>
      <label>Predicted ko</label>
      <span class="records-number">
        {{ predicted.ko | formatNumber }}
      </span>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  computed: {
    total() {
      return this.dataset.results.total;
    },
    predicted() {
      return this.dataset.results.aggregations.predicted;
    },
    KoPercent() {
      return (this.predicted.ko / this.total) * 100;
    },
  },
};
</script>

<style lang="scss" scoped>
.pie-chart {
  margin: 0 auto 2em auto;
}
.color-bullet {
  height: 10px;
  width: 10px;
  border-radius: 50%;
  display: inline-block;
  margin: 0.3em 0.3em 0.3em 0;
  &.ok {
    background: #50cb88;
  }
  &.ko {
    background: $error;
  }
}
.info {
  position: relative;
  display: flex;
  margin-bottom: 0.7em;
  color: $font-secondary-dark;
  &.total {
    margin-bottom: 1.5em;
  }
}
.records-number {
  margin-right: 0;
  margin-left: auto;
}
</style>
