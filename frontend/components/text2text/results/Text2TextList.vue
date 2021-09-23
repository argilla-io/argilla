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
  <div v-click-outside="clickOutside">
    <div
      :class="[
        'content',
        hasAnnotationAndPredictions ? 'content--separator' : null,
        !editable ? 'content--exploration-mode' : 'content--annotation-mode',
      ]"
    >
      <div
        :class="[
          editionMode || !list.length
            ? 'content--editable'
            : 'content--non-editable',
          showScore ? 'content--has-score' : null,
        ]"
      >
        <span v-for="(sentence, index) in list" :key="sentence.text">
          <div class="content__sentences" v-if="itemNumber === index">
            <div class="content__edition-area">
              <p
                id="text"
                ref="text"
                class="content__text"
                :contenteditable="editable && editionMode"
                placeholder="Type your text"
                @input="input"
              >
                {{ sentence.text }}
              </p>
              <span v-if="editionMode"
                ><strong>shift Enter</strong> to validate</span
              >
            </div>
            <div class="content__footer">
              <div v-if="showScore" class="content__score">
                Score:
                <re-numeric
                  :value="decorateScore(sentence.score)"
                  type="%"
                  :decimals="2"
                ></re-numeric>
              </div>
              <div v-if="list.length > 1" class="content__nav-buttons">
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
                {{ itemNumber + 1 }} of {{ list.length }} predictions
                <a
                  :class="list.length <= itemNumber + 1 ? 'disabled' : null"
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
            </div>
          </div>
        </span>

        <div v-if="!list.length">
          <p
            class="content__text"
            :contenteditable="editable"
            placeholder="Type your text"
            @input="input"
          ></p>
        </div>
      </div>
      <div class="content__buttons">
        <re-button
          v-if="newSentence && editable"
          :class="[
            'button-primary',
            status === 'Validated' && !editionMode ? 'active' : null,
          ]"
          @click="annotate"
          >{{ status === "Validated" && !editionMode ? "Validated" : "Validate" }}</re-button
        >
        <re-button
          v-if="!editionMode && editable && newSentence && list.length"
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
          v-if="hasAnnotationAndPredictions && !editionMode"
          class="button-clear"
          @click="getSentences()"
          >{{
            sentencesOrigin === "Annotation"
              ? `View predictions (${predictionsLength})`
              : "View annotation"
          }}</re-button
        >
      </div>
    </div>
  </div>
</template>

<script>
import "assets/icons/pencil";
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
    hasAnnotationAndPredictions: {
      type: Boolean,
      default: true,
    },
    predictionsLength: {
      type: Number,
    },
    sentencesOrigin: {
      type: String,
    },
    status: {
      type: String,
    },
  },
  data: () => {
    return {
      itemNumber: 0,
      newSentence: undefined,
      editionMode: false,
      shiftPressed: false,
      shiftKey: undefined,
    };
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
      this.editionMode = true;
    },
    focus() {
      this.$nextTick(() => {
        if (this.$refs.text && this.$refs.text[0]) {
          this.$refs.text[0].focus();
        }
      });
    },
    back() {
      this.itemNumber = 0;
      this.editionMode = false;
    },
    getSentences() {
      this.itemNumber = 0;
      this.editionMode = false;
      this.$emit("get-sentences");
    },
    decorateScore(score) {
      return score * 100;
    },
    annotate() {
      this.itemNumber = 0;
      this.editionMode = false;
      if (this.newSentence) {
        let newS = {
          score: 1,
          text: this.newSentence,
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
      this.editionMode = false;
    },
  },
};
</script>

<style lang="scss" scoped>
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
  margin-bottom: 1em;
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
  }
  &__text {
    color: black;
  }
  &__edition-area {
    position: relative;
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
    span {
      font-weight: 600;
      margin-left: 1em;
      @include font-size(14px);
    }
  }
  &__footer {
    padding-top: 2em;
    margin-top: auto;
    margin-bottom: 0;
    display: flex;
    align-items: center;
  }
  &__buttons {
    min-width: 120px;
    margin-left: 2em;
    text-align: right;
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
      }
      &.button-clear {
        color: $font-secondary;
        min-height: 2em;
        line-height: 2em;
        opacity: 0;
        transition: opacity 0.3s ease-in-out 0.2s;
      }
      & + .re-button {
        margin-top: 1em;
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
      line-height: 20px;
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
        opacity: 0.2;
        pointer-events: none;
      }
    }
  }
}
.button {
  display: block;
}
</style>
