<template>
  <div class="record-reference__wrapper">
    <SimilarityReference
      :preview="fieldsPreview"
      :visibleReferenceRecord="visibleReferenceRecord"
      :recordCriteria="recordCriteria"
      @show-reference-record="showReferenceRecord"
      @hide-reference-record="hideReferenceRecord"
    />
    <RecordFields
      v-if="visibleReferenceRecord"
      class="record-reference"
      :fields="fields"
    />
  </div>
</template>

<script>
export default {
  props: {
    fields: {
      type: Array,
      required: true,
    },
    recordCriteria: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      visibleReferenceRecord: false,
      numberOfVisibleCharsInPreview: 30,
    };
  },
  computed: {
    fieldsPreview() {
      const firstFieldText = (index) =>
        `${this.fields[index].title}: ${this.fields[index].content}`;
      return this.fields.length > 1
        ? [firstFieldText(0), firstFieldText(1)]
        : [firstFieldText(0)];
    },
  },
  methods: {
    showReferenceRecord() {
      this.visibleReferenceRecord = true;
    },
    hideReferenceRecord() {
      this.visibleReferenceRecord = false;
    },
  },
};
</script>
<style lang="scss" scoped>
.record-reference {
  &.record {
    max-height: 30vh;
    overflow: auto;
    border: 1px solid $similarity-color;
  }
  &__wrapper {
    display: flex;
    flex-direction: column;
    gap: $base-space;
  }
}
</style>
