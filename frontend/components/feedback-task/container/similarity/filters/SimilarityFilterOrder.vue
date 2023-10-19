<template>
  <SimilarityConfigDropdown v-model="value" :options="['most', 'least']" />
</template>
<script>
export default {
  props: {
    value: {
      type: String,
      required: true,
    },
  },
};
</script>
