<template>
  <BaseBadgeSkeleton font-size="11px" v-if="isFieldsLoading" :quantity="1" />
  <div class="fields" v-else>
    <div class="fields__badges">
      <BaseBadge
        v-for="field in fields"
        :key="field.id"
        :text="$t(field.type)"
        color="var(--bg-opacity-54)"
        font-size="11px"
      />
    </div>
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

<style scoped lang="scss">
.fields {
  display: flex;
  flex-wrap: wrap;
  gap: calc($base-space / 2);
  &__badges {
    display: flex;
    flex-wrap: wrap;
    gap: calc($base-space / 2);
  }
}
</style>
