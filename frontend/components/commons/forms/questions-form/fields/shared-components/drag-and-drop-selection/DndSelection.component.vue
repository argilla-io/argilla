<template>
  <div class="draggable">
    <div class="draggable__questions-container">
      <draggable
        class="draggable__questions"
        :list="ranking.questions"
        :group="{ name: 'question' }"
        :sort="false"
      >
        <div v-for="{ text, value } in ranking.questions" :key="value">
          <div class="draggable__rank-card" v-text="text" />
        </div>
      </draggable>
    </div>

    <div class="draggable__slots-container">
      <div
        class="draggable__slot"
        v-for="{ index, rank, items } in ranking.slots"
        :key="index"
      >
        <span> #{{ rank }} </span>

        <draggable
          class="draggable__questions-ranked"
          :list="items"
          group="question"
          :sort="false"
          @add="onMoveEnd"
          @remove="onMoveEnd"
        >
          <div v-for="{ text, value } in items" :key="value">
            <div class="draggable__ranked-card" v-text="text" />
          </div>
        </draggable>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "DndSelectionComponent",
  props: {
    ranking: {
      type: Object,
      required: true,
    },
  },
  methods: {
    onMoveEnd() {
      this.$emit("on-reorder", this.ranking);
    },
  },
};
</script>

<style lang="scss" scoped>
$primary-color: #4c4ea3;
$cards-separation: 10px;
$background-slot-color: #fafafa;
$slot-height: 30px;

.draggable {
  user-select: none;
  display: flex;
  flex-direction: row-reverse;
  gap: 5px;
  height: 100%;

  &__questions-container {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    width: 40%;
    height: 100%;
  }

  &__slots-container {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: $cards-separation;
  }

  &__questions {
    width: 100%;
    height: 150px;
    display: flex;
    flex-direction: column;
    gap: $cards-separation;
  }

  &__slot {
    width: 100%;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-items: center;
    gap: 2px;

    & span {
      width: 10%;
      height: 100%;
      display: inline-flex;
      align-items: center;
      padding: 5px;
      border-radius: 5px;
      text-align: center;
      background-color: $background-slot-color;
      font-weight: bold;
    }
  }

  &__rank-card {
    cursor: move;
    height: $slot-height;
    min-width: 50px;
    padding: 5px;
    color: $primary-color;
    border-radius: 3px;
    border: 1px solid $primary-color;
    font-weight: bold;

    &::before {
      content: "⋮⋮ ";
      color: gray;
    }
  }

  &__ranked-card {
    cursor: move;
    height: $slot-height;
    min-width: 50px;
    padding: 5px;
    background-color: $primary-color;
    border-radius: 3px;
    color: white;
    font-weight: bold;

    &::before {
      content: "⋮⋮ ";
    }
  }

  &__questions-ranked {
    width: 100%;
    min-height: $slot-height;
    background-color: $background-slot-color;
    border-radius: 5px;
    display: flex;
    flex-direction: column;
    gap: 5px;
  }
}
</style>
