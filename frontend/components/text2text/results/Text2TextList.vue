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
        !annotationEnabled
          ? 'content--exploration-mode'
          : 'content--annotation-mode',
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
        <div v-if="!sentences.length">
          <text-2-text-content-editable
            :key="refresh"
            :annotation-enabled="annotationEnabled"
            :edition-mode="true"
            :default-text="visibleSentence || ''"
            placeholder="Type your text"
            @back="back"
            @edit="edit"
            @annotate="onAnnotate"
            @change-text="onTextChanged"
          />
          <div class="content__footer">
            <div class="content__actions-buttons">
              <re-button
                v-if="visibleSentence && annotationEnabled"
                class="button-primary"
                @click="onAnnotate(visibleSentence)"
                >Validate</re-button
              >
            </div>
          </div>
        </div>

        <span
          v-for="(sentence, index) in sentences"
          v-else
          :key="sentence.text"
        >
          <div v-if="itemNumber === index" class="content__sentences">
            <div class="content__group">
              <p v-if="!editionMode" class="content__sentences__title">
                {{ sentencesOrigin }}
              </p>
              <re-button
                v-if="hasAnnotationAndPredictions && !editionMode"
                class="button-clear"
                @click="changeVisibleSentences"
                >{{
                  sentencesOrigin === "Annotation"
                    ? annotationEnabled
                      ? `View predictions (${predictionsLength})`
                      : `Back to predictions (${predictionsLength})`
                    : annotationEnabled
                    ? "Back to annotation"
                    : "View annotation"
                }}</re-button
              >
            </div>
            <text-2-text-content-editable
              :key="refresh"
              :annotation-enabled="annotationEnabled"
              :edition-mode="editionMode"
              :default-text="visibleSentence || sentence.text || ''"
              :content-editable="annotationEnabled && editionMode"
              @back="back"
              @edit="edit"
              @annotate="onAnnotate"
              @change-text="onTextChanged"
            />
            <div v-if="!editionMode" class="content__footer">
              <template v-if="sentencesOrigin === 'Prediction'">
                <div v-if="showScore" class="content__score">
                  Score: {{ sentence.score | percent }}
                </div>
                <div v-if="sentences.length" class="content__nav-buttons">
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
              </template>
              <div v-if="annotationEnabled" class="content__actions-buttons">
                <re-button
                  v-if="sentences.length"
                  :class="[
                    'edit',
                    allowValidation
                      ? 'button-primary--outline'
                      : 'button-primary',
                  ]"
                  @click="edit"
                  >Edit</re-button
                >
                <re-button
                  v-if="allowValidation"
                  class="button-primary"
                  @click="onAnnotate(visibleSentence)"
                  >Validate</re-button
                >
              </div>
            </div>
          </div>
        </span>
      </div>
    </div>
  </div>
</template>

<script>
import "assets/icons/pencil";
import { IdState } from "vue-virtual-scroller";
import { mapActions } from "vuex";

