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
        <Text2TextContentEditable
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
              v-if="annotations.length"
              :class="sentencesOrigin === 'Annotation' ? '--active' : null"
              @click="changeVisibleSentences('Annotation')"
              >{{ `Annotation (${annotations.length})` }}</base-button
            >
            <base-button
              v-if="showPredictionTab"
              :class="sentencesOrigin === 'Prediction' ? '--active' : null"
              @click="changeVisibleSentences('Prediction')"
              >{{ `Predictions (${predictionsLength})` }}</base-button
            >
          </div>
          <div :class="sentencesOrigin !== 'Prediction' ? '--editable' : null">
            <div
              class="content__prediction-tabs"
              v-if="showPredictionInternalTabs"
            >
              <base-button
                @click="showPredictionNumber(index)"
                :class="predictionNumber === index ? '--active' : null"
                v-for="(sentence, index) in sentences"
                :key="index"
                >Score : {{ sentence.score | percent }}</base-button
              >
            </div>
            <Text2TextContentEditable
              v-if="sentencesOrigin !== 'Prediction'"
              :key="refresh"
              :annotation-enabled="annotationEnabled"
              :default-text="defaultText(sentence)"
              :content-editable="annotationEnabled"
              placeholder="Type your text"
              @annotate="onValidate()"
              @change-text="onTextChanged"
            />
            <p class="sentence--non-editable" :key="visibleSentence" v-else>
              {{ defaultText(sentence) }}
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
      visibleSentence: null,
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
        return this.idState.visibleSentence;
      },
      set: async function (newValue) {
        this.idState.visibleSentence = newValue;
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
      return this.sentences[this.predictionNumber]?.text;
    },
    predictionsLength() {
      return this.predictions.length;
    },
    showScore() {
      return this.sentencesOrigin === "Prediction";
    },
    showPredictionTab() {
      return (this.predictions.length && this.annotations.length) || false;
    },
    showPredictionInternalTabs() {
      return (
        this.sentencesOrigin !== "Annotation" && this.visibleSentence !== ""
      );
    },
    sentences() {
      const origin = this.sentencesOrigin;
      switch (origin) {
        case "Annotation":
          return this.annotations;
        case "Preannotation":
          return this.predictions;
        case "Prediction":
          return this.predictions;
        default:
          return [];
      }
    },
    allowValidation() {
      return (
        this.sentencesOrigin === "Preannotation" ||
        (this.record.status !== "Validated" &&
          this.visibleSentence &&
          !!this.record?.sentenceForAnnotation)
      );
    },
    text2textClassifierActionButtons() {
      const originIsEqualToPrediction = this.sentencesOrigin === "Prediction";
      const emptyVisibleSentence = this.visibleSentence !== "";
      const showClean =
        (this.annotations.length && emptyVisibleSentence) ||
        (!this.annotations.length && emptyVisibleSentence);
      return [
        {
          id: "validate",
          name: "Validate",
          allow: !originIsEqualToPrediction,
          active: this.allowValidation,
        },
        {
          id: "discard",
          name: "Discard",
          allow: !originIsEqualToPrediction,
          active: !this.recordStatusIs("Discarded"),
        },
        {
          id: "clear",
          name: "Clear",
          allow: !originIsEqualToPrediction,
          active: showClean,
        },
        {
          id: "reset",
          name: "Reset",
          allow: !originIsEqualToPrediction,
          active: this.recordStatusIs("Edited"),
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
    annotations(newValue, oldValue) {
      if (newValue !== oldValue) {
        this.initializeSentenceOrigin();
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
    defaultText(sentence) {
      return this.visibleSentence ?? (sentence.text || "");
    },
    async showPredictionNumber(index) {
      this.predictionNumber = index;
      this.visibleSentence = this.selectedSentence;
    },
    async onTextChanged(newText) {
      let status = "Edited";

      if (this.selectedSentence === newText) {
        status = "Default";
      }

      this.visibleSentence = newText;
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
      this.visibleSentence = this.selectedSentence;
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
          },
        ],
      });
      this.refresh++;
      this.visibleSentence = "";
    },
    async onReset() {
      this.refresh++;
      this.visibleSentence = this.selectedSentence;
      this.$emit("reset-record");
    },
    onDiscard() {
      this.$emit("discard");
    },
    recordStatusIs(status) {
      return this.record.status === status;
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
    margin-bottom: $base-space * 2;
    .button {
      border-radius: 0;
      padding: $base-space;
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
  border: 1px solid $black-10;
  border-radius: $border-radius-s;
  .content--exploration-mode & {
    border: none;
    padding: 0;
  }
}
.sentence {
  &--non-editable {
    font-style: italic;
    color: $black-54;
    padding: $base-space 0;
  }
}
</style>
