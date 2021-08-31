<template>
  <results-list
    :dataset="dataset"
    :metadata-item="selectedMetadataItem"
    @closeMetadata="resetMetadataItem"
  >
    <template slot="header">
      <explain-help-info v-if="isExplainedRecord" />
    </template>
    <template slot="record" slot-scope="results">
      <record-text-classification
        :dataset="dataset"
        :record="results.record"
        @onShowMetadata="onShowMetadata"
      />
      <!--<RecordTokenClassification :dataset="dataset" :record="results.record" />-->
    </template>
  </results-list>
</template>
<script>
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => ({
    selectedMetadataItem: undefined,
  }),
  computed: {
    isExplainedRecord() {
      return this.dataset.results.records.some((record) => record.explanation);
    },
  },
  methods: {
    onShowMetadata(id) {
      this.selectedMetadataItem = id;
    },
    resetMetadataItem() {
      this.selectedMetadataItem = undefined;
    },
  },
};
</script>
