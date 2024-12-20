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
    <BaseDropdown
      id="dropdown-menu"
      :visible="dropdownIsVisible"
      @visibility="onVisibility"
    >
      <span slot="dropdown-header">
        <BaseButton
          class="selected-option"
          :class="currentOptionId"
          :data-title="$t('status')"
          aria-haspopup="listbox"
          :aria-expanded="dropdownIsVisible"
          :aria-label="`Selected option: ${currentOptionName}`"
        >
          {{ currentOptionName }}
          <svgicon
            name="chevron-down"
            width="8"
            height="8"
            aria-hidden="true"
          />
        </BaseButton>
      </span>
      <span slot="dropdown-content">
        <ul class="options" role="group">
          <li
            v-for="{ id, name, color } in options"
            class="option"
            :class="id"
            :key="id"
            tabindex="0"
            :aria-checked="id === selectedOption"
            :aria-label="name"
            role="radio"
            @keydown.space="changeOption(id)"
            @keydown.enter="changeOption(id)"
          >
            <BaseRadioButton
              class="option__radio"
              :color="color"
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
  text-transform: capitalize;
  padding: $base-space;
  border-radius: $border-radius;
  &:focus {
    outline: none;
  }
  &.discarded {
    &:hover,
    &:focus-within {
      background: hsl(from var(--fg-status-discarded) h s l / 10%);
    }
  }
  &.submitted {
    &:hover,
    &:focus-within {
      background: hsl(from var(--fg-status-submitted) h s l / 10%);
    }
  }
  &.pending {
    &:hover,
    &:focus-within {
      background: hsl(from var(--fg-status-pending) h s l / 10%);
    }
  }
  &.draft {
    &:hover,
    &:focus-within {
      background: hsl(from var(--fg-status-draft) h s l / 10%);
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
  background: var(--bg-accent-grey-1);
  @include font-size(14px);
  text-transform: capitalize;
  &.discarded {
    color: var(--fg-secondary);
    border: 1px solid var(--fg-status-discarded);
    &:before {
      background: var(--fg-status-discarded);
    }
  }
  &.submitted {
    color: var(--fg-status-submitted);
    border: 1px solid var(--fg-status-submitted);
    &:before {
      background: var(--fg-status-submitted);
    }
  }
  &.pending {
    color: var(--fg-status-pending);
    border: 1px solid var(--fg-status-pending);
    &:before {
      background: var(--fg-status-pending);
    }
  }
  &.draft {
    color: var(--fg-status-draft);
    border: 1px solid var(--fg-status-draft);
    &:before {
      background: var(--fg-status-draft);
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
