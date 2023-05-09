<template>
  <div class="record">
    <StatusTag class="record__status" :title="recordStatus" />
    <div class="item" v-for="{ id, title, field_text } in fields" :key="id">
      <div class="title-area --body1">
        <span v-text="title" />
      </div>
      <div class="record__content --body1" v-text="field_text" />
    </div>
  </div>
</template>

<script>
export default {
  props: {
    recordStatus: {
      type: String,
      required: true,
    },
    fields: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped>
.record {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: auto;
  gap: $base-space * 2;
  padding: $base-space * 2;
  background: palette(white);
  border: 1px solid palette(grey, 600);
  border-radius: $border-radius;
  &__status {
    display: inline-flex;
    margin-right: auto;
  }
  &__content {
    white-space: pre-wrap;
  }
}

.item {
  display: flex;
  flex-direction: column;
  gap: $base-space;
  padding: 2 * $base-space;
  background: palette(grey, 800);
  border-radius: $border-radius;
  .title-area {
    display: flex;
    align-items: center;
    gap: $base-space;
    color: $black-37;
  }
}
</style>
