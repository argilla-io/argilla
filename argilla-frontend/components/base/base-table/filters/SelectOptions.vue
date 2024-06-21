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
  <ul v-if="type === 'multiple'">
    <li v-for="(option, index) in options" :key="index">
      <base-checkbox
        :id="optionValue(option)"
        v-model="selectedOptions"
        class="checkbox--dark"
        :value="optionValue(option)"
      >
        {{ optionName(option) }}
        <template v-if="optionCounter(option) !== undefined"
          >({{ optionCounter(option) | formatNumber }})</template
        >
      </base-checkbox>
    </li>
    <li v-if="!Object.entries(options).length">0 results</li>
  </ul>
  <ul v-else-if="type === 'single'" class="--single">
    <li v-for="option in options" :key="optionName(option)">
      <a href="#" @click.prevent="select(option)">
        {{ optionName(option) }}
      </a>
    </li>
    <li v-if="!options.length">0 results</li>
  </ul>
</template>

<script>
export default {
  props: {
    options: {
      type: Array,
      default: () => [],
    },
    value: {
      type: Array,
      default: () => [],
    },
    optionName: {
      type: Function,
      default: (option) => option,
    },
    optionValue: {
      type: Function,
      default: (option) => option,
    },
    optionCounter: {
      type: Function,
      default: () => undefined,
    },
    type: {
      type: String,
      required: false,
      default: "multiple",
      validator: function (value) {
        return ["multiple", "single"].includes(value);
      },
    },
  },
  computed: {
    selectedOptions: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
  methods: {
    select(option) {
      this.$emit("selected", option);
    },
  },
};
</script>

<style scoped lang="scss">
.checkbox {
  margin: 0;
  width: 100% !important;
  cursor: default;
}
.checkbox-label {
  height: auto;
  white-space: normal;
  text-transform: none;
  word-break: break-word;
  hyphens: auto;
}
ul {
  max-height: 205px;
  overflow-y: auto;
  margin: 0 -1em 0 -1em;
  padding: 0 1em 1em 1em;
  &.--single {
    padding-bottom: 0;
    margin-bottom: -0.5em;
  }
}
li {
  padding: 0.4em 0;
  list-style: none;
}
a {
  text-decoration: none;
  max-width: 250px;
  display: block;
  word-break: break-word;
  hyphens: auto;
}
</style>
