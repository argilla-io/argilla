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
    <reButton
      v-if="!showLabelCreation"
      class="new-label__main-button button-secondary--outline"
      @click="openLabelCreation()"
      ><svgicon name="plus" width="10" height="10" />{{ text }}</reButton
    >
    <div v-else class="new-label">
      <input
        v-model="label"
        autofocus
        class="new-label__input"
        type="text"
        placeholder="New label"
        @keyup.enter="createNewLabel(label)"
      />
      <svgicon class="new-label__close" name="cross" @click="reset()" />
      <reButton
        class="new-label__button button-primary--small"
        :disabled="!label"
        @click="createNewLabel(label)"
        >Create</reButton
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
      default: "Create new label",
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
  border-radius: 3px;
  border: 2px solid $primary-color;
  padding: 1em;
  position: absolute;
  top: -1em;
  background: $lighter-color;
  text-align: left;
  &__close {
    position: absolute;
    top: 1.2em;
    right: 1em;
    cursor: pointer;
    height: 12px;
    width: 12px;
    stroke: $font-secondary;
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
    margin-right: 0;
    margin-left: auto;
    width: 180px;
  }
}
</style>
