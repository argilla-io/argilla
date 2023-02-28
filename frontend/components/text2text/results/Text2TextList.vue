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
      class="content content--separator"
      :class="
        !annotationEnabled ? 'content--exploration-mode' : 'content--selectable'
      "
    >
      <div class="--editable" :class="isFocused ? '--focused' : null">
        <Text2TextContentEditable
          v-if="!annotations && !predictions"
          :annotation-enabled="annotationEnabled"
          :edition-mode="true"
          :default-text="visibleSentence || ''"
          placeholder="Type your text"
          @annotate="onValidate()"
          @change-text="onTextChanged"
          @on-change-focus="setFocus"
        />
        <div v-else-if="annotationEnabled || annotations.length">
          <div
            class="content__prediction-tabs"
            v-if="showPredictionInternalTabs"
          >
            <base-button
              @click="showPredictionNumber(index)"
              :class="predictionNumber === index ? '--active' : null"
              v-for="(prediction, index) in predictions"
              :key="index"
              data-title="Score"
              >{{ prediction.score | percent }}</base-button
            >
          </div>
          <Text2TextContentEditable
            :key="refresh"
            :annotation-enabled="annotationEnabled"
            :default-text="defaultText"
            :content-editable="annotationEnabled"
            :annotations="annotations"
            placeholder="Type your text"
            @annotate="onValidate()"
            @change-text="onTextChanged"
            @on-change-focus="setFocus"
          />
        </div>
      </div>
      <Text2TextPredictions
        v-if="visiblePredictions"
        :record="record"
        :predictions="predictions"
      />
    </div>
    <record-action-buttons
      v-if="annotationEnabled"
      :actions="text2textClassifierActionButtons"
      @validate="onValidate()"
      @clear="onClearAnnotations()"
      @reset="onReset()"
      @discard="onDiscard()"
    />
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
      predictionNumber: 0,
      refresh: 1,
      visibleSentence: null,
    };
  },
  data: () => {
    return {
      isFocused: false,
    };
  },
  computed: {
    predictionNumber: {
      get: function () {
        return this.idState.predictionNumber;
      },
      set: function (newValue) {
        this.idState.predictionNumber = newValue;
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
    visibleSentence: {
      get: function () {
        return this.idState.visibleSentence;
      },
      set: async function (newValue) {
        this.idState.visibleSentence = newValue;
      },
    },
    defaultText() {
      return (
        this.visibleSentence ??
        (this.currentAnnotation ||
          this.predictions[this.predictionNumber]?.text ||
          "")
      );
    },
    currentAnnotation() {
      return this.annotations[0]?.text;
    },
    visiblePredictions() {
      const isExploreMode = !this.annotationEnabled;
      const arePredictionEdited =
        this.predictions[this.predictionNumber]?.text !== this.defaultText;
      const isAnnotationVisible = this.currentAnnotation === this.defaultText;
      return (
        !!this.predictionsLength &&
        (isExploreMode || arePredictionEdited || isAnnotationVisible)
      );
    },
    predictionsLength() {
      return this.predictions.length;
    },
    showPredictionInternalTabs() {
      return (
        !this.annotations.length &&
        this.visibleSentence !== "" &&
        !this.visiblePredictions
      );
    },
    allowValidation() {
      return (
        !this.annotations.length ||
        (this.record.status !== "Validated" &&
          this.defaultText &&
          !!this.record?.sentenceForAnnotation) ||
        false
      );
    },
    text2textClassifierActionButtons() {
      const emptyVisibleSentence = this.visibleSentence !== "";
      const showClean =
        (this.annotations.length && emptyVisibleSentence) ||
        (!this.annotations.length && emptyVisibleSentence);
      return [
        {
          id: "validate",
          name: "Validate",
          allow: true,
          active: !this.allowValidation,
          disable: !this.defaultText,
        },
        {
          id: "discard",
          name: "Discard",
          allow: true,
          active: this.recordStatusIs("Discarded"),
        },
        {
          id: "clear",
          name: "Clear",
          allow: true,
          disable: !showClean,
        },
        {
          id: "reset",
          name: "Reset",
          allow: true,
          disable: !this.recordStatusIs("Edited"),
        },
      ];
    },
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateDatasetRecords",
    }),
    async showPredictionNumber(index) {
      this.refresh++;
      this.predictionNumber = index;
      this.visibleSentence = this.predictions[this.predictionNumber]?.text;
    },
    async onTextChanged(newText) {
      let status = this.currentAnnotation === newText ? "Default" : "Edited";
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
    async onValidate() {
      let newS = {
        score: 1,
        text: this.record.sentenceForAnnotation || null,
      };
      this.$emit("annotate", { sentences: [newS] });
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
      this.visibleSentence = this.currentAnnotation;
      this.$emit("reset-record");
    },
    onDiscard() {
      this.$emit("discard");
    },
    recordStatusIs(status) {
      return this.record.status === status;
    },
    setFocus(status) {
      this.isFocused = status;
    },
    getText2TextDataset() {
      return getText2TextDatasetById(this.datasetId);
    },
  },
  beforeDestroy() {
    this.visibleSentence = null;
  },
};
</script>

<style lang="scss" scoped>
.content {
  position: relative;
  display: flex;
  gap: $base-space * 2;
  margin-top: 1em;
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
  &__prediction-tabs {
    display: flex;
    gap: $base-space;
    justify-content: right;
    .button {
      padding: 2px 4px;
      @include font-size(13px);
      color: $black-54;
      border: 1px solid $black-20;
      border-radius: $border-radius;
      background-color: $black-4;
      &.--active,
      &:hover {
        background-color: palette(white);
      }
      &.--active {
        color: $primary-color;
        border-color: $primary-color;
        background-color: palette(white);
      }
      &[data-title] {
        position: relative;
        overflow: visible;
        @extend %has-tooltip--top;
      }
    }
  }
}
.--editable {
  width: calc(100% - 200px);
  padding: $base-space;
  border: 1px solid $black-20;
  border-radius: $border-radius-s;
  &.--focused {
    border-color: $primary-color;
  }
  .content--exploration-mode & {
    border: none;
    padding: 0;
  }
}
</style>
