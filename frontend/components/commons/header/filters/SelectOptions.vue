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
      <ReCheckbox
        v-if="optionIsAString(option)"
        :id="option"
        v-model="selectedOptions"
        class="re-checkbox--dark"
        :value="option"
      >
        {{ option }}
      </ReCheckbox>
      <ReCheckbox
        v-else
        :id="option[0]"
        v-model="selectedOptions"
        class="re-checkbox--dark"
        :value="option[0]"
      >
        {{ option[0] }} ({{ option[1] | formatNumber }})
      </ReCheckbox>
    </li>
    <li v-if="!Object.entries(options).length">0 results</li>
  </ul>
  <ul v-else-if="type === 'single'">
    <li
      v-for="option in options"
      :key="optionName ? option[optionName] : option"
    >
      <a href="#" @click.prevent="select(option)">
        {{ optionName ? option[optionName] : option }}
      </a>
    </li>
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
      type: String,
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
      console.log(option);
      this.$emit("selected", option);
    },
    optionIsAString(option) {
      return typeof option === "string";
    },
  },
};
</script>

<style scoped lang="scss">
.re-checkbox {
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
  max-height: 188px;
  overflow-y: auto;
  margin: 0 -1em 0 -1em;
  padding: 0 1em 1em 1em;
  @extend %hide-scrollbar;
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
