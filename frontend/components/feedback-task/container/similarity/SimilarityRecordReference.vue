<template>
  <div
    :class="isExpanded ? 'record-reference--isExpanded' : 'record-reference'"
  >
    <div class="record-reference__header">
      <SimilarityReference
        :preview="textPreview"
        :isExpanded="isExpanded"
        @expand="expand"
        @minimize="minimize"
      />
    </div>
    <RecordFeedbackTaskComponent
      v-if="isExpanded"
      :fields="fields"
      :showDefaultRecordHeader="false"
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
  },
  data() {
    return {
      isExpanded: true,
    };
  },
  computed: {
    textPreview() {
      const numberOfCharsByDefault = 30;
      const numberOfFields = this.fields[1] ? 1 : 2;
      let text = "";
      for (let i = 0; i <= numberOfFields; i++) {
        text += `${this.fields[i].title}: ${this.fields[i].content.substring(
          0,
          numberOfCharsByDefault / numberOfFields
        )}... `;
      }
      return text;
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
  .record {
    border: none;
    padding-top: 0;
  }
  :deep(.text_field_component) {
    background: $color-bg;
  }
  &--isExpanded {
    flex: 1;
    height: 100%;
    background: palette(white);
    overflow: auto;
    border: 1px solid palette(grey, 600);
    @extend .record-reference;
    #{$this}__header {
      padding: $base-space $base-space * 2;
    }
  }
}
</style>
