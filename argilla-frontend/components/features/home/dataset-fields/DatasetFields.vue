<template>
  <BaseBadgeSkeleton v-if="isFieldsLoading" :quantity="3" />
  <div class="fields" v-else>
    <DatasetBadge
      v-for="field in fields"
      :key="field.id"
      :text="$t(field.type)"
      font-size="12px"
      color="hsl(50, 40%, 53%)"
    />
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
