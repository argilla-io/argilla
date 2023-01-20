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
    @mouseenter="showTooltip = true"
    @mouseleave="showTooltip = false"
    :class="['highlight', span.origin, annotationEnabled ? 'editable' : null]"
    ><span
      v-for="(token, i) in span.tokens"
      :key="i"
      class="highlight__content"
      @click="openTagSelector"
      @dblclick="removeEntity"
      v-html="visualizeToken(token, i)"
    ></span
    ><span class="whitespace">{{ charsBetweenTokens }}</span>
    <svgicon
      class="remove-button"
      @click="removeEntity"
      v-if="annotationEnabled && span.origin === 'annotation'"
      width="11"
      height="11"
      name="close"
    ></svgicon>
    <lazy-text-span-tooltip v-if="showTooltip" :span="span" />
  </span>
</template>

<script>
import "assets/icons/close";
import { getViewSettingsByDatasetName } from "@/models/viewSettings.queries";

export default {
  props: {
    span: {
      type: Object,
      required: true,
    },
    whiteSpace: {
      type: String,
    },
    datasetName: {
      type: String,
      required: true,
    },
    record: {
      type: Object,
      required: true,
    },
  },
  data: () => {
    return {
      singleClickDelay: 300,
      doubleClicked: false,
      clicked: false,
      showTooltip: false,
    };
  },
  computed: {
    viewSettings() {
      return this.datasetName
        ? getViewSettingsByDatasetName(this.datasetName)
        : {};
    },
    annotationEnabled() {
      return this.viewSettings.viewMode === "annotate";
    },
    charsBetweenTokens() {
      return this.span.tokens[this.span.tokens.length - 1].charsBetweenTokens;
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
    visualizeToken(token, i) {
      let text = token.highlighted
        ? this.$htmlHighlightText(token.text)
        : this.$htmlText(token.text);
      return `${text}${
        token.charsBetweenTokens && i + 1 !== this.span.tokens.length
          ? token.charsBetweenTokens
          : ""
      }`;
    },
  },
};
</script>

<style lang="scss" scoped>
:deep(.whitespace) {
  background: palette(white);
  padding-bottom: 3px;
  border-bottom: 5px solid palette(white);
  @include font-size(16px);
  white-space: pre-line;
  display: inline;
}

.highlight {
  font-size: 0;
  line-height: 1em;
  position: relative;
  cursor: default; // display: inline-flex;
  border-radius: 2px;
  padding: 0;
  &.editable {
    cursor: pointer;
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
  &__content {
    @include font-size(16px);
    white-space: pre-line;
    display: inline;
    padding-bottom: 1px;
  }
  &:hover .remove-button {
    opacity: 1;
    z-index: 5;
  }
}

.remove-button {
  opacity: 0;
  z-index: -1;
  position: absolute;
  top: -23px;
  right: -3px;
  border-radius: 2px;
  min-width: 10px;
  background: $black-87;
  fill: palette(white);
  padding: 2px;
}
</style>
