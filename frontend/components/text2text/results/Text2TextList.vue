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
    class="content content--separator"
    :class="
      !annotationEnabled ? 'content--exploration-mode' : 'content--selectable'
    "
  >
    <div>
      <div class="--editable" v-if="!sentences.length">
        <text-2-text-content-editable
          :key="refresh"
          :annotation-enabled="annotationEnabled"
          :edition-mode="true"
          :default-text="visibleSentence || ''"
          placeholder="Type your text"
          @annotate="onValidate()"
          @change-text="onTextChanged"
        />
      </div>
      <span v-for="(sentence, index) in sentences" v-else :key="index">
        <div v-if="predictionNumber === index" class="content__sentences">
          <div class="content__tabs">
            <base-button
              v-if="isPreannotated"
              :class="sentencesOrigin === 'Preannotation' ? '--active' : null"
              @click="changeVisibleSentences('Preannotation')"
              >PreAnnotation</base-button
            >
            <base-button
              v-if="annotations.length"
              :class="sentencesOrigin === 'Annotation' ? '--active' : null"
              @click="changeVisibleSentences('Annotation')"
              >Annotation</base-button
            >
            <base-button
              v-if="predictions.length"
              :class="sentencesOrigin === 'Prediction' ? '--active' : null"
              @click="changeVisibleSentences('Prediction')"
              >{{ `Predictions (${predictionsLength})` }}</base-button
            >
          </div>
          <div :class="sentencesOrigin !== 'Prediction' ? '--editable' : null">
            <div
              class="content__prediction-tabs"
              v-if="sentencesOrigin !== 'Annotation'"
            >
              <base-button
                @click="showPredictionNumber(index)"
                :class="predictionNumber === index ? '--active' : null"
                v-for="(sentence, index) in sentences"
                :key="index"
                >Prediction {{ index + 1 }} :
                {{ sentence.score | percent }}</base-button
              >
            </div>
            <text-2-text-content-editable
              v-if="sentencesOrigin !== 'Prediction'"
              :key="refresh"
              :annotation-enabled="annotationEnabled"
              :default-text="visibleSentence || sentence.text || ''"
              :content-editable="annotationEnabled"
              @annotate="onValidate()"
              @change-text="onTextChanged"
            />
            <p class="sentence--non-editable" v-else>
              {{ visibleSentence || sentence.text || "" }}
            </p>
          </div>
        </div>
      </span>
      <record-action-buttons
        v-if="annotationEnabled && sentencesOrigin !== 'Prediction'"
        :actions="text2textClassifierActionButtons"
        @validate="onValidate()"
        @clear="onClearAnnotations()"
        @reset="onReset()"
        @discard="onDiscard()"
      />
    </div>
  </div>
</template>

<script>
import { IdState } from "vue-virtual-scroller";
import { mapActions } from "vuex";
import { getText2TextDatasetById } from "@/models/text2text.queries";

