<template>
  <div class="record">
    <div class="record__header" v-if="showDefaultRecordHeader">
      <div class="record__header--left">
        <StatusTag
          v-if="recordStatus"
          class="record__status"
          :recordStatus="recordStatus"
        />
        <BaseBadge :text="similarityScore" data-title="Similarity Score" />
      </div>
      <SimilarityFilter
        v-if="recordVectors.length"
        :available-vectors="recordVectors"
      />
    </div>
    <div
      v-for="{ id, title, content, isTextType, settings } in fields"
      :key="id"
    >
      <TextFieldComponent
        v-if="isTextType"
        :title="title"
        :fieldText="content"
        :useMarkdown="settings.use_markdown"
        :stringToHighlight="searchValue"
      />
    </div>
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
    showDefaultRecordHeader: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      similarityScore: "80 %",
      recordVectors: [{ id: "text_vector" }, { id: "second_vector" }],
    };
  },
  computed: {
    searchValue() {
      return this.$route.query?._search ?? "";
    },
  },
};
</script>

<style lang="scss" scoped>
.record {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: auto;
  gap: $base-space * 2;
  padding: $base-space * 2;
  background: palette(white);
  border: 1px solid palette(grey, 600);
  border-radius: $border-radius-m;
  &__header {
    display: flex;
    justify-content: space-between;
    &--left {
      display: flex;
      align-items: center;
      gap: $base-space;
    }
  }
  &__status {
    display: inline-flex;
    margin-right: auto;
  }
}
.badge {
  color: #ee7b00;
  border-color: #ee7b00;
  background: lighten(#ee7b00, 50%);
  font-weight: 500;
  &[data-title] {
    position: relative;
    @extend %has-tooltip--right;
  }
}
</style>
