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
      :class="[
        'content',
        hasAnnotationAndPredictions ? 'content--separator' : null,
        !editable ? 'content--exploration-mode' : 'content--annotation-mode',
      ]"
    >
      <div
        :class="[
          editionMode || !sentences.length
            ? 'content--editable'
            : 'content--non-editable',
          showScore ? 'content--has-score' : null,
        ]"
      >
        <span v-for="(sentence, index) in sentences" :key="sentence.text">
          <div v-if="itemNumber === index" class="content__sentences">
            <p v-if="!editionMode" class="content__sentences__title">{{sentencesOrigin}}</p>
            <div class="content__edition-area">
              <p
                :key="refresh"
                ref="text"
                class="content__text"
                :contenteditable="editable && editionMode"
                placeholder="Type your text"
                @input="input"
                v-html="sentence.text"
                @click="edit()"
              ></p>
              <span v-if="editionMode"
                ><strong>shift Enter</strong> to validate</span
              >
            </div>
            <div class="content__buttons">
              <re-button
                v-if="hasAnnotationAndPredictions && !editionMode"
                class="button-clear"
                @click="changeVisibleSentences"
                >{{
                  sentencesOrigin === "Annotation"
                    ? editable ? `View predictions (${predictionsLength})` : `Back to predictions (${predictionsLength})`
                    : editable ? "Back to annotation" : "View annotation"
                }}</re-button
              >
            </div>
            <div class="content__footer">
              <div v-if="showScore" class="content__score">
                Score:<span>{{ sentence.score | percent }}</span>
              </div>
              <div v-if="sentences.length && sentencesOrigin === 'Prediction'" class="content__nav-buttons">
                <a
                  :class="itemNumber <= 0 ? 'disabled' : null"
                  href="#"
                  @click.prevent="showitemNumber(--itemNumber)"
                >
                  <svgicon
                    name="chev-left"
                    width="8"
                    height="8"
                    color="#4C4EA3"
                  />
                </a>
                {{ itemNumber + 1 }} of {{ sentences.length }} predictions
                <a
                  :class="
                    sentences.length <= itemNumber + 1 ? 'disabled' : null
                  "
                  href="#"
                  @click.prevent="showitemNumber(++itemNumber)"
                >
                  <svgicon
                    name="chev-right"
                    width="8"
                    height="8"
                    color="#4C4EA3"
                  />
                </a>
              </div>
              <div class="content__actions-buttons">
                <re-button
                  v-if="!editionMode && editable && newSentence && sentences.length"
                  class="button-primary--outline"
                  @click="edit()"
                  >Edit</re-button
                >
                <re-button
                  v-if="editionMode && editable && newSentence"
                  class="button-primary--outline"
                  @click="back()"
                  >Back</re-button
                >
                <re-button
                  v-if="newSentence && editable"
                  :class="[
                    'button-primary',
                    status === 'Validated' && sentencesOrigin === 'Annotation' && !editionMode ? 'active' : null,
                  ]"
                  @click="annotate"
                  >{{
                    status === "Validated" && sentencesOrigin === 'Annotation' && !editionMode ? "Validated" : "Validate"
                  }}</re-button
                >
              </div>
            </div>
          </div>
        </span>

        <div v-if="!sentences.length">
          <p
            class="content__text content__text--no-sentences"
            :contenteditable="editable"
            placeholder="Type your text"
            @input="input"
          ></p>
            <div class="content__footer">
              <div class="content__actions-buttons">
                <re-button
                  v-if="newSentence && editable"
                  :class="[
                    'button-primary',
                    status === 'Validated' && sentencesOrigin === 'Annotation' && !editionMode ? 'active' : null,
                  ]"
                  @click="annotate"
                  >{{
                    status === "Validated" && sentencesOrigin === 'Annotation' && !editionMode ? "Validated" : "Validate"
                  }}</re-button
                >
              </div>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import "assets/icons/pencil";
export default {
  props: {
    predictions: {
      type: Array,
      required: true
    },
    annotations: {
      type: Array,
      required: true
    },
    sentencesOrigin: {
      type: String,
      default: undefined
    },
    status: {
      type: String,
      required: true
    },
    editable: {
      type: Boolean,
      default: false
    }
  },
  data: () => {
    return {
      itemNumber: 0,
      newSentence: undefined,
      editionMode: false,
      shiftPressed: false,
      shiftKey: undefined,
      refresh: 1
    };
  },
  computed: {
    predictionsLength() {
      return this.predictions.length;
    },
    showScore() {
      return this.sentencesOrigin === "Prediction";
    },
    sentences() {
      if (this.sentencesOrigin === "Annotation") {
        return this.annotations;
      }
      if (this.sentencesOrigin === "Prediction") {
        return this.predictions;
      }
      return [];
    },
    hasAnnotationAndPredictions() {
      return this.predictions.length && this.annotations.length;
    }
  },
  mounted() {
    this.getText();
  },
  updated() {
    this.getText();
    this.focus();
  },
  created() {
    window.addEventListener("keydown", this.keyDown);
    window.addEventListener("keyup", this.keyUp);
  },
  destroyed() {
    window.removeEventListener("keydown", this.keyDown);
    window.addEventListener("keyup", this.keyUp);
  },
  methods: {
    getText() {
      if (this.$refs.text && this.$refs.text[0]) {
        this.newSentence = this.$refs.text[0].innerText;
      }
    },
    showitemNumber(index) {
      this.itemNumber = index;
    },
    input(e) {
      this.newSentence = e.target.innerText;
    },
    edit() {
      if (this.editable) {
        this.editionMode = true;
        this.$emit("edition-mode", this.editionMode);
      }
    },
    focus() {
      this.$nextTick(() => {
        if (this.$refs.text && this.$refs.text[0]) {
          this.$refs.text[0].focus();
        }
      });
    },
    back() {
      this.editionMode = false;
      this.$emit("edition-mode", this.editionMode);
      this.refresh++;
    },
    changeVisibleSentences() {
      this.itemNumber = 0;
      this.editionMode = false;
      this.$emit("edition-mode", this.editionMode);
      this.$emit("change-visible-sentences");
    },
    annotate() {
      this.itemNumber = 0;
      this.editionMode = false;
      this.$emit("edition-mode", this.editionMode);
      if (this.newSentence) {
        let newS = {
          score: 1,
          text: this.newSentence
        };
        this.$emit("annotate", { sentences: [newS] });
      }
    },
    keyUp(event) {
      if (this.shiftKey === event.key) {
        this.shiftPressed = false;
      }
    },
    keyDown(event) {
      if (event.shiftKey) {
        this.shiftKey = event.key;
        this.shiftPressed = true;
      }
      const enter = event.key === "Enter";
      if (this.shiftPressed && this.editionMode && enter) {
        this.annotate();
      }
    },
    clickOutside() {
      this.itemNumber = 0;
      this.editionMode = false;
    }
  }
};
</script>

