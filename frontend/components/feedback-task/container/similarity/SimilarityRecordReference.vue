<template>
  <div
    :class="
      isExpanded
        ? 'record-reference--isExpanded'
        : 'record-reference--isCollapsed'
    "
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
    border: 1px solid $black-10;
    :deep(.similarity-reference__button-close) {
      opacity: 0;
      pointer-events: none;
    }
    &:hover {
      :deep(.similarity-reference__button-close) {
        opacity: 1;
        pointer-events: all;
      }
    }
    #{$this}__header {
      padding: $base-space $base-space * 2;
    }
  }
  &--isCollapsed {
    @extend .record-reference;
    background: $black-4;
    border-radius: $border-radius;
    transition: background 0.2s ease;
    &:hover {
      transition: background 0.2s ease;
      background: $black-6;
    }
    #{$this}__header {
      padding: calc($base-space / 2) $base-space;
    }
  }
}
</style>
