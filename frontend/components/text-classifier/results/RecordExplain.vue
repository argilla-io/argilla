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
  <div>
    <div
      v-for="tokenItem in explainFormatted"
      :key="tokenItem.index"
      :class="['atom', customClass(tokenItem)]"
    >
      <span v-if="tokenItem.grad" class="atom__tooltip">{{
        tokenItem.grad
      }}</span>
      <span v-html="tokenItem.text === ' ' ? '&nbsp;' : tokenItem.text"></span>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    queryText: {
      type: String,
      default: undefined,
    },
    explain: {
      type: Array,
    },
    predicted: {
      type: String,
      default: undefined,
    },
  },
  computed: {
    explainFormatted() {
      // TODO ALLOW FOR MULTI LABEL
      return this.explain.map((token) => {
        const grad = Number(Object.values(token.attributions)).toFixed(3);
        let percent = Math.round(Math.abs(grad) * 100);
        if (percent !== 0) {
          /* eslint-disable no-mixed-operators */
          const p = 1.5; // color sensitivity (values from 1 to 4)
          const s = 100 / Math.log10(100) ** p;
          percent = Math.round(Math.log10(percent) ** p * s);
        }
        return {
          text: this.queryText
            ? this.$highlightSearch(this.queryText, token.token)
            : token.token,
          percent: percent.toString(),
          grad,
        };
      });
    },
  },
  methods: {
    customClass(tokenItem) {
      if (this.predicted !== undefined) {
        if (Math.sign(tokenItem.grad) !== 1) {
          return `grad-neg-${tokenItem.percent}`;
        } else {
          return this.predicted === "ko"
            ? `grad-rest-${tokenItem.percent}`
            : `grad-plus-${tokenItem.percent}`;
        }
      } else {
        return Math.sign(tokenItem.grad) !== 1
          ? `grad-rest-${tokenItem.percent}`
          : `grad-plus-${tokenItem.percent}`;
      }
    },
  },
};
</script>

<style lang="scss">
.highlight-text {
  display: inline-block;
  background: #ffbf00;
  line-height: 16px;
}
</style>
<style lang="scss" scoped>
%grad {
  .atom__tooltip {
    &:after {
      margin: auto;
      transform: translateY(10px);
      position: absolute;
      bottom: 5px;
      right: 0;
      left: 0;
    }
  }
}
@for $i from 0 through 100 {
  .grad-#{$i} {
    $bg: hsla(40, 100%, 100 - $i * 0.5, 1);
    @extend %grad;
    background: $bg;
    .atom__tooltip {
      background: $bg;
      &:after {
        @include triangle(bottom, 6px, 6px, $bg);
      }
    }
  }
  .grad-neg-#{$i} {
    $bg: hsla(200, 60%, 100 - $i * 0.5, 1);
    @extend %grad;
    background: $bg;
    .atom__tooltip {
      background: $bg;
      &:after {
        @include triangle(bottom, 6px, 6px, $bg);
      }
    }
  }
  .grad-plus-#{$i} {
    $bg: hsla(100, 60%, 100 - $i * 0.5, 1);
    @extend %grad;
    background: $bg;
    .atom__tooltip {
      background: $bg;
      &:after {
        @include triangle(bottom, 6px, 6px, $bg);
      }
    }
  }
  .grad-rest-#{$i} {
    $bg: hsla(0, 80%, 100 - $i * 0.5, 1);
    @extend %grad;
    background: $bg;
    .atom__tooltip {
      background: $bg;
      &:after {
        @include triangle(bottom, 6px, 6px, $bg);
      }
    }
  }
}

.atom {
  position: relative;
  display: inline-block;
  margin: 0;
  line-height: 1.2em;
  border-radius: 2px;
  word-break: break-all;
  margin-right: 3px;
  &:first-of-type {
    margin-left: 0;
  }
  &:hover {
    .atom__tooltip {
      z-index: 1;
      opacity: 1;
      height: auto;
      width: auto;
      visibility: visible;
      transition: opacity 0.2s ease 0.2s;
      overflow: visible;
    }
  }
  &__tooltip {
    position: absolute;
    padding: 0.5em;
    bottom: calc(100% + 8px);
    right: 50%;
    transform: translateX(50%);
    opacity: 0;
    height: 0;
    width: 0;
    visibility: hidden;
    overflow: hidden;
    pointer-events: none;
    font-weight: lighter;
    border-radius: 3px;
    word-break: normal;
  }
  ::v-deep .highlight-text {
    line-height: 16px;
  }
}
.white-space {
  padding: 0.5em 0.13em;
}
.word {
  margin: 0 0.13em 0 0.12em;
}
</style>
