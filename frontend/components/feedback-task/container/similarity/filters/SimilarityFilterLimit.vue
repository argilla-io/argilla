<template>
  <SimilarityConfigDropdown v-model="value" :options="[50, 100, 200]" />
</template>
<script>
export default {
  props: {
    value: {
      type: Number,
      required: true,
    },
  },
};
</script>
