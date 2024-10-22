<template>
  <div class="import-from-python" v-click-outside="closeDialog">
    <BaseButton class="import-from-python__button" @click="toggleVisibleSnippet"
      ><svgicon
        class="import-from-python__button__icon"
        name="code"
        width="18"
        height="18"
        color="var(--bg-opacity-87)"
      ></svgicon
      >Import from Python</BaseButton
    >
    <transition name="fade" appear>
      <dialog class="import-from-python__dialog" v-if="visibleSnippet">
        <p class="import-from-python__title">Import from Python</p>
        <div class="import-from-python__content">
          <BaseInputContainer>
            <BaseInput v-model="repositoryId" placeholder="Repository ID" />
          </BaseInputContainer>
          <BaseButton>Import</BaseButton>
        </div>
      </dialog>
    </transition>
  </div>
</template>

<script>
import "assets/icons/code";
export default {
  data() {
    return {
      visibleSnippet: false,
    };
  },
  methods: {
    toggleVisibleSnippet() {
      this.visibleSnippet = !this.visibleSnippet;
    },
    closeDialog() {
      this.visibleSnippet = false;
    },
  },
};
</script>

<style lang="scss" scoped>
.import-from-python {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  &__dialog {
    display: flex;
    flex-direction: column;
    gap: $base-space;
    padding: $base-space * 2;
    background-color: var(--bg-accent-grey-2);
    border-radius: $border-radius-m;
    &__title {
      font-weight: 500;
    }
    &__content {
      display: flex;
      flex-direction: column;
      gap: $base-space;
    }
  }
  &__button.button {
    min-height: 42px;
    background: linear-gradient(
      177.33deg,
      var(--bg-accent-grey-1) 16.49%,
      var(--bg-opacity-4) 114.03%
    );
    box-shadow: 0 0 0 1px var(--bg-opacity-10);
  }
  &__button__icon {
    flex-shrink: 0;
  }
}
.fade-enter-active,
.fade-leave-active {
  transition: all 0.4s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>