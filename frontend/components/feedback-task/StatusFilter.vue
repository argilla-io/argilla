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
  <div v-if="options.length" :style="cssVars">
    <BaseDropdown :visible="dropdownIsvisible" @visibility="onVisibility">
      <span slot="dropdown-header">
        <BaseButton class="selected-option">
          {{ currentOptionName }}
          <svgicon name="chevron-down" />
        </BaseButton>
      </span>
      <span slot="dropdown-content">
        <ul class="options">
          <li
            v-for="{ id, name, color, bgColor } in options"
            class="option"
            :key="id"
            :style="{
              backgroundColor: bgColor,
            }"
          >
            <BaseRadioButton
              class="option__radio"
              :color="color"
              :id="id"
              :model="id"
              :value="selectedStatus"
              @change="changeOption(id)"
              >{{ name }}</BaseRadioButton
            >
          </li>
        </ul>
      </span>
    </BaseDropdown>
  </div>
</template>

<script>
export default {
  props: {
    options: {
      type: Array,
      required: true,
    },
    selectedStatus: {
      type: String,
    },
  },
  data() {
    return {
      dropdownIsvisible: false,
    };
  },
  model: {
    prop: "selectedStatus",
    event: "change",
  },
  computed: {
    currentOption() {
      return this.options.find((opt) => opt.id === this.selectedStatus);
    },
    currentOptionId() {
      return this.currentOption?.id;
    },
    currentOptionName() {
      return this.currentOption?.name;
    },
    cssVars() {
      return {
        "--selected-option-color": this.currentOption?.color,
        "--selected-option-text-color": this.currentOption?.textColor,
      };
    },
  },
  methods: {
    onVisibility(value) {
      this.dropdownIsvisible = value;
    },
    changeOption(id) {
      this.$emit("change", id);
    },
  },
};
</script>

<style lang="scss" scoped>
$selector-width: 160px;
.options {
  display: flex;
  flex-direction: column;
  gap: calc($base-space / 2);
  min-width: $selector-width;
  padding: calc($base-space / 2);
  margin: 0;
  list-style: none;
}
.option {
  padding: $base-space;
  border-radius: $border-radius;
  &:not(:hover) {
    background: palette(white) !important;
    transition: background 0.2s ease-in;
  }
  &__radio {
    margin: 0;
  }
}
.button.selected-option {
  min-width: $selector-width;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: $base-space + 4px;
  background: palette(white);
  color: var(--selected-option-text-color);
  border: 1px solid var(--selected-option-color);
  .svg-icon {
    margin-left: auto;
  }
  &:before {
    content: "";
    height: $base-space;
    width: $base-space;
    background: var(--selected-option-color);
    border-radius: 50%;
  }
}
</style>
