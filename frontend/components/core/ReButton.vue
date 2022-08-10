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
    :class="buttonClasses"
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

  <nuxt-link
    v-else-if="to"
    class="re-button"
    :class="buttonClasses"
    :to="to"
    :loading="loading"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <!-- <re-spinner v-if="loading"></re-spinner> -->
    <slot />
  </nuxt-link>

  <button
    v-else
    class="re-button"
    :class="buttonClasses"
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
    buttonClasses() {
      return {
        loading: this.loading,
        centered: this.centered,
      };
    },
  },
};
</script>

<style lang="scss" scoped>
// buttons
%button {
  position: relative;
  min-width: auto;
  min-height: $button-height;
  padding: 0 1.2em 0 1.2em;
  display: inline-block;
  position: relative;
  overflow: hidden;
  user-select: none;
  cursor: pointer;
  outline: 0;
  background: none;
  border: 0;
  border-radius: $button-radius;
  font-family: $sff;
  @include font-size(13px);
  font-style: inherit;
  font-variant: inherit;
  letter-spacing: inherit;
  font-weight: 500;
  line-height: $button-height;
  text-align: center;
  text-decoration: none;
  vertical-align: middle;
  white-space: nowrap;
  margin-bottom: 10px;
  transition: all 0.4s $cb-fast;
  &:focus {
    outline: 0;
  }
  &::-moz-focus-inner {
    border: 0;
  }
  &[disabled] {
    opacity: 0.5;
    cursor: default;
    pointer-events: none;
  }
}
.button-primary {
  @extend %button;
  background-color: $primary-color;
  color: palette(white);
  display: flex;
  .svg-icon {
    margin: auto 0.5em auto -0.3em;
    fill: palette(white);
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
  color: palette(white);
  .svg-icon {
    margin: auto 0.5em auto -0.3em;
    fill: palette(blue, 300);
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
    border: 1px solid palette(grey, 600);
    color: palette(blue, 300);
    text-transform: none;
    display: flex;
    &:hover,
    &:focus {
      background: transparent;
      border-color: darken(palette(grey, 600), 10%);
      color: darken(palette(blue, 300), 10%);
    }
    &[disabled] {
      background-color: transparent;
      opacity: 0.6;
    }
  }
}

.button-tertiary {
  @extend %button;
  background: $font-medium;
  color: palette(white);
  .svg-icon {
    margin-right: 1em;
    vertical-align: middle;
    fill: palette(white);
  }
  &:hover,
  &:focus,
  &:active,
  &.active {
    background-color: darken($font-medium, 10%);
  }
  &[disabled] {
    background-color: lighten($font-medium, 20%);
  }
  &--outline {
    @extend .button-tertiary;
    background: transparent;
    border: 1px solid $primary-color;
    color: $primary-color;
    text-transform: none;
    .svg-icon {
      fill: $primary-color;
    }
    &:hover,
    &:focus {
      background: transparent;
      border-color: darken($primary-color, 10%);
      color: darken($primary-color, 10%);
      .svg-icon {
        fill: darken($primary-color, 10%);
      }
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

.button-quaternary {
  @extend %button;
  background: palette(white);
  color: $font-dark;
  border: 1px solid palette(grey, 600);
  box-shadow: inset 0 -2px 6px 0 rgba(223, 223, 223, 0.5);
  .svg-icon {
    margin: auto 1em auto auto;
    vertical-align: middle;
    fill: $font-dark;
  }
  &:hover,
  &:focus,
  &:active,
  &.active {
    background-color: palette(white);
    border: 1px solid darken(palette(grey, 600), 10%);
  }
  &[disabled] {
    background-color: palette(white);
  }
  &--small {
    @extend .button-quaternary;
    text-transform: none;
    min-height: 30px;
    line-height: 30px;
    min-width: auto;
  }
  &--outline {
    @extend .button-quaternary;
    background: transparent;
    border: 1px solid palette(white);
    color: palette(white);
    text-transform: none;
    display: flex;
    box-shadow: none;
    &:hover,
    &:focus {
      background: transparent;
      border-color: darken(palette(white), 10%);
      color: darken(palette(white), 10%);
    }
    &[disabled] {
      background-color: transparent;
      opacity: 0.6;
    }
  }
}

.button-clear {
  @extend %button;
  @extend %clear;
  &:hover,
  &:focus {
    text-decoration: none;
    color: $font-dark;
  }
  &--small {
    @extend %button;
    @include font-size(12px);
    min-height: 26px;
    line-height: 26px;
    min-width: auto;
    background: none;
    text-transform: none;
    color: $font-medium;
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

.re-button {
  font-family: $sff;
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
  color: $font-secondary-medium;
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