export default {
  mixins: [
    IdState({
      // You can customize this
      idProp: (vm) => `${vm.dataset.name}-${vm.record.id}`,
    }),
  ],
  props: {
    dataset: {
      type: Object,
      required: true,
    },
    record: {
      type: Object,
      required: true,
    },
    predictions: {
      type: Array,
      required: true,
    },
    annotations: {
      type: Array,
      required: true,
    },
    annotationEnabled: {
      type: Boolean,
      default: false,
    },
  },
  idState() {
    return {
      sentencesOrigin: undefined,
      itemNumber: 0,
      editionMode: false,
      refresh: 1,
    };
  },
  computed: {
    sentencesOrigin: {
      get: function () {
        return this.idState.sentencesOrigin;
      },
      set: function (newValue) {
        this.idState.sentencesOrigin = newValue;
      },
    },
    itemNumber: {
      get: function () {
        return this.idState.itemNumber;
      },
      set: function (newValue) {
        this.idState.itemNumber = newValue;
      },
    },
    visibleSentence: {
      get: function () {
        return this.record.lastEditedSentence;
      },
      set: async function (newValue) {
        if (this.record.lastEditedSentence !== newValue) {
          // this.record.lastEditedSentence = newValue;
          await this.updateRecords({
            dataset: this.dataset,
            records: [
              {
                ...this.record,
                lastEditedSentence: newValue,
              },
            ],
          });
        }
      },
    },
    editionMode: {
      get: function () {
        return this.idState.editionMode;
      },
      set: function (newValue) {
        this.idState.editionMode = newValue;
      },
    },
    refresh: {
      get: function () {
        return this.idState.refresh;
      },
      set: function (newValue) {
        this.idState.refresh = newValue;
      },
    },
    selectedSentence() {
      return (
        this.sentences[this.itemNumber] && this.sentences[this.itemNumber].text
      );
    },
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
    },
    allowValidation() {
      return (
        this.sentencesOrigin === "Prediction" ||
        this.record.status === "Discarded"
      );
    },
    selected() {
      return this.record.selected;
    },
  },
  watch: {
    selected(newValue, oldValue) {
      if (newValue === false && oldValue === true) {
        this.refresh++;
        this.sentencesOrigin = "Annotation";
        this.editionMode = false;
        this.itemNumber = 0;
        this.$emit("update-initial-record");
      }
    },
    annotationEnabled(newValue, oldValue) {
      if (newValue !== oldValue) {
        this.refresh++;
        this.initializeSentenceOrigin();
        this.back();
        this.itemNumber = 0;
      }
    },
  },
  updated() {
    if (this.sentencesOrigin === undefined) {
      this.initializeSentenceOrigin();
    }
  },
  mounted() {
    if (this.sentencesOrigin === undefined) {
      this.initializeSentenceOrigin();
    }
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateDatasetRecords",
    }),
    async showitemNumber(index) {
      this.itemNumber = index;
      await (this.visibleSentence = this.selectedSentence);
    },
    async onTextChanged(newText) {
      let status = "Edited";

      if (this.selectedSentence === newText) {
        status = "Default";
      }

      await (this.visibleSentence = newText);
      await this.updateRecords({
        dataset: this.dataset,
        records: [
          {
            ...this.record,
            selected: true,
            status,
            lastEditedSentence: newText,
          },
        ],
      });
    },
    edit() {
      if (this.annotationEnabled) {
        this.editionMode = true;
      }
    },
    async back() {
      this.editionMode = false;
      this.refresh++;
      await (this.visibleSentence = this.selectedSentence);
      this.$emit("reset-initial-record");
    },
    async changeVisibleSentences() {
      this.sentencesOrigin !== "Annotation"
        ? (this.sentencesOrigin = "Annotation")
        : (this.sentencesOrigin = "Prediction");
      this.itemNumber = 0;
      this.editionMode = false;
      await (this.visibleSentence = this.selectedSentence);
    },
    initializeSentenceOrigin() {
      if (this.annotationEnabled) {
        if (this.annotations.length) {
          this.sentencesOrigin = "Annotation";
        } else if (this.predictions.length) {
          this.sentencesOrigin = "Prediction";
        }
      } else {
        if (this.predictions.length) {
          this.sentencesOrigin = "Prediction";
        } else if (this.annotations.length) {
          this.sentencesOrigin = "Annotation";
        }
      }
    },
    async onAnnotate(sentence) {
      let newS = {
        score: 1,
        text: sentence,
      };
      this.$emit("annotate", { sentences: [newS] });
      this.itemNumber = 0;
      this.editionMode = false;
      this.sentencesOrigin = "Annotation";
      // await (this.visibleSentence = this.selectedSentence);
    },
  },
};
</script>

<style lang="scss" scoped>
.content {
  position: relative;
  display: flex;
  margin-top: 1em;
  &--exploration-mode {
    align-items: flex-end;
  }
  &--separator {
    padding-top: 1em;
    &:before {
      content: "";
      border-top: 1px solid palette(grey, light);
      width: calc(100% - 200px);
      position: absolute;
      top: 0;
    }
  }
  &--editable {
    width: 100%;
    ::v-deep p {
      padding: 0.6em;
      margin: 0;
      outline: none;
    }
    ::v-deep .re-button {
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
      @include font-size(13px);
      color: palette(grey, medium);
      margin: 0;
    }
  }
  &__score {
    @include font-size(13px);
    margin-right: 0;
    min-width: 33%;
    color: palette(grey, medium);
  }
  &__footer {
    padding-top: 2em;
    margin-top: auto;
    margin-bottom: 0;
    display: flex;
    align-items: center;
  }
  &__group {
    width: calc(100% - 200px);
    display: flex;
    align-items: center;
    margin-bottom: 0.5em;
    .button-clear {
      @include font-size(13px);
      margin: auto 0 auto auto;
      color: palette(grey, dark);
      transition: opacity 0.3s ease-in-out 0.2s;
      &:hover {
        color: darken(palette(grey, dark), 10%);
      }
    }
  }
  &__actions-buttons {
    margin-right: 0;
    margin-left: auto;
    display: flex;
    .edit {
      opacity: 0;
      pointer-events: none;
    }
    .re-button {
      min-height: 32px;
      line-height: 32px;
      display: block;
      margin-bottom: 0;
      margin-right: 0;
      margin-left: auto;
      & + .re-button {
        margin-left: 6px;
      }
    }
  }
  &__nav-buttons {
    @include font-size(13px);
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 33%;
    margin-right: auto;
    margin-left: 0;
    color: palette(grey, medium);
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
        background: palette(grey, bg);
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
