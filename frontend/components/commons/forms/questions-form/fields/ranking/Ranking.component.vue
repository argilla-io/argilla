<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :title="title"
      :isRequired="isRequired"
      :tooltipMessage="description"
    />
  </div>
</template>

<script>
export default {
  name: "RankingComponent",
  props: {
    title: {
      type: String,
      required: true,
    },
    isRequired: {
      type: Boolean,
      default: false,
    },
    description: {
      type: String,
      default: "",
    },
    settings: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped></style>
