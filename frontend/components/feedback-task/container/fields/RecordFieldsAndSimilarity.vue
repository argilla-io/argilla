<template>
  <div class="fields">
    <SimilarityRecordReference :fields="fields" />
    <RecordFields :recordStatus="recordStatus" :fields="fields" />
  </div>
</template>
<script>
export default {
  props: {
    recordStatus: {
      type: String,
    },
    fields: {
      type: Array,
      required: true,
    },
  },
};
</script>
<style lang="scss" scoped>
.fields {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: $base-space * 2;
  min-width: 0;
  height: 100%;
}
</style>
