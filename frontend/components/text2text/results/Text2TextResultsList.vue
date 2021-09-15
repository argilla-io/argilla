<template>
  <results-list
    :dataset="dataset"
    :metadata-item="selectedMetadataItem"
    @closeMetadata="resetMetadataItem"
  >
    <template slot="record" slot-scope="results">
      <RecordText2Text
        :dataset="dataset"
        :record="results.record"
        @onShowMetadata="onShowMetadata"
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
  data: () => ({
    selectedMetadataItem: undefined,
  }),
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
