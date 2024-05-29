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
        <BaseButton
          class="selected-option"
          :class="currentOptionId"
          :data-title="$t('status')"
        >
          {{ currentOptionName }}
          <svgicon name="chevron-down" width="8" height="8" />
        </BaseButton>
      </span>
      <span slot="dropdown-content">
        <ul class="options" role="radiogroup">
          <li
            v-for="{ id, name } in options"
            class="option"
            :class="id"
            :key="id"
            tabindex="0"
            :aria-checked="id"
            role="radio"
            @keydown.space="changeOption(id)"
            @keydown.enter="changeOption(id)"
          >
            <BaseRadioButton
              class="option__radio"
              :color="getRadioColor(id)"
              :id="id"
              :model="id"
              :value="selectedOption"
              @change="changeOption(id)"
              tabindex="-1"
              aria-hidden="true"
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
          return "#BB720A";
        case "submitted":
          return "#3E5CC9";
        case "draft":
          return "#73BFBD";
      }
    },
  },
};
</script>

<style lang="scss" scoped>
$selector-width: 140px;
.options {
  display: flex;
  flex-direction: column;
  gap: calc($base-space / 2);
  padding: $base-space;
  margin: 0;
  width: $selector-width;
  list-style: none;
}
.option {
  padding: $base-space;
  border-radius: $border-radius;
  &:focus {
    outline: none;
  }
  &.discarded {
    &:hover,
    &:focus-within {
      background: lighten($discarded-color, 30%);
    }
  }
  &.submitted {
    &:hover,
    &:focus-within {
      background: lighten($submitted-color, 44%);
    }
  }
  &.pending {
    &:hover,
    &:focus-within {
      background: lighten($pending-color, 54%);
    }
  }
  &.draft {
    &:hover,
    &:focus-within {
      background: lighten($draft-color, 56%);
    }
  }
  &__radio {
    margin: 0;
    &:focus {
      outline: none;
    }
  }
}
.button.selected-option {
  display: flex;
  align-items: center;
  gap: $base-space;
  padding: $base-space;
  background: palette(white);
  @include font-size(14px);
  &.discarded {
    color: $black-54;
    border: 1px solid $discarded-color;
    &:before {
      background: $discarded-color;
    }
  }
  &.submitted {
    color: $submitted-color;
    border: 1px solid $submitted-color;
    &:before {
      background: $submitted-color;
    }
  }
  &.pending {
    color: $pending-color;
    border: 1px solid $pending-color;
    &:before {
      background: $pending-color;
    }
  }
  &.draft {
    color: $draft-color;
    border: 1px solid $draft-color;
    &:before {
      background: $draft-color;
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

[data-title] {
  overflow: visible;
  @include tooltip-mini("top");
}
</style>
