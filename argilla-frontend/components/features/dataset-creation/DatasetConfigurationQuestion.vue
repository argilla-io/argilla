<template>
  <DatasetConfigurationCard :item="question" :type-options="typeOptions">
    <template slot="header">
      <BaseButton
        class="config-card__remove"
        @click="remove"
        v-if="removeIsAllowed"
        >Remove</BaseButton
      >
    </template>
  </DatasetConfigurationCard>
</template>

<script>
export default {
  props: {
    question: {
      type: Object,
      required: true,
    },
    typeOptions: {
      type: Array,
      required: true,
    },
    removeIsAllowed: {
      type: Boolean,
      default: false,
    },
  },
  model: {
    prop: "type",
    event: "change",
  },
  methods: {
    remove() {
      this.$emit("remove");
    },
  },
};
</script>