export default {
  mixins: [
    IdState({
      // You can customize this
      idProp: (vm) => `${vm.datasetName}-${vm.record.id}`,
    }),
  ],
  props: {
    datasetId: {
      type: Array,
      required: true,
    },
    datasetName: {
      type: String,
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
      predictionNumber: 0,
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
    predictionNumber: {
      get: function () {
        return this.idState.predictionNumber;
      },
      set: function (newValue) {
        this.idState.predictionNumber = newValue;
      },
    },
    visibleSentence: {
      get: function () {
        return this.record.lastEditedSentence;
      },
      set: async function (newValue) {
        if (this.record.lastEditedSentence !== newValue) {
          await this.updateRecords({
            dataset: this.getText2TextDataset(),
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
        this.sentences[this.predictionNumber] &&
        this.sentences[this.predictionNumber].text
      );
    },
    isPreannotated() {
      return (this.predictionsLength && !this.annotations.length) || false;
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
      if (this.sentencesOrigin === "Preannotation") {
        return this.predictions;
      }
      return [];
    },
    allowValidation() {
      return (
        this.sentencesOrigin === "Prediction" ||
        (this.record.status !== "Validated" &&
          !!this.record?.sentenceForAnnotation)
      );
    },
    text2textClassifierActionButtons() {
      return [
        {
          id: "validate",
          name: "Validate",
          allow: this.sentencesOrigin !== "Prediction",
          active: this.allowValidation,
        },
        {
          id: "discard",
          name: "Discard",
          allow: this.sentencesOrigin !== "Prediction",
          active: this.record.status !== "Discarded",
        },
        // {
        //   id: "clear",
        //   name: "Clear",
        //   allow: this.sentencesOrigin !== "Prediction",
        //   active: this.record.annotation || false,
        // },
        {
          id: "reset",
          name: "Reset",
          allow: this.sentencesOrigin !== "Prediction",
          active: this.record.status === "Edited",
        },
      ];
    },
  },
  watch: {
    annotationEnabled(newValue, oldValue) {
      if (newValue !== oldValue) {
        this.refresh++;
        this.initializeSentenceOrigin();
        this.predictionNumber = 0;
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
    async showPredictionNumber(index) {
      this.predictionNumber = index;
      await (this.visibleSentence = this.selectedSentence);
    },
    async onTextChanged(newText) {
      let status = "Edited";

      if (this.selectedSentence === newText) {
        status = "Default";
      }

      await (this.visibleSentence = newText);
      await this.updateRecords({
        dataset: this.getText2TextDataset(),
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
    async changeVisibleSentences(tab) {
      this.refresh++;
      this.sentencesOrigin = tab;
      this.predictionNumber = 0;
      await (this.visibleSentence = this.selectedSentence);
    },
    initializeSentenceOrigin() {
      if (this.annotationEnabled) {
        if (this.annotations.length) {
          this.sentencesOrigin = "Annotation";
        } else if (this.predictions.length) {
          this.sentencesOrigin = "Preannotation";
        }
      } else {
        if (this.predictions.length) {
          this.sentencesOrigin = "Prediction";
        } else if (this.annotations.length) {
          this.sentencesOrigin = "Annotation";
        }
      }
    },
    async onValidate() {
      let newS = {
        score: 1,
        text: this.record.sentenceForAnnotation || null,
      };
      this.$emit("annotate", { sentences: [newS] });
      this.predictionNumber = 0;
      this.sentencesOrigin = "Annotation";
    },
    async onClearAnnotations() {
      await this.updateRecords({
        dataset: this.getText2TextDataset(),
        records: [
          {
            ...this.record,
            selected: true,
            status: "Edited",
            annotation: null,
            lastEditedSentence: null,
            sentenceForAnnotation: null,
          },
        ],
      });
      this.initializeSentenceOrigin();
    },
    async onReset() {
      this.refresh++;
      await (this.visibleSentence = this.selectedSentence);
      this.$emit("reset-record");
    },
    onDiscard() {
      this.$emit("discard");
    },
    getText2TextDataset() {
      return getText2TextDatasetById(this.datasetId);
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
      width: 100%;
      content: "";
      border-top: 1px solid palette(grey, 700);
      position: absolute;
      top: 0;
    }
  }
  &__tabs {
    display: flex;
    gap: $base-space * 2;
    margin-bottom: $base-space * 2;
    .button {
      border-radius: 0;
      padding: $base-space 0;
      border-bottom: 2px solid transparent;
      color: $black-54;
      &:hover {
        color: $black-87;
      }
      &.--active {
        border-color: $primary-color;
        color: $black-87;
      }
    }
  }
  &__prediction-tabs {
    display: flex;
    gap: $base-space * 2;
    .button {
      padding: 0;
      margin-bottom: $base-space * 2;
      @include font-size(13px);
      color: $black-20;
      &.--active,
      &:hover {
        color: $black-37;
      }
    }
  }
  &__sentences {
    display: flex;
    flex-direction: column;
  }
  &__score {
    @include font-size(13px);
    margin-right: 0;
    min-width: 33%;
    color: $black-54;
  }
}
.--editable {
  padding: $base-space;
  box-shadow: 0 1px 4px 1px rgba(222, 222, 222, 0.5);
  border-radius: $border-radius-s;
}
.sentence {
  &--non-editable {
    padding: $base-space 0;
  }
}
</style>
