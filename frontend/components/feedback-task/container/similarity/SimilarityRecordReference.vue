<template>
  <div
    :class="isExpanded ? 'record-reference--isExpanded' : 'record-reference'"
  >
    <div class="record-reference__header">
      <SimilarityReference
        :preview="fieldsPreview"
        :isExpanded="isExpanded"
        :recordCriteria="recordCriteria"
        @expand="expand"
        @minimize="minimize"
      />
    </div>
    <RecordFields v-if="isExpanded" :fields="fields" />
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
      isExpanded: false,
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
    expand() {
      this.isExpanded = true;
    },
    minimize() {
      this.isExpanded = false;
    },
  },
};
</script>
<style lang="scss" scoped>
$color-bg: #fff3e9;
.record-reference {
  $this: &;
  display: flex;
  flex-direction: column;
  border-radius: $border-radius-m;
  background: palette(white);
  border: 1px solid palette(grey, 600);
  &__header {
    padding: calc($base-space / 2) $base-space * 2;
  }
  .record {
    border: none;
    padding-top: 0;
  }
  :deep(.text_field_component) {
    background: $color-bg;
  }
  &--isExpanded {
    max-height: 30vh;
    overflow: auto;
    @extend .record-reference;
    #{$this}__header {
      padding: $base-space $base-space * 2;
    }
  }
}
</style>
