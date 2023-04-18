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
      <div class="content" v-text="text" />
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
  gap: $base-space;
  padding: 2 * $base-space 4 * $base-space 2 * $base-space 4 * $base-space;
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
}

.item {
  display: flex;
  flex-direction: column;
  padding: 2 * $base-space;
  background: #f5f5f5;
  border-radius: 8px;
  .title-area {
    display: flex;
    align-items: center;
    gap: $base-space;
    color: rgba(0, 0, 0, 0.37);
  }
}
</style>
