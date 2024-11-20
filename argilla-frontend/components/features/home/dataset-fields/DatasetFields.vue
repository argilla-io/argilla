<template>
  <BaseBadgeSkeleton v-if="isFieldsLoading" :quantity="3" />
  <div class="fields" v-else>
    <span class="fields__title">{{ $t("fields") }}</span>
    <div class="fields__badges">
      <DatasetBadge
        v-for="field in fields"
        :key="field.id"
        :text="$t(field.type)"
        font-size="11px"
        color="hsl(50, 40%, 53%)"
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
  gap: 8px;
  &__title {
    @include font-size(12px);
    color: var(--fg-tertiary);
    font-weight: 200;
    min-width: $base-space * 8;
  }
  &__badges {
    display: flex;
    flex-wrap: wrap;
    gap: $base-space;
  }
}
</style>
