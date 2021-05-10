<template>
  <div v-if="this.items && this.items < this.total" class="show-more-data">
    <p>{{ this.items }} of {{ this.total }} records</p>
    <ReProgress
      class="re-progress--minimal"
      re-mode="determinate"
      :progress="shownRecordsProgress"
    />
    <ReButton class="button-tertiary--outline" @click="$emit('moredata')">
      Next 5 records
    </ReButton>
  </div>
</template>

<script>
export default {
  props: {
    items: {
      default: undefined,
      type: Number,
    },
    total: {
      default: undefined,
      type: Number,
    },
  },
  data: () => ({}),
  computed: {
    shownRecordsProgress() {
      const progress = (100 * this.items) / this.total;
      return progress;
    },
  },
};
</script>
<style lang="scss" scoped>
.show-more-data {
  padding-top: 1em;
  text-align: center;
  display: block;
  margin-bottom: 2em;
  @include font-size(13px);
  .re-progress {
    width: 300px;
    margin: 1.5em auto;
    background: $line-smooth-color;
  }
  .re-button {
    margin-bottom: 0;
  }
}
</style>
