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
  <div class="slides-nav">
    <a
      :class="itemNumber <= 0 ? 'disabled' : null"
      href="#"
      @click.prevent="prev(itemNumber)"
    >
      <svgicon name="chevron-left" width="8" height="8" color="#4C4EA3" />
    </a>
    {{ itemNumber + 1 }} of {{ slidesOrigin.length }} {{ slidesName }}
    <a
      :class="slidesOrigin.length <= itemNumber + 1 ? 'disabled' : null"
      href="#"
      @click.prevent="next(itemNumber)"
    >
      <svgicon name="chevron-right" width="8" height="8" />
    </a>
  </div>
</template>

<script>
export default {
  props: {
    itemNumber: {
      type: Number,
      required: true,
    },
    slidesName: {
      type: String,
    },
    slidesOrigin: {
      type: Array,
      required: true,
    },
  },
  methods: {
    prev(number) {
      this.$emit("go-to", --number);
    },
    next(number) {
      this.$emit("go-to", ++number);
    },
  },
};
</script>

<style scoped lang="scss">
.slides-nav {
  @include font-size(13px);
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 33%;
  margin-right: 33%;
  margin-left: auto;
  color: var(--fg-secondary);
  a {
    height: 20px;
    width: 20px;
    line-height: 19px;
    border-radius: $border-radius-s;
    text-align: center;
    margin-left: 1.5em;
    margin-right: 1.5em;
    display: inline-block;
    text-decoration: none;
    outline: none;
    @include font-size(13px);
    transition: all 0.2s ease-in-out;
    background: var(--bg-solid-grey-1);
    .svg-icon {
      fill: var(--bg-opacity-87);
    }
    &:hover {
      background: var(--bg-solid-grey-2);
      transition: all 0.2s ease-in-out;
    }
    &.disabled {
      opacity: 0.5;
      pointer-events: none;
    }
  }
}
</style>
