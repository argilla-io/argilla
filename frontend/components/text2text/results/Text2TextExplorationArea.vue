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
    <div v-if="annotation.length && currentSentence === 'Annotation'">
      <text-2-text-list
        :predictions-length="prediction.length"
        :has-annotation-and-predictions="hasAnnotationAndPredictions"
        :sentences-origin="currentSentence"
        :list="annotation"
        :editable="false"
        @get-sentences="onGetSentences"
      />
    </div>
    <div v-else-if="prediction.length && currentSentence === 'Prediction'">
      <text-2-text-list
        :predictions-length="prediction.length"
        :show-score="true"
        :has-annotation-and-predictions="hasAnnotationAndPredictions"
        :sentences-origin="currentSentence"
        :list="prediction"
        :editable="false"
        @get-sentences="onGetSentences"
      />
    </div>
  </div>
</template>
<script>
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
  data: () => {
    return {
      currentSentence: "Annotation",
    };
  },
  computed: {
    hasAnnotationAndPredictions() {
      return this.prediction.length && this.annotation.length ? true : false;
    },
  },
  mounted() {
    if (!this.annotation.length && this.prediction.length) {
      this.currentSentence = "Prediction";
    }
  },
  methods: {
    onGetSentences() {
      this.currentSentence !== "Annotation"
        ? (this.currentSentence = "Annotation")
        : (this.currentSentence = "Prediction");
    },
    decorateScore(score) {
      return score * 100;
    },
  },
};
</script>
<style lang="scss" scoped></style>
