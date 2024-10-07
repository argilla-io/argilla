<template>
  <DatasetConfigurationCard
    :item="metadata"
    :available-types="[...availableFieldTypes, ...availableMetadataTypes]"
    @is-focused="$emit('is-focused', $event)"
  />
</template>

<script>
export default {
  props: {
    metadata: {
      type: Object,
      required: true,
    },
    availableFieldTypes: {
      type: Array,
      required: true,
    },
    availableMetadataTypes: {
      type: Array,
      required: true,
    },
  },
  watch: {
    metadata: {
      handler() {
        if (this.availableFieldTypes.includes(this.metadata.type)) {
          this.$emit("field-type-selected", this.metadata);
        }
      },
      deep: true,
    },
  },
  model: {
    prop: "type",
    event: "change",
  },
};
</script>
