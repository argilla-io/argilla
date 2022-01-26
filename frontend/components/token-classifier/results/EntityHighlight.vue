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
  <span
    :class="['highlight', span.entity.origin, isText ? '' : 'highlight--block']"
  >
    <span
      class="highlight__content"
      @click="openTagSelector"
      @dblclick="removeEntity"
      v-html="$highlightSearch(dataset.query.text, text)"
    />
    <span class="highlight__label">
      <span
        :class="[
          'highlight__tooltip',
          annotationEnabled ? 'highlight__tooltip--icon' : '',
        ]"
      >
        <span
          class="highlight__tooltip__origin"
          v-if="span.entity.origin === 'annotation'"
          >Annot.</span
        >
        <span
          >{{ span.entity.label }}
          <svgicon
            v-if="annotationEnabled"
            width="8"
            height="8"
            name="cross"
            @click="removeEntity"
          ></svgicon>
        </span>
      </span>
    </span>
  </span>
</template>
<script>
import "assets/icons/cross";

export default {
  props: {
    span: {
      type: Object,
      required: true,
    },
    text: {
      type: String,
      required: true,
    },
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => {
    return {
      singleClickDelay: 300,
      doubleClicked: false,
      clicked: false,
    };
  },
  computed: {
    isText() {
      return this.text.replace(/\s/g, "").length;
    },
    annotationEnabled() {
      return this.dataset.viewSettings.viewMode === "annotate";
    },
  },
  methods: {
    openTagSelector() {
      this.clicked = true;
      if (this.annotationEnabled) {
        setTimeout(() => {
          if (!this.doubleClicked) {
            this.$emit("openTagSelector");
          }
          this.clicked = false;
        }, this.singleClickDelay);
      }
    },
    removeEntity() {
      this.doubleClicked = true;
      if (this.annotationEnabled) {
        this.$emit("removeEntity");
        setTimeout(() => {
          this.doubleClicked = false;
        }, this.singleClickDelay);
      }
    },
  },
};
</script>
<style lang="scss" scoped>
.highlight {
  @include font-size(16px);
  line-height: 1em;
  position: relative;
  cursor: default;
  // display: inline-flex;
  border-radius: 2px;
  padding: 0;
  margin-right: -3.2px;
  &--block {
    display: block;
    .highlight__content:after {
      content: "";
      position: absolute;
      top: 0;
      width: 100%;
      height: 100%;
    }
  }
  &__label {
    @include font-size(0px);
  }
  &__content {
    display: inline;
  }
  &__tooltip {
    display: block;
    position: absolute;
    border-radius: 2px;
    padding: 4px 9px 5px 9px;
    opacity: 0;
    z-index: -1;
    margin-bottom: 0.5em;
    transition: opacity 0.5s ease, z-index 0.2s ease;
    white-space: nowrap;
    user-select: none;
    cursor: default;
    font-weight: 600;
    right: 50%;
    transform: translateX(50%);
    @include font-size(12px);
    & > span {
      display: block;
    }
    &__origin {
      @include font-size(8px);
    }
    .annotation & {
      bottom: 100%;
    }
    .prediction & {
      top: calc(100% + 15px);
    }
    &--icon {
      padding-right: 20px;
      .svg-icon {
        position: absolute;
        top: 8px;
        right: 8px;
        cursor: pointer;
      }
    }
  }
  &__tooltip:after {
    margin: auto;
    position: absolute;
    right: 0;
    left: 0;
    .annotation & {
      @include triangle(bottom, 6px, 6px, auto);
      bottom: 5px;
      transform: translateY(10px);
    }
    .prediction & {
      @include triangle(top, 6px, 6px, auto);
      top: -15px;
      transform: translateY(10px);
    }
  }
  &:hover .highlight__tooltip {
    opacity: 1;
    transition-delay: 0s;
    z-index: 4;
  }
}
</style>
