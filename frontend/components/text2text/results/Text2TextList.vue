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
  <div
    :class="[
      editable ? 'content--editable' : null,
      showScore ? 'content--has-score' : null,
      'content',
    ]"
  >
    <span v-for="(sentence, index) in list" :key="index">
      <div v-if="itemNumber === index">
        <p class="content__text" :contenteditable="editable" @input="input">
          {{ sentence.text }}
        </p>
        <div v-if="showScore" class="content__score">
          <re-numeric
            :value="decorateScore(sentence.score)"
            type="%"
            :decimals="2"
          ></re-numeric>
        </div>
      </div>
    </span>
    <div v-if="!list.length">
      <p class="content__text" :contenteditable="editable" @input="input"></p>
    </div>
    <div v-if="list.length > 1" class="content__buttons">
      <a
        :class="itemNumber <= 0 ? 'disabled' : null"
        href="#"
        @click.prevent="showitemNumber(--itemNumber)"
      >
        <svgicon name="chev-left" width="15" height="15" color="#4A4A4A" />
      </a>
      <a
        :class="list.length <= itemNumber + 1 ? 'disabled' : null"
        href="#"
        @click.prevent="showitemNumber(++itemNumber)"
      >
        <svgicon name="chev-right" width="15" height="15" color="#4A4A4A" />
      </a>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    list: {
      type: Array,
      required: true,
    },
    editable: {
      type: Boolean,
      default: false,
    },
    showScore: {
      type: Boolean,
      default: false,
    },
  },
  data: () => {
    return {
      itemNumber: 0,
    };
  },
  methods: {
    showitemNumber(index) {
      this.itemNumber = index;
    },
    input(e) {
      this.$emit("input", e.target.innerText);
    },
    decorateScore(score) {
      return score * 100;
    },
  },
};
</script>

<style lang="scss" scoped>
.content {
  position: relative;
  border: 1px solid $primary-color;
  margin-bottom: 1em;
  &--editable {
    margin-top: 1em;
    font-family: monospace;
  }
  &--has-score {
    .content__text {
      padding-right: 4em;
    }
  }
  &__score {
    position: absolute;
    top: 1em;
    right: 1em;
    border-radius: 3px;
    @include font-size(12px);
    padding: 0 0.3em;
    border: 1px solid palette(grey, smooth);
  }
  &__buttons {
    margin: 1em;
    text-align: right;
    a {
      height: 20px;
      width: 20px;
      border-radius: 50%;
      color: white;
      line-height: 20px;
      text-align: center;
      margin-left: 0.5em;
      display: inline-block;
      text-decoration: none;
      @include font-size(13px);
      &.disabled {
        opacity: 0.2;
        pointer-events: none;
      }
    }
  }
  p {
    padding: 1em;
    margin: 0;
    outline: none;
  }
}
</style>
