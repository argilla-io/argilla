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
    :class="[
      'highlight',
      span.origin,
      isText ? '' : 'highlight--block',
      annotationEnabled ? 'editable' : null,
    ]"
  >
    <span
      class="highlight__content"
      @click="openTagSelector"
      @dblclick="removeEntity"
    >
      <span
        class="highlight__content__text"
        v-html="$highlightSearch(dataset.query.text, text)"
      />
    </span>
    <span class="highlight__label">
      <span @click="removeEntity" class="highlight__tooltip__container">
        <span
          :class="[
            'highlight__tooltip',
            annotationEnabled ? 'highlight__tooltip--icon' : '',
          ]"
        >
          <span class="highlight__tooltip__origin" v-if="span.origin">{{
            span.origin === "prediction" ? "pred." : "annot."
          }}</span>
          <span
            >{{ span.entity.label }}
            <svgicon
              v-if="annotationEnabled && span.origin === 'annotation'"
              width="8"
              height="8"
              name="cross"
            ></svgicon>
          </span>
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
  @include font-size(18px);
  line-height: 1em;
  position: relative;
  cursor: default;
  // display: inline-flex;
  border-radius: 2px;
  padding: 0;
  margin-right: -3.62px;
  &.editable {
    cursor: pointer;
  }
  ::selection {
    background: none;
  }
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
    padding-bottom: 1px;
  }
  &__tooltip {
    pointer-events: all;
    cursor: pointer;
    display: block;
    border-radius: 2px;
    padding: 5px 10px 6px 10px;
    margin-bottom: 0.5em;
    transition: opacity 0.5s ease, z-index 0.2s ease;
    white-space: nowrap;
    user-select: none;
    font-weight: 600;
    min-width: 80px;
    @include font-size(16px);
    .prediction & {
      margin-top: 0.5em;
    }
    & > span {
      display: block;
    }
    &__container {
      position: absolute;
      right: 50%;
      transform: translateX(50%);
      opacity: 0;
      z-index: -1;
      .annotation & {
        bottom: 100%;
      }
      .prediction & {
        top: calc(100% + 8px);
      }
    }
    &__origin {
      @include font-size(12px);
      font-weight: normal;
    }
    &--icon {
      padding-right: 20px;
      .svg-icon {
        position: absolute;
        top: 10px;
        right: 10px;
        cursor: pointer;
        .prediction & {
          top: 16px;
        }
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
      bottom: 2px;
    }
    .prediction & {
      @include triangle(top, 6px, 6px, auto);
      top: 3px;
    }
  }
  &:hover .highlight__tooltip__container {
    opacity: 1;
    transition-delay: 0s;
    z-index: 4;
  }
}
</style>
