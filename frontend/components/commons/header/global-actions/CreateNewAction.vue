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
  <div class="new-label__container">
    <base-button
      v-if="!showLabelCreation"
      class="new-label__main-button secondary text"
      @click="openLabelCreation()"
      >{{ text }}</base-button
    >
    <div v-else class="new-label">
      <input
        ref="labelCreation"
        v-model="label"
        autofocus
        class="new-label__input"
        type="text"
        placeholder="New label"
        @keyup.enter="createNewLabel(label)"
      />
      <svgicon class="new-label__close" name="close" @click="reset()" />
      <base-button
        class="new-label__button primary small"
        :disabled="!label"
        @click="createNewLabel(label)"
        >Create</base-button
      >
    </div>
  </div>
</template>
<script>
export default {
  props: {
    text: {
      type: String,
      required: false,
      default: "Create label",
    },
  },
  data: () => ({
    label: undefined,
    showLabelCreation: false,
  }),

  methods: {
    createNewLabel(label) {
      if (!(label && label.trim())) {
        // If no label, nothing to do
        return;
      }
      this.$emit("new-label", label);
      this.reset();
    },
    openLabelCreation() {
      this.showLabelCreation = true;
      this.$nextTick(() => {
        this.$refs.labelCreation.focus();
      });
    },
    reset() {
      this.label = undefined;
      this.showLabelCreation = false;
    },
  },
};
</script>
<style lang="scss" scoped>
.new-label {
  width: 180px;
  border-radius: $border-radius;
  box-shadow: $shadow;
  padding: $base-space * 2;
  position: absolute;
  top: -1em;
  background: palette(white);
  text-align: left;
  &__close {
    position: absolute;
    top: 1.2em;
    right: 1em;
    cursor: pointer;
    height: 12px;
    width: 12px;
    stroke: $black-54;
    stroke-width: 1;
  }
  &__input {
    border: 0;
    outline: none;
    padding-right: 2em;
    width: 100%;
  }
  &__button {
    margin-top: 2em;
    margin-bottom: 0 !important;
  }
  &__main-button {
    margin-bottom: 0 !important;
    margin-right: 0;
    margin-left: auto;
  }
  &__container {
    text-align: right;
    position: relative;
  }
}
</style>
