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
  <div v-if="options.length">
    <RadioButtonsSelectBase
      :options="options"
      :selected-option="selectedOption"
      @change="changeOption"
    />
  </div>
</template>

<script>
export default {
  props: {
    options: {
      type: Array,
      required: true,
    },
    selectedOption: {
      type: String,
    },
  },
  model: {
    prop: "selectedOption",
    event: "change",
  },
  methods: {
    changeOption(id) {
      this.$emit("change", id);
      this.updateRouteQuery(id);
    },
    updateRouteQuery(query) {
      const currentQuery = this.$route.query;
      this.$router.push({
        query: { ...currentQuery, _status: query },
      });
    },
  },
};
</script>
