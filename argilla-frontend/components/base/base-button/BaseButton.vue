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
    @click="onClick"
    @mouseover="$emit('mouseover')"
    @mouseleave="$emit('mouseleave')"
  >
    <slot />
  </a>

  <nuxt-link
    v-else-if="to"
    :class="buttonClasses"
    :to="to"
    :loading="loading"
    :disabled="disabled"
    @click="onClick"
    @mouseover="$emit('mouseover')"
    @mouseleave="$emit('mouseleave')"
  >
    <slot />
  </nuxt-link>

  <button
    v-else
    :class="buttonClasses"
    :tabindex="tabIndex"
    :loading="loading"
    :type="type"
    :disabled="disabled"
    @click="onClick"
    @mouseover="$emit('mouseover')"
    @mouseleave="$emit('mouseleave')"
  >
    <BaseSpinner
      class="spinner"
      v-if="loading"
      :size="20"
      :progress="loadingProgress"
    />
    <slot />
  </button>
</template>

<script>
export default {
  name: "BaseButton",
  props: {
    tabIndex: {
      type: Number,
      default: 0,
    },
    href: String,
    target: String,
    rel: String,
    type: {
      type: String,
      default: "button",
    },
    loading: Boolean,
    loadingProgress: {
      type: Number,
      default: 0,
    },
    disabled: Boolean,
    centered: Boolean,
    to: { type: String | Object },
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
  methods: {
    onClick($event) {
      //FIXME - replace "click" event by "on-click"
      this.$emit("click", $event);
      this.$emit("on-click", $event);
    },
  },
};
</script>

<style lang="scss" scoped>
// buttons
%button {
  position: relative;
  display: flex;
  align-items: center;
  gap: $base-space;
  min-width: auto;
  overflow: hidden;
  user-select: none;
  outline: 0;
  background: none;
  border: 0;
  border-radius: $button-radius;
  font-style: inherit;
  font-variant: inherit;
  letter-spacing: inherit;
  font-weight: 500;
  text-align: center;
  text-decoration: none;
  white-space: nowrap;
  @include font-size(14px);
  line-height: 14px;
  padding: 12px 24px;
  transition: background 0.3s ease-in;
  cursor: pointer;
  &[disabled] {
    opacity: 0.5;
    cursor: default;
    pointer-events: none;
  }
  &:focus {
    outline: 2px solid var(--bg-action);
  }
  &:focus:not(:focus-visible) {
    outline: none;
  }
}
.button {
  @extend %button;
  .spinner {
    flex-shrink: 0;
    border: 3px solid var(--bg-opacity-54);
    border-top-color: var(--bg-opacity-10);
  }
}
.small {
  @include font-size(13px);
  line-height: 13px;
  padding: $base-space;
}
.full-width {
  width: 100%;
  justify-content: center;
}
.primary {
  background-color: var(--bg-action);
  color: var(--color-white);
  .svg-icon {
    fill: var(--color-white);
  }
  .spinner {
    border-color: #ffffff40;
    border-top-color: var(--color-white);
  }
  &:hover,
  &:active,
  &.active {
    background-color: var(--bg-action-accent);
  }
  &.outline {
    background: none;
    border: 1px solid var(--bg-action);
    color: var(--bg-action);
    .svg-icon {
      fill: var(--bg-action);
    }
    &:hover,
    &:active,
    &.active {
      color: var(--bg-action-accent);
      border-color: var(--bg-action-accent);
    }
  }
  &.text {
    padding-left: 0;
    padding-right: 0;
    background: none;
    color: var(--bg-action);
    border-radius: 0;
    &:hover {
      background: none;
      color: var(--bg-action-accent);
    }
  }
}

.secondary {
  background-color: var(--bg-opacity-4);
  color: var(--fg-secondary);
  .svg-icon {
    fill: var(--fg-secondary);
  }
  .spinner {
    border-color: var(--fg-secondary);
  }
  &:hover,
  &:active,
  &.active {
    background-color: var(--bg-opacity-6);
  }
  &.outline {
    background: none;
    border: 1px solid var(--fg-secondary);
    color: var(--fg-secondary);
  }
  &.light {
    background: hsl(from var(--bg-opacity-4) h s l / 3%);
    color: var(--fg-secondary);
    &:hover,
    &:active,
    &.active {
      background: var(--bg-opacity-6);
    }
    .svg-icon {
      fill: var(--fg-secondary);
    }
  }

  &.text {
    padding-left: 0;
    padding-right: 0;
    background: none;
    color: var(--fg-secondary);
    border-radius: 0;
    &:hover {
      background: none;
      color: var(--fg-primary);
    }
  }
}
.--danger {
  background-color: var(--color-danger);
  color: var(--color-white);
  .svg-icon {
    fill: var(--color-white);
  }
  &:hover,
  &:active,
  &.active {
    background-color: hsl(from var(--color-danger) h s calc(l - 4));
  }
  &.outline {
    background: none;
    border: 1px solid var(--color-danger);
    color: var(--color-danger);
    .svg-icon {
      fill: var(--color-danger);
    }
    &:hover,
    &:active,
    &.active {
      color: hsl(from var(--color-danger) h s calc(l - 4));
      border-color: hsl(var(--color-danger) calc(l - 4));
    }
  }
  &.light {
    background: var(--bg-opacity-2);
    color: var(--color-danger);
    &:hover,
    &:active,
    &.active {
      background: var(--bg-opacity-4);
    }
  }
  &.link {
    background: none;
    color: var(--color-danger);
    &:hover {
      text-decoration: underline;
      background: none;
    }
  }
}
.clear {
  background: none;
  height: 30px;
  &:hover,
  &:active,
  &.active {
    background: var(--bg-opacity-4);
  }
}
</style>
