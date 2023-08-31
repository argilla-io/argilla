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
    <BaseDropdown :visible="dropdownIsVisible" @visibility="onVisibility">
      <span slot="dropdown-header">
        <BaseButton class="selected-option" :class="currentOptionId">
          {{ currentOptionName }}
          <svgicon name="chevron-down" />
        </BaseButton>
      </span>
      <span slot="dropdown-content">
        <ul class="options">
          <li
            v-for="{ id, name } in options"
            class="option"
            :class="id"
            :key="id"
          >
            <BaseRadioButton
              class="option__radio"
              :color="getRadioColor(id)"
              :id="id"
              :model="id"
              :value="selectedOption"
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
import "assets/icons/chevron-down";
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
  data() {
    return {
      dropdownIsVisible: false,
    };
  },
  model: {
    prop: "selectedOption",
    event: "change",
  },
  computed: {
    currentOption() {
      return this.options.find((opt) => opt.id === this.selectedOption);
    },
    currentOptionId() {
      return this.currentOption?.id;
    },
    currentOptionName() {
      return this.currentOption?.name;
    },
  },
  methods: {
    onVisibility(value) {
      this.dropdownIsVisible = value;
    },
    changeOption(id) {
      this.$emit("change", id);
      this.dropdownIsVisible = false;
    },
    getRadioColor(status) {
      switch (status) {
        case "discarded":
          return "#B7B7B7";
        case "pending":
          return "#B6B9FF";
        case "submitted":
          return "#3E5CC9";
        default:
      }
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
  &.discarded {
    &:hover {
      background: #f2f2f2;
    }
  }
  &.submitted {
    &:hover {
      background: #ebf3ff;
    }
  }
  &.pending {
    &:hover {
      background: #eeeeff;
    }
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
  &.discarded {
    color: #656363;
    border: 1px solid #b7b7b7;
    &:before {
      background: #b7b7b7;
    }
  }
  &.submitted {
    color: #3e5cc9;
    border: 1px solid #3e5cc9;
    &:before {
      background: #3e5cc9;
    }
  }
  &.pending {
    color: #4c4ea3;
    border: 1px solid #b6b9ff;
    &:before {
      background: #b6b9ff;
    }
  }
  .svg-icon {
    margin-left: auto;
  }
  &:before {
    content: "";
    height: $base-space;
    width: $base-space;
    border-radius: 50%;
  }
}
</style>
