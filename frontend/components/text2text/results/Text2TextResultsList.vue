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
  <results-list :dataset="dataset" @search-records="searchRecords">
    <template slot="record" slot-scope="slotProps">
      <record-text-2-text
        :dataset="dataset"
        :record="slotProps.record"
        :isReferenceRecord="slotProps.isReferenceRecord"
      />
    </template>
  </results-list>
</template>
<script>
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  methods: {
    searchRecords(query) {
      this.$emit("search-records", query);
    },
  },
};
</script>
