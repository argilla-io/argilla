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
      validator: (settings) => {
        const settingsKeys = Object.keys(settings);
        const checkAllKeysOfSettingsAreValid = settingsKeys.every((key) =>
          ["type", "options", "ranking_slots"].includes(key)
        );
        return checkAllKeysOfSettingsAreValid;
      },
    },
  },
  data() {
    return {
      ranking: [],
    };
  },
  beforeMount() {
    // this.ranking = [
    //   {
    //     index: 1,
    //     items: [
    //       {
    //         title: "item 1",
    //       },
    //     ],
    //   },
    //   {
    //     index: 2,
    //     items: [
    //       {
    //         title: "item 2",
    //       },
    //       {
    //         title: "item 3",
    //       },
    //     ],
    //   },
    // ];
  },
};
</script>

<style lang="scss" scoped></style>
