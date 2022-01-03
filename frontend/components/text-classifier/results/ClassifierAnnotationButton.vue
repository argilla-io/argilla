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
  <div
    class="re-annotation-button"
    :class="[classes, allowMultiple ? 'multiple' : 'single']"
  >
    <label :for="id" class="button" @click.prevent="toggleCheck">
      <span class="annotation-button-data__text" :title="label.class"
        >{{ label.class }}
      </span>
      <div v-if="label.score > 0" class="annotation-button-data__info">
        <span>{{ label.score | percent }}</span>
      </div>
    </label>
    <div
      class="annotation-button-container"
      tabindex="0"
      @click.stop="toggleCheck"
    >
      <input
        :id="id"
        type="checkbox"
        :disabled="disabled"
        :value="value"
        :checked="checked"
      />
    </div>
  </div>
</template>

<script>
export default {
  model: {
    prop: "areChecked",
    event: "change",
  },
  props: ["areChecked", "value", "id", "disabled", "label", "allowMultiple"],
  data() {
    return {
      checked: this.value || false,
    };
  },
  computed: {
    classes() {
      return {
        active: Array.isArray(this.areChecked)
          ? this.areChecked.includes(this.value)
          : this.checked,
        disabled: this.disabled,
      };
    },
  },
  watch: {
    value() {
      this.checked = !!this.value;
    },
  },
  methods: {
    toggleCheck() {
      if (!this.disabled) {
        let checked = this.areChecked;
        const found = checked.indexOf(this.value);
        if (found >= 0) {
          checked.splice(found, 1);
        } else {
          if (checked.length && !this.allowMultiple) {
            checked = [];
          }
          checked.push(this.value);
        }
        this.$emit("change", checked);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
$annotation-button-size: 20px;
$annotation-button-touch-size: 48px;
.re-annotation-button {
  width: auto;
  margin: 16px 8px 16px 0;
  display: inline-flex;
  position: relative;
  .annotation-button-container {
    display: none;
  }
  &.label-button {
    margin: 3.5px;
    color: $font-secondary-dark;
    padding: 0;
    transition: all 0.3s ease;
    max-width: 238px;
    .button {
      outline: none;
      cursor: pointer;
      background: #f0f0fe;
      border-radius: 8px;
      height: 40px;
      line-height: 40px;
      padding-left: 0.5em;
      padding-right: 0.5em;
      width: 100%;
      display: flex;
      font-family: $sff;
      font-weight: 500;
      overflow: hidden;
      color: $font-secondary-dark;
      box-shadow: 0;
      transition: all 0.2s ease-in-out;
    }
    &.predicted-label {
      .button {
        background: #d6d6ff;
      }
    }
    &.active {
      transition: all 0.2s ease-in-out;
      box-shadow: none;
      .button {
        transition: all 0.2s ease-in-out;
        background: $secondary-color;
        box-shadow: none;
      }
      &:hover {
        .button {
          transition: all 0.2s ease-in-out;
          box-shadow: 0 0 1px 0 rgba(212, 212, 212, 0.5),
            inset 0 -2px 6px 0 #3b3c81;
        }
      }
      &:after {
        display: none !important;
      }
      .annotation-button-data__text,
      .annotation-button-data__score {
        color: $lighter-color;
      }
      .annotation-button-data__info {
        color: $lighter-color;
      }
    }
    .annotation-button-data {
      overflow: hidden;
      transition: transform 0.3s ease;
      &__text {
        max-width: 200px;
        overflow: hidden;
        text-overflow: ellipsis;
        display: inline-block;
        white-space: nowrap;
        vertical-align: top;
      }
      &__info {
        margin-right: 0;
        margin-left: 1em;
        transform: translateY(0);
        transition: all 0.3s ease;
      }
      &__score {
        min-width: 40px;
        @include font-size(12px);
        display: inline-block;
        text-align: center;
        line-height: 1.5em;
        border-radius: 2px;
      }
    }
    &:not(.active):hover {
      .button {
        box-shadow: 0 0 1px 0 rgba(212, 212, 212, 0.5),
          inset 0 -2px 6px 1px #bbbce0;
      }
    }
  }
  &.disabled {
    opacity: 0.5;
  }
  &.non-reactive {
    pointer-events: none;
    cursor: pointer;
    // display: none;
    // &:nth-of-type(-n + 5) {
    //   display: inline-block;
    // }
    .button {
      background: $lighter-color !important;
      color: $lighter-color;
      border: 1px solid palette(grey, light);
    }
  }
  &:not(.disabled) {
    cursor: pointer;
    .annotation-button {
      cursor: pointer;
    }
  }
  .annotation-button {
    height: $annotation-button-size;
    padding-left: 8px;
    line-height: $annotation-button-size;
  }
}
</style>
