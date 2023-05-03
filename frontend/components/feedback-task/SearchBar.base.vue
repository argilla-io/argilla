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
  <div class="searchbar" :class="{ active: $attrs.value?.length }">
    <BaseIcon
      v-if="!$attrs.value?.length"
      icon-name="search"
      icon-width="20"
      icon-height="20"
    />
    <BaseButton v-else class="searchbar__button" @click="$emit('input', null)">
      <BaseIcon
        class="searchbar__button__icon"
        icon-name="close"
        icon-width="20"
        icon-height="20"
      />
    </BaseButton>
    <!-- <label class="searchbar__label" for="query" v-text="description" /> -->
    <input
      class="searchbar__input"
      ref="input"
      type="text"
      name="query"
      id="query"
      :value="$attrs.value"
      :placeholder="placeholder"
      @input="$emit('input', $event.target.value)"
      autocomplete="off"
    />
  </div>
</template>

<script>
export default {
  props: {
    placeholder: {
      type: String,
      default: "Introduce your text:",
    },
    // description: {
    //   type: String,
    //   default: "Introduce your text",
    // },
    bgColor: {
      type: String,
      default: "#ffffff",
    },
  },
};
</script>

<style lang="scss" scoped>
.searchbar {
  display: flex;
  align-items: center;
  gap: $base-space;
  max-width: 50vw;
  padding: $base-space * 1.4;
  background: palette(white);
  border-radius: $border-radius-s;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.13);
  transition: all 0.2s ease;
  &:hover {
    box-shadow: 0 6px 10px 0 rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
  }
  &__button.button {
    display: flex;
    padding: 0;
    &:hover {
      background: $black-4;
    }
  }
  &__button {
    &__icon {
      padding: calc($base-space / 2);
    }
  }
  // &__label {
  //   @extend %visuallyhidden;
  // }
  &__input {
    width: 100%;
    height: 1rem;
    padding: 0;
    border: none;
    outline: 0;
    background: none;
    line-height: 1rem;
  }
}
</style>
