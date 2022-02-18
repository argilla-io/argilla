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
  <results-list
    v-if="!dataset.viewSettings.visibleRulesList"
    :dataset="dataset"
    :metadata-item="selectedMetadataItem"
    @closeMetadata="resetMetadataItem"
  >
    <template slot="results-header">
      <rule-definition :dataset="dataset" v-if="showRulesArea" />
    </template>
    <template slot="record" slot-scope="results">
      <record-text-classification
        :dataset="dataset"
        :record="results.record"
        @onShowMetadata="onShowMetadata"
      />
    </template>
  </results-list>
  <rules-management class="content" v-else :dataset="dataset" />
</template>
<script>
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => ({
    selectedMetadataItem: undefined,
  }),
  computed: {
    showRulesArea() {
      return this.dataset.viewSettings.viewMode === "labelling-rules";
    },
  },
  methods: {
    onShowMetadata(id) {
      this.selectedMetadataItem = id;
    },
    resetMetadataItem() {
      this.selectedMetadataItem = undefined;
    },
  },
};
</script>
<style lang="scss" scoped>
.content {
  padding-right: calc(4em + 45px);
  .--metrics & {
    @include media(">desktop") {
      width: 100%;
      padding-right: calc(294px + 100px);
      transition: padding 0.1s ease-in-out;
    }
  }
  @include media(">desktop") {
    transition: padding 0.1s ease-in-out;
    width: 100%;
    padding-right: 100px;
  }
}
</style>
