<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :title="title"
      :isRequired="isRequired"
      :tooltipMessage="description"
    />

    <dndSelectionComponent :listOfItems="ranking" />
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
    values: {
      type: Array,
      required: true,
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
  created() {
    this.initialSettings = {
      options: [
        {
          value: "label-01",
          text: "My label",
          description: "This is an optional field",
        },
        { value: "label-02", text: "My other Label" },
        { value: "label-03", text: "Wat?!" },
        { value: "label-04", text: "Ough!" },
      ],
      ranking_slots: [
        {
          text: "First place",
        },
        {
          text: "Second place",
        },
        {
          text: "Out of top 2",
        },
      ],
    };
  },
  beforeMount() {
    this.ranking = [
      {
        index: 1,
        items: [
          {
            title: "item 1",
          },
        ],
      },
      {
        index: 2,
        items: [
          {
            title: "item 2",
          },
          {
            title: "item 3",
          },
        ],
      },
    ];
  },
};
</script>

<style lang="scss" scoped></style>
