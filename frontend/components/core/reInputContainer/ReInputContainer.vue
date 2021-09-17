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
  <div class="re-input-container" :class="[classes]">
    <slot />

    <span v-if="enableCounter" class="re-count"
      >{{ inputLength }} / {{ counterLength }}</span
    >

    <button
      v-if="reClearable && hasValue"
      tabindex="-1"
      class="button-icon"
      @click="clearInput"
    >
      <re-icon>clear</re-icon>
    </button>
  </div>
</template>

<script>
import isArray from "~/components/core/utils/isArray";

export default {
  props: {
    reInline: Boolean,
    reClearable: Boolean,
  },
  data() {
    return {
      value: "",
      input: false,
      inputInstance: null,
      enableCounter: false,
      hasSelect: false,
      hasPlaceholder: false,
      hasFile: false,
      isDisabled: false,
      isRequired: false,
      isFocused: false,
      counterLength: 0,
      inputLength: 0,
    };
  },
  computed: {
    hasValue() {
      if (isArray(this.value)) {
        return this.value.length > 0;
      }

      return Boolean(this.value);
    },
    classes() {
      return {
        "re-input-inline": this.reInline,
        "re-clearable": this.reClearable,
        "re-has-select": this.hasSelect,
        "re-has-file": this.hasFile,
        "re-has-value": this.hasValue,
        "re-input-placeholder": this.hasPlaceholder,
        "re-input-disabled": this.isDisabled,
        "re-input-required": this.isRequired,
        "re-input-focused": this.isFocused,
      };
    },
  },
  mounted() {
    this.input = this.$el.querySelectorAll(
      "input, textarea, select, .re-file"
    )[0];

    if (!this.input) {
      this.$destroy();

      throw new Error(
        "Missing input/select/textarea inside re-input-container"
      );
    }
  },
  methods: {
    isInput() {
      return this.input && this.input.tagName.toLowerCase() === "input";
    },
    clearInput() {
      this.inputInstance.$el.value = "";
      this.inputInstance.$emit("input", "");
      this.setValue("");
    },
    setValue(value) {
      this.value = value;
    },
  },
};
</script>

<style lang="scss" scoped>
input:-webkit-autofill {
  box-shadow: 0 0 0px 1000px $lighter-color inset;
}

.re-input-container {
  input,
  textarea {
    width: 100%;
    height: $input-size;
    padding: 0;
    display: block;
    flex: 1;
    border: none !important;
    background: none;
    transition: $swift-ease-out;
    transition-property: font-size;
    color: $font-secondary;
    line-height: normal;
    @include input-placeholder {
      color: $font-secondary;
    }
    &:focus {
      outline: none;
    }
  }
}
</style>
