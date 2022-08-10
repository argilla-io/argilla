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
    :class="buttonClasses"
    :href="href"
    :loading="loading"
    :disabled="disabled"
    :target="target"
    :rel="newRel"
    @click="$emit('click', $event)"
  >
    <slot />
  </a>

  <nuxt-link
    v-else-if="to"
    :class="buttonClasses"
    :to="to"
    :loading="loading"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <slot />
  </nuxt-link>

  <button
    v-else
    :class="buttonClasses"
    tabindex="0"
    :loading="loading"
    :type="type"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <slot />
  </button>
</template>

<script>
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
    to: String,
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
        button: true,
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
  display: flex;
  position: relative;
  overflow: hidden;
  user-select: none;
  cursor: pointer;
  outline: 0;
  background: none;
  border: 0;
  border-radius: $button-radius;
  font-family: $sff;
  font-style: inherit;
  font-variant: inherit;
  letter-spacing: inherit;
  font-weight: 500;
  text-align: center;
  text-decoration: none;
  vertical-align: middle;
  white-space: nowrap;
  align-items: center;
  @include font-size(14px);
  line-height: 14px;
  padding: 12px 24px;
  transition: all 0.4s $cb-normal;
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
.button {
  @extend %button;
  :deep(.svg-icon) {
    margin-right: $base-space * 2;
    margin-left: -$base-space * 2;
  }
}
.small {
  @include font-size(13px);
  line-height: 13px;
  padding: 9px 18px;
  :deep(.svg-icon) {
    margin-right: $base-space;
    margin-left: -$base-space;
  }
}
.primary {
  background-color: $primary-color;
  color: palette(white);
  .svg-icon {
    fill: palette(white);
  }
  &:hover,
  &:focus,
  &:active,
  &.active {
    background-color: $primary-darken-color;
  }
  &.outline {
    background: none;
    border: 1px solid $primary-color;
    color: $primary-color;
    .svg-icon {
      fill: $primary-color;
    }
    &:hover,
    &:focus,
    &:active,
    &.active {
      color: $primary-darken-color;
      border-color: $primary-darken-color;
    }
  }
  &.clear {
    background: transparent;
    color: $font-dark;
    &:hover,
    &:focus,
    &:active,
    &.active {
      background: palette(grey, 700);
    }
  }
}

.secondary {
  background-color: palette(grey, 700);
  color: palette(blue, 200);
  .svg-icon {
    fill: palette(blue, 200);
  }
  &:hover,
  &:focus,
  &:active,
  &.active {
    background-color: $secondary-darken-color;
  }
  &.outline {
    background: none;
    border: 1px solid palette(grey, 600);
  }
}

.tertiary {
  background-color: none;
  color: $font-medium;
  .svg-icon {
    fill: $font-medium;
  }
  &:hover,
  &:focus,
  &:active,
  &.active {
    background-color: $font-dark;
  }
  &.outline {
    background: none;
    border: 1px solid $font-medium;
    &:hover,
    &:focus,
    &:active,
    &.active {
      border-color: $font-dark;
      color: $font-dark;
    }
  }
}
.quaternary {
  background-color: palette(white);
  color: $font-medium;
  .svg-icon {
    fill: $font-medium;
  }
  &:hover,
  &:focus,
  &:active,
  &.active {
    background-color: $font-dark;
  }
  &.outline {
    background: none;
    border: 1px solid palette(white);
    color: palette(white);
  }
}
</style>
