<template>
  <div class="record">
    <div
      class="item"
      v-for="{ id, title, text } in record.record_fields"
      :key="id"
    >
      <div class="title-area --body1">
        <span v-text="title" />
      </div>
      <div class="content --body1" v-text="text" />
    </div>
  </div>
</template>

<script>
export default {
  props: {
    record: {
      type: Object,
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
}

.item {
  display: flex;
  flex-direction: column;
  gap: $base-space;
  padding: 2 * $base-space;
  background: $black-4;
  border-radius: $border-radius;
  .title-area {
    display: flex;
    align-items: center;
    gap: $base-space;
    color: $black-37;
  }
}
</style>
