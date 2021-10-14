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
  <div class="re-annotation-button" :class="classes">
    <label :for="id" class="button" @click.prevent="toggleCheck">
      <span class="annotation-button-data__text" :title="label.class"
        >{{ label.class }}
      </span>
      <div class="annotation-button-data__info" v-if="!label.selected && label.score > 0">
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
    margin: auto auto 20px auto;
    color: $darker-color;
    padding: 0;
    transition: all 0.3s ease;
    max-width: 238px;
    width: 100%;
    border-radius: 7px;
    .button {
      outline: none;
      cursor: pointer;
      border-radius: 5px;
      background: $lighter-color;
      border: 1px solid $line-smooth-color;
      height: 40px;
      line-height: 40px;
      padding-left: 0.5em;
      padding-right: 0.5em;
      width: 100%;
      display: flex;
      font-weight: 600;
      overflow: hidden;
      color: $darker-color;
    }
    &.active {
      .button {
        background: $secondary-color;
        border: 1px solid $line-smooth-color;;
      }
      transition: all 0.02s ease-in-out;
      box-shadow: none; // Animate the size, outside
      animation: pulse 0.4s;
      transform: scale3d(1, 1, 1);
      -webkit-font-smoothing: antialiased;
      transform: translate3d(1, 1, 1); // z-index: 1;
      &:after {
        display: none !important;
      }
      @keyframes pulse {
        0% {
          transform: scale3d(1, 1, 1);
        }
        70% {
          transform: scale3d(1.04, 1.04, 1.04);
        }
        100% {
          transform: scale3d(1, 1, 1);
        }
      }
      @keyframes pulse-font {
        0% {
          transform: scale3d(1, 1, 1);
        }
        70% {
          transform: scale3d(1.06, 1.06, 1.06);
        }
        100% {
          transform: scale3d(1, 1, 1);
        }
      }
      .annotation-button-data__text,
      .annotation-button-data__score {
        color: $lighter-color;
        animation: pulse-font 0.5s;
      }
      .annotation-button-data__info {
        display: none;
      }
    }
    .annotation-button-data {
      overflow: hidden;
      transition: transform 0.3s ease;
      &__text {
        max-width: calc(100% - 10px);
        overflow: hidden;
        text-overflow: ellipsis;
        display: inline-block;
        white-space: nowrap;
        vertical-align: top;
      }
      &__info {
        margin-right: 0;
        margin-left: auto;
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
      box-shadow: 0px 3px 8px 3px rgba(222, 222, 222, 0.4) !important;
      border-color: $line-light-color;
    }
  }
  &.disabled {
    opacity: 0.5;
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
