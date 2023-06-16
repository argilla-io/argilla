<template>
  <div class="draggable">
    <div class="draggable__questions-container">
      <draggable
        class="draggable__questions"
        :list="ranking.questions"
        :group="{ name: 'question' }"
        :sort="false"
      >
        <div v-for="item in ranking.questions" :key="item.name">
          <div class="draggable__rank-card">{{ item.name }}</div>
        </div>
      </draggable>
    </div>

    <div class="draggable__slots-container">
      <v-flex
        class="draggable__slot"
        v-for="slot in ranking.slots"
        :key="slot.index"
      >
        <span>
          {{ slot.name }}
        </span>

        <draggable
          class="draggable__questions-ranked"
          :list="slot.items"
          group="question"
          :sort="false"
        >
          <v-flex v-for="item in slot.items" :key="item.name">
            <div class="draggable__ranked-card">{{ item.name }}</div>
          </v-flex>
        </draggable>
      </v-flex>
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
