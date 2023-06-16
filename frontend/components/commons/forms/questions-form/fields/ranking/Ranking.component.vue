<template>
  <div class="wrapper">
    <QuestionHeaderComponent
      :title="title"
      :isRequired="isRequired"
      :tooltipMessage="description"
    />

    <DndSelectionComponent :ranking="ranking" />
  </div>
</template>

<script>
import { factoryRanking } from "./ranking-adapter";
import { settingsFake } from "./ranking-fakes";

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
    // values: {
    //   type: Array,
    //   required: true,
    // },
    // settings: {
    //   type: Object,
    //   required: true,
    //   validator: (settings) => {
    //     const settingsKeys = Object.keys(settings);
    //     const checkAllKeysOfSettingsAreValid = settingsKeys.every((key) =>
    //       ["type", "options", "ranking_slots"].includes(key)
    //     );
    //     return checkAllKeysOfSettingsAreValid;
    //   },
    // },
  },
  data() {
    return {
      ranking: factoryRanking(settingsFake),
    };
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
