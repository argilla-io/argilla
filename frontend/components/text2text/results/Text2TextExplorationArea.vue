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
  <div v-if="annotation.length || prediction.length">
    <re-tabs
      :tabs="availableTabs"
      :active-tab="showTab"
      @change-tab="onChangeTab"
    >
      <div>
        <template v-if="showTab === 'Prediction'">
          <text-2-text-list :show-score="true" :list="prediction" />
        </template>
        <template v-if="showTab === 'Annotation'">
          <text-2-text-list :list="annotation" />
        </template>
      </div>
    </re-tabs>
  </div>
</template>
<script>
import "assets/icons/chev-left";
import "assets/icons/chev-right";
export default {
  props: {
    annotation: {
      type: Array,
      required: true,
    },
    prediction: {
      type: Array,
      required: true,
    },
  },
  data: () => ({
    showTab: "Prediction",
    predictionNumber: 0,
  }),
  mounted() {
    this.showTab = this.availableTabs.includes('Prediction') ? 'Prediction' : 'Annotation'
  },
  computed: {
    availableTabs() {
      let tabs = [];
      if (this.prediction.length) {
        tabs.push("Prediction");
      }
      if (this.annotation.length) {
        tabs.push("Annotation");
      }
      return tabs;
    },
  },
  methods: {
    onChangeTab(tab) {
      this.showTab = tab;
    },
    showPredictionNumber(index) {
      this.predictionNumber = index;
    },
    decorateScore(score) {
      return score * 100;
    },
  },
};
</script>
<style lang="scss" scoped></style>
