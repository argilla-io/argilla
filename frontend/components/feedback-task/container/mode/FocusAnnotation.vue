<template>
  <div class="wrapper">
    <section class="wrapper__records">
      <DatasetFiltersComponent :recordCriteria="recordCriteria">
        <ToggleAnnotationType
          v-if="
            records.hasRecordsToAnnotate && recordCriteria.committed.isPending
          "
          :recordCriteria="recordCriteria"
      /></DatasetFiltersComponent>
      <SimilarityRecordReference
        v-show="recordCriteria.isFilteringBySimilarity"
        v-if="!!records.reference"
        :fields="records.reference.fields"
        :recordCriteria="recordCriteria"
        :availableVectors="datasetVectors"
      />
      <div class="wrapper__records__header">
        <PaginationFeedbackTaskComponent :recordCriteria="recordCriteria" />
      </div>
      <Record
        v-if="records.hasRecordsToAnnotate"
        :class="swipeClass"
        :datasetVectors="datasetVectors"
        :recordCriteria="recordCriteria"
        :record="record"
      />
      <div v-else class="wrapper--empty">
        <p class="wrapper__text --heading3" v-text="noRecordsMessage" />
      </div>
    </section>

    <QuestionsFormComponent
      v-if="!!record"
      :key="`${record.id}_questions`"
      class="wrapper__form"
      :class="statusClass"
      :datasetId="recordCriteria.datasetId"
      :record="record"
      :show-discard-button="!record.isDiscarded"
      :is-draft-saving="isDraftSaving"
      :is-submitting="isSubmitting"
      :is-discarding="isDiscarding"
      :enableAutoSubmitWithKeyboard="true"
      @on-submit-responses="onSubmit"
      @on-discard-responses="onDiscard"
      @on-save-draft="onSaveDraft"
    />
  </div>
</template>
<script>
import { useFocusAnnotationViewModel } from "./useFocusAnnotationViewModel";
export default {
  props: {
    recordCriteria: {
      type: Object,
      required: true,
    },
    datasetVectors: {
      type: Array,
      required: false,
    },
    records: {
      type: Object,
      required: true,
    },
    record: {
      type: Object,
    },
    noRecordsMessage: {
      type: String,
      required: true,
    },
    statusClass: {
      type: String,
      required: true,
    },
  },
  methods: {
    async onSubmit() {
      await this.submit(this.record);
      this.$emit("on-submit-responses");
    },
    async onDiscard() {
      if (this.record.isDiscarded) return;

      await this.discard(this.record);
      this.$emit("on-discard-responses");
    },
    async onSaveDraft() {
      await this.saveAsDraft(this.record);
    },
  },
  data() {
    return {
      swipeClass: "",
    };
  },
  mounted() {
    this.$root.$on("swipeLeft", () => {
      this.swipeClass = "swipeLeft";

      setTimeout(() => {
        this.swipeClass = "";
      }, 500);
    });
    this.$root.$on("swipeRight", () => {
      this.swipeClass = "swipeRight";

      setTimeout(() => {
        this.swipeClass = "";
      }, 500);
    });
    this.$root.$on("swipeUp", () => {
      this.swipeClass = "swipeUp";

      setTimeout(() => {
        this.swipeClass = "";
      }, 500);
    });
  },
  setup() {
    return useFocusAnnotationViewModel();
  },
};
</script>

<style lang="scss" scoped>
.swipeLeft {
  animation: swipeLeft 0.5s ease-in-out forwards;
}
.swipeRight {
  animation: swipeRight 0.5s ease-in-out forwards;
}
.swipeUp {
  animation: swipeUp 0.5s ease-in-out forwards;
  background: blue;
}

@keyframes swipeUp {
  0% {
    transform: translateY(-20px);
  }
  25% {
    transform: translateY(-10vh);
  }
  50% {
    transform: translateY(-30vh);
  }
  75% {
    transform: translateY(-60vh);
  }
  100% {
    transform: translateY(-100vh);
  }
}

@keyframes swipeRight {
  0% {
    transform: rotate(10deg) translate(10vw);
  }
  25% {
    transform: rotate(20deg) translate(30vw);
  }
  50% {
    transform: rotate(20deg) translate(60vw);
  }
  75% {
    transform: rotate(70deg) translate(80vw);
  }
  100% {
    visibility: hidden;
  }
}

@keyframes swipeLeft {
  0% {
    transform: rotate(-10deg) translate(-10vw);
  }
  25% {
    transform: rotate(-20deg) translate(-30vw);
  }
  50% {
    transform: rotate(-20deg) translate(-60vw);
  }
  75% {
    transform: rotate(-70deg) translate(-80vw);
  }
  100% {
    visibility: hidden;
  }
}

.wrapper {
  overflow: hidden;
  position: relative;
  flex-direction: column;
  display: flex;
  flex-wrap: wrap;
  height: 100%;
  gap: $base-space * 2;
  padding: $base-space * 2;
  @include media("<desktop") {
    flex-flow: column;
    overflow: hidden;
  }
  &__records,
  &__form {
    @include media("<desktop") {
      overflow: visible;
      height: auto !important;
      max-height: none !important;
    }
  }
  &__records {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: $base-space;
    height: 100%;
    min-width: 0;
    @include media("<desktop") {
      flex: 1;
      height: auto;
    }
    &__header {
      display: flex;
      justify-content: flex-end;
      align-items: center;
      gap: $base-space;
    }
  }
  &__text {
    color: $black-54;
  }
  &--empty {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
</style>