<style lang="scss" scoped>
$marginRight: 200px;
[contenteditable="true"] {
  box-shadow: 0 1px 4px 1px rgba(222, 222, 222, 0.5);
  border-radius: 3px 3px 3px 3px;
  &:focus + span {
    display: block;
  }
}
[contenteditable="true"]:empty:before {
  color: palette(grey, verylight);
  content: attr(placeholder);
  pointer-events: none;
  display: block; /* For Firefox */
}
.content {
  position: relative;
  display: flex;
  margin-top: 1em;
  &--exploration-mode {
    align-items: flex-end;
  }
  &--separator {
    border-top: 1px solid palette(grey, light);
    padding-top: 1em;
  }
  &--editable {
    width: 100%;
    p {
      padding: 0.6em;
      margin: 0;
      outline: none;
    }
    .re-button {
      opacity: 1 !important;
    }
  }
  &--non-editable {
    width: 100%;
    p {
      margin: 0;
      outline: none;
    }
  }
  &--has-score {
    .content__text {
      padding-right: 4em;
    }
  }
  &__sentences {
    height: 100%;
    display: flex;
    flex-direction: column;
    min-height: 140px;
    &__title {
      color: palette(grey, verylight);
      @include font-size(12px);
      font-weight: 600;
      margin: 0;
    }
  }
  &__text {
    color: black;
    white-space: pre-wrap;
    display: inline-block;
    width: 100%;
    &--no-sentences {
      max-width: calc(100% - #{$marginRight});
    }
  }
  &__edition-area {
    position: relative;
    margin-right: $marginRight;
    span {
      position: absolute;
      top: 100%;
      right: 0;
      @include font-size(12px);
      color: palette(grey, verylight);
      margin-top: 0.5em;
      display: none;
    }
  }
  &__score {
    @include font-size(12px);
    padding: 0 0.3em;
    margin-right: auto;
    min-width: 20%;
    span {
      font-weight: 600;
      margin-left: 1em;
      @include font-size(14px);
    }
  }
  &__footer {
    padding-top: 3em;
    margin-top: auto;
    margin-bottom: 0;
    display: flex;
    align-items: center;
  }
  &__buttons {
    position: absolute;
    top: 1em;
    right: 0;
    .button-clear {
      color: $font-secondary;
      min-height: 2em;
      line-height: 2em;
      opacity: 0;
      transition: opacity 0.3s ease-in-out 0.2s;
      &:hover {
        color: darken($font-secondary, 10%);
      }
    }
  }
  &__actions-buttons {
    margin-right: 0;
    margin-left: auto;
    display: flex;
    min-width: 20%;
    .re-button {
      min-height: 38px;
      line-height: 38px;
      display: block;
      margin-bottom: 0;
      margin-right: 0;
      margin-left: auto;
      &.active {
        background: $font-secondary;
        pointer-events: none;
        cursor: pointer;
      }
      &.button-primary--outline {
        min-height: 36px;
        line-height: 36px;
        color: $font-secondary;
        border-color: $font-secondary;
        opacity: 0;
        transition: opacity 0.3s ease-in-out 0.2s;
        min-width: auto;
      }
      &.button-primary:not(.active) {
        opacity: 0;
        transition: opacity 0.3s ease-in-out 0.2s;
      }
      & + .re-button {
        margin-left: 1em;
      }
    }
  }
  &__nav-buttons {
    @include font-size(12px);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: auto;
    margin-left: auto;
    a {
      height: 20px;
      width: 20px;
      line-height: 19px;
      text-align: center;
      border-radius: 3px;
      text-align: center;
      margin-left: 1.5em;
      margin-right: 1.5em;
      display: inline-block;
      text-decoration: none;
      outline: none;
      @include font-size(13px);
      background: transparent;
      transition: all 0.2s ease-in-out;
      &:hover {
        background: palette(grey, smooth);
        transition: all 0.2s ease-in-out;
      }
      &.disabled {
        opacity: 0;
        pointer-events: none;
      }
    }
  }
}
.button {
  display: block;
}
</style>
