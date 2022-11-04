<template>
  <transition-group name="chips" class="chips">
    <div class="chips__items" v-for="chip in chips" :key="chip.id">
      <label
        class="chip"
        :for="chip.id"
        v-text="chip.text"
        :class="[chip.is_activate ? 'activate' : 'not-activate']"
        @click="onChipsSelect(chip)"
      />
      <input :id="chip.id" type="checkbox" v-model="chip.is_activate" />
    </div>
  </transition-group>
</template>

<script>
export default {
  component: "ChipsComponent",
  props: {
    chips: {
      type: Array,
      required: true,
    },
    isMultiSelection: {
      type: Boolean,
      default: () => false,
    },
  },
  data() {
    return {
      cloneChips: [],
    };
  },
  methods: {
    onChipsSelect({ id, dataset_id }) {
      this.$emit("on-chips-select", { id, dataset_id });
    },
  },
};
</script>

<style lang="scss" scoped>
.chips {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  &__items {
    display: inline-flex;
  }
}
.chip {
  display: flex;
  justify-content: center;
  align-items: center;
  padding-inline: 1em;
  border: none;
  min-height: 50px;
  min-width: 100px;
  border-radius: 8px;
  cursor: pointer;
  user-select: none;
}

input[type="checkbox"] {
  display: none;
}
.activate {
  color: white;
  background-color: #4c4ea3;
}

.not-activate {
  color: black;
  background-color: #e0e1ff;
}

.chips__items {
  transition: all 1s;
}
.chips-enter,
.chips-leave-to {
  opacity: 0;
}
.chips-leave-active {
  position: absolute;
}
</style>
