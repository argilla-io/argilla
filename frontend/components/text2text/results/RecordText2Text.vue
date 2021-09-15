<template>
  <div class="record">
    <div class="record--left record__item">
      <record-string-text-2-text
        :query-text="dataset.query.text"
        :text="record.text"
      />
      <text-2-text-annotation-area
        v-if="annotationEnabled"
        :prediction="predictionSentences"
        :annotation="annotationSentences"
        @annotate="onAnnotate"
      />
      <text-2-text-exploration-area
        v-else
        :prediction="predictionSentences"
        :annotation="annotationSentences"
      />
    </div>
  </div>
</template>
<script>
import { Text2TextRecord, Text2TextDataset } from "@/models/Text2Text";
import { mapActions } from "vuex";
export default {
  props: {
    dataset: {
      type: Text2TextDataset,
      required: true,
    },
    record: {
      type: Text2TextRecord,
      required: true,
    },
  },
  data: () => ({}),
  computed: {
    annotationEnabled() {
      return this.dataset.viewSettings.annotationEnabled;
    },
    annotationSentences() {
      return this.record.annotation ? this.record.annotation.sentences : [];
    },
    predictionSentences() {
      return this.record.prediction ? this.record.prediction.sentences : [];
    },
  },
  methods: {
    ...mapActions({
      validate: "entities/datasets/validateAnnotations",
    }),

    async onAnnotate({ sentences }) {
      await this.validate({
        dataset: this.dataset,
        agent: this.$auth.user,
        records: [
          {
            ...this.record,
            status: "Validated",
            annotation: {
              sentences,
            },
          },
        ],
      });
    },
  },
};
</script>

<style scoped lang="scss">
.record {
  display: flex;
  &__item {
    margin-right: 1em;
    display: block;
    @include font-size(16px);
    line-height: 1.6em;
  }
  &--left {
    width: 100%;
    padding: 2em 6em 0.5em 2em;
    .list__item--annotation-mode & {
      padding-left: 65px;
    }
  }
}
</style>
