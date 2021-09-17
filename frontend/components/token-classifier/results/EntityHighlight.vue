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
  <span :class="['highlight', isText ? '' : 'highlight--block']">
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
          >{{ span.entity.label }}
          <svgicon
            v-if="annotationEnabled"
            width="12"
            height="12"
            name="cross"
            @click="removeEntity"
          ></svgicon>
        </span>
      </span>
      <span v-if="span.agent" class="highlight__metadata">
        <strong>agent:</strong> {{ span.agent }}
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
      return this.dataset.viewSettings.annotationEnabled;
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
  display: inline;
  border-radius: 2px;
  padding: 0;
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
  .highlight__content {
    display: inline;
  }
  .highlight__metadata {
    background: white;
    display: block;
    position: absolute;
    border-radius: 2px;
    padding: 4px 9px 5px 9px;
    opacity: 0;
    z-index: -1;
    top: 100%;
    margin-top: 0.5em;
    transition: opacity 0.5s ease, z-index 0.2s ease;
    white-space: nowrap;
    user-select: none;
    cursor: default;
    font-weight: 500;
    box-shadow: $shadow-100;
    text-align: left;
    @include font-size(12px);
    right: 50%;
    transform: translateX(50%);
  }
  .highlight__tooltip {
    display: block;
    position: absolute;
    border-radius: 2px;
    padding: 4px 9px 5px 9px;
    opacity: 0;
    z-index: -1;
    bottom: 100%;
    margin-bottom: 0.5em;
    transition: opacity 0.5s ease, z-index 0.2s ease;
    white-space: nowrap;
    user-select: none;
    cursor: default;
    font-weight: 500;
    right: 50%;
    transform: translateX(50%);
    @include font-size(12px);
    &--icon {
      padding-right: 20px;
      .svg-icon {
        display: inline-block;
        margin-left: 1em;
        cursor: pointer;
      }
    }
  }
  .highlight__tooltip:after {
    margin: auto;
    transform: translateY(10px);
    @include triangle(bottom, 6px, 6px, auto);
    position: absolute;
    bottom: 5px;
    right: 0;
    left: 0;
  }
  &:hover .highlight__metadata {
    opacity: 1;
    transition-delay: 0s;
    z-index: 4;
  }
  &:hover .highlight__tooltip {
    opacity: 1;
    transition-delay: 0s;
    z-index: 4;
  }
}
</style>
