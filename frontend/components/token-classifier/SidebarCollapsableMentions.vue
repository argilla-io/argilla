<template>
  <div>
    <div
      v-for="(item, index) in Object.entries(object[k]).slice(0, limit)"
      :key="index"
      class="info"
    >
      <label>{{ item[0] }}</label>
      <span class="records-number">
        <strong>{{ item[1] }}</strong>
      </span>
    </div>
    <a
      v-if="limit !== 0"
      class="sidebar__view-more"
      href="#"
      @click.prevent="$emit('limit', k)"
      >{{ limit === 3 ? `view more` : `view less` }}</a
    >
  </div>
</template>
<script>
export default {
  props: {
    limit: {
      type: Number,
      required: true,
    },
    object: {
      type: Object,
      required: true,
    },
    k: {
      type: String,
      required: true,
    },
  },
};
</script>
<style scoped lang="scss">
.sidebar {
  &__view-more {
    color: $font-secondary;
    text-decoration: none;
    outline: none;
    margin-bottom: 1.5em;
    display: inline-block;
  }
}
.info {
  position: relative;
  display: flex;
  margin-bottom: 0.7em;
}
.records-number {
  margin-right: 0;
  margin-left: auto;
  font-weight: bold;
}
</style>
