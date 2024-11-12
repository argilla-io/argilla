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
  <RadioButtonsSelectBase
    v-if="options.length"
    class="filter-status"
    :options="options"
    :selected-option="selectedOption"
    @change="onChangeOption"
    aria-label="Filter Records by Status"
    aria-controls="dropdown-menu"
  />
</template>

<script>
import { RecordStatus } from "~/v1/domain/entities/record/RecordStatus";

export default {
  props: {
    selectedOption: {
      type: String,
    },
  },
  model: {
    prop: "selectedOption",
    event: "change",
  },
  data() {
    return {
      options: [
        {
          id: RecordStatus.pending.name,
          name: this.$tc(`recordStatus.${RecordStatus.pending.name}`, 1),
          color: RecordStatus.pending.color,
        },
        {
          id: RecordStatus.draft.name,
          name: this.$tc(`recordStatus.${RecordStatus.draft.name}`, 1),
          color: RecordStatus.draft.color,
        },
        {
          id: RecordStatus.discarded.name,
          name: this.$tc(`recordStatus.${RecordStatus.discarded.name}`, 1),
          color: RecordStatus.discarded.color,
        },
        {
          id: RecordStatus.submitted.name,
          name: this.$tc(`recordStatus.${RecordStatus.submitted.name}`, 1),
          color: RecordStatus.submitted.color,
        },
      ],
    };
  },
  methods: {
    onChangeOption(option) {
      this.$emit("change", option);
    },
  },
};
</script>

<style lang="scss" scoped>
.filter-status {
  flex-shrink: 0;
}
</style>
