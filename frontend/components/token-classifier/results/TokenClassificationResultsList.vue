<template>
  <results-list
    :dataset="dataset"
    :metadata-item="selectedMetadataRecord"
    @onCloseMetadata="onCloseMetadata"
  >
    <template slot="record" slot-scope="results">
      <record-token-classification
        :dataset="dataset"
        :record="results.record"
      />
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
  data() {
    return {
      selectedMetadataRecord: undefined,
    };
  },
  computed: {
    isExplainedRecord() {
      return this.dataset.results.records.some((record) => record.explanation);
    },
  },
  methods: {
    onCloseMetadata() {
      this.selectedMetadataRecord = undefined;
    },
  },
};
</script>
