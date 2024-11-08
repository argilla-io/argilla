<template>
  <BaseBadgeSkeleton v-if="isFieldsLoading" :quantity="3" />
  <div class="fields" v-else>
    <BaseBadge v-for="field in fields" :key="field.id" :text="$t(field.type)" />
  </div>
</template>
<script>
import { useDatasetFields } from "./useDatasetFields";

export default {
  name: "DatasetFields",
  props: {
    dataset: {
      type: Object,
    },
  },
  setup(props) {
    return useDatasetFields(props);
  },
};
</script>

<style scoped>
.fields {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
