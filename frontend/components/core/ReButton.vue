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
  <a
    v-if="href"
    class="re-button"
    :class="{ loading: loading, centered: centered }"
    :href="href"
    :loading="loading"
    :disabled="disabled"
    :target="target"
    :rel="newRel"
    @click="$emit('click', $event)"
  >
    <!-- <re-spinner v-if="loading"></re-spinner> -->
    <slot />
  </a>

  <button
    v-else
    class="re-button"
    :class="{ loading: loading, centered: centered }"
    tabindex="0"
    :loading="loading"
    :type="type"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <!-- <re-spinner v-if="loading"></re-spinner> -->
    <slot />
  </button>
</template>

<script>
// import reSpinner from '@recognai/re-commons/src/components/elements/core/reSpinner/reSpinner';

export default {
  name: "ReButton",
  props: {
    href: String,
    target: String,
    rel: String,
    type: {
      type: String,
      default: "button",
    },
    loading: Boolean,
    disabled: Boolean,
    centered: Boolean,
  },
  computed: {
    newRel() {
      if (this.target === "_blank") {
        return this.rel || "noopener";
      }

      return this.rel;
    },
  },
};
</script>

<style lang="scss" scoped>
.button-primary {
  @extend %button;
  background-color: $primary-color;
  color: $lighter-color;
  display: flex;
  .svg-icon {
    margin: auto 0.5em auto -0.3em;
    fill: $lighter-color;
  }
  &:hover,
  &:focus,
  &:active,
  &.active {
    background-color: $primary-darken-color;
  }
  &[disabled] {
    background-color: $primary-lighten-color;
    box-shadow: none;
  }
  &--main {
    @extend .button-primary;
    box-shadow: $shadow;
    min-height: 46px;
    line-height: 46px;
    &:hover,
    &:focus {
      box-shadow: none;
      background-color: $primary-color;
    }
  }
  &--small {
    @extend .button-primary;
    text-transform: none;
    min-height: 30px;
    line-height: 30px;
    min-width: auto;
  }
  &--outline {
    @extend .button-primary;
    background: transparent;
    border: 1px solid $primary-color;
    color: $primary-color;
    text-transform: none;
    display: flex;
    &:hover,
    &:focus {
      background: transparent;
      border-color: darken($primary-color, 10%);
      color: darken($primary-color, 10%);
    }
    &[disabled] {
      background-color: transparent;
      opacity: 0.6;
    }
  }
}

.button-secondary {
  @extend %button;
  background: $primary-color;
  color: $lighter-color;
  .svg-icon {
    margin: auto 0.5em auto -0.3em;
    fill: $secondary-color;
  }
  &:hover,
  &:focus,
  &:active,
  &.active {
    background-color: $primary-darken-color;
  }
  &[disabled] {
    background-color: lighten($primary-color, 20%);
  }
  &--small {
    @extend .button-secondary;
    text-transform: none;
    min-height: 30px;
    line-height: 30px;
    min-width: auto;
  }
  &--outline {
    @extend .button-secondary;
    background: transparent;
    border: 1px solid $line-smooth-color;
    color: $secondary-color;
    text-transform: none;
    display: flex;
    &:hover,
    &:focus {
      background: transparent;
      border-color: darken($line-smooth-color, 10%);
      color: darken($secondary-color, 10%);
    }
    &[disabled] {
      background-color: transparent;
      opacity: 0.6;
    }
  }
}

.button-tertiary {
  @extend %button;
  background: $font-medium-color;
  color: $lighter-color;
  .svg-icon {
    margin-right: 1em;
    vertical-align: middle;
    fill: $lighter-color;
  }
  &:hover,
  &:focus,
  &:active,
  &.active {
    background-color: darken($font-medium-color, 10%);
  }
  &[disabled] {
    background-color: lighten($font-medium-color, 20%);
  }
  &--outline {
    @extend .button-tertiary;
    background: transparent;
    border: 1px solid $primary-color;
    color: $primary-color;
    text-transform: none;
    &:hover,
    &:focus {
      background: transparent;
      border-color: darken($primary-color, 10%);
      color: darken($primary-color, 10%);
    }
    &[disabled] {
      background-color: transparent;
      opacity: 0.6;
    }
  }
  &--small {
    @extend .button-tertiary;
    text-transform: none;
    min-height: 30px;
    line-height: 30px;
    min-width: auto;
  }
}

.button-clear {
  @extend %button;
  @extend %clear;
  &:hover,
  &:focus {
    text-decoration: none;
    color: $font-dark-color;
  }
  &--small {
    @extend %button;
    @include font-size(12px);
    min-height: 26px;
    line-height: 26px;
    min-width: auto;
    background: none;
    text-transform: none;
    color: $font-medium-color;
  }
  &[disabled] {
    opacity: 0.4;
  }
}

.button-icon {
  cursor: pointer;
  background: transparent;
  border: 0;
  padding: 15px;
  outline: none;
  .hide {
    display: none;
  }
  .show {
    display: block;
  }
}

.modal-buttons {
  .re-button {
    margin-bottom: 0;
    &:last-child {
      margin-left: 1em;
    }
  }
}

// .button-group {
//     display: flex;
//     .re-button {
//         min-height: 50px;
//         width: 100%;
//         margin: 2px;
//         &:active {
//             color: $lighter-color;
//         }
//         &.inactive {
//             opacity: 0.5;
//             &:hover {
//                 opacity: 1;
//             }
//         }
//     }
// }

.re-button {
  .spinner {
    position: absolute;
    left: 1em;
    top: 0;
    bottom: 0;
    margin: auto;
  }
  &.loading {
    padding-left: 3.6em;
    .svg-icon {
      display: none;
    }
  }
}

.external-link,
.external-link a {
  position: relative;
  color: $primary-color;
  display: inline-block;
  margin-left: 1em;
  height: 30px;
  line-height: 30px;
  &:after {
    line-height: 1.4em;
  }
  &:hover,
  &:focus {
    transition: $swift-ease-in-out;
    color: darken($primary-color, 5%);
    .svg-icon {
      fill: darken($primary-color, 5%);
    }
  }
  .svg-icon {
    margin-left: 0.5em;
  }
}
.button-action {
  position: relative;
  color: $font-secondary;
  display: inline-block;
  height: 30px;
  line-height: 30px;
  margin-bottom: 0;
  text-transform: none;
  &:hover,
  &:focus {
    transition: $swift-ease-in-out;
    color: darken($primary-color, 5%);
    .svg-icon {
      fill: darken($primary-color, 5%);
    }
  }
  .svg-icon {
    margin-right: 0.5em;
  }
}
</style>
