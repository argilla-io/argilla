<template>
  <div class="settings__container">
    <div class="settings__edition-form">
      <h2 class="--heading5 --medium" v-text="$t('settings.editVectors')" />
      <div v-for="vector in settings.vectors" :key="vector.id">
        <form
          @submit.prevent="onSubmit(vector)"
          class="settings__edition-form__vectors"
        >
          <div class="settings__edition-form__name">
            <h4 class="--body1 --medium" v-text="vector.name" />
          </div>

          <Validation
            :validations="vector.validate().title"
            class="settings__edition-form__group"
          >
            <label for="vector.title" v-text="$t('title')" />
            <input type="text" id="vector.title" v-model="vector.title" />
          </Validation>

          <div class="settings__edition-form__group">
            <label for="vector.dimensions" v-text="$t('dimension')" />
            <input
              type="number"
              id="vector.dimensions"
              v-model="vector.dimensions"
              disabled
            />
          </div>

          <div class="settings__edition-form__footer">
            <BaseButton
              type="button"
              class="secondary light small"
              @on-click="restore(vector)"
              :disabled="!vector.isModified"
            >
              <span v-text="$t('cancel')" />
            </BaseButton>
            <BaseButton
              type="submit"
              class="primary small"
              :disabled="!vector.isModified || !vector.isValid"
            >
              <span v-text="$t('update')" />
            </BaseButton>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { useSettingsVectorsViewModel } from "./useSettingsVectorsViewModel";

export default {
  name: "SettingsVectors",
  props: {
    settings: {
      type: Object,
      required: true,
    },
  },
  methods: {
    onSubmit(vector) {
      this.update(vector);
    },
  },
  setup() {
    return useSettingsVectorsViewModel();
  },
};
</script>
<style lang="scss" scoped>
.settings {
  &__container {
    display: flex;
    gap: $base-space * 4;
    height: 100%;
    flex-wrap: wrap;
    min-height: 0;
    overflow: auto;
  }

  &__edition-form {
    display: flex;
    flex: 1;
    flex-direction: column;
    gap: $base-space * 2;
    max-width: 800px;
    padding-top: $base-space;

    &__vectors {
      display: flex;
      flex-direction: column;
      gap: $base-space * 2;
    }

    &__name {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: space-between;
      gap: $base-space * 2;
      h4 {
        margin: 0;
      }
      p {
        color: var(--fg-secondary);
      }
    }

    &__group {
      display: flex;
      flex-direction: column;
      width: 100%;
      gap: 12px;

      & label {
        width: fit-content;
        height: 14px;
        color: var(--fg-primary);
      }

      & input {
        display: flex;
        flex-direction: row;
        align-items: center;
        width: 100%;
        height: 24px;
        padding: 16px;
        background: var(--bg-accent-grey-2);
        color: var(--fg-primary);
        border: 1px solid var(--bg-opacity-20);
        border-radius: $border-radius;
        outline: 0;
        &:focus {
          border: 1px solid var(--bg-action);
        }
      }
    }

    &__footer {
      width: 100%;
      flex-direction: row;
      justify-content: flex-end;
      align-items: center;
      padding: $base-space * 2 0;
      border-bottom: 1px solid var(--bg-opacity-10);
      display: inline-flex;
      gap: $base-space;
    }
  }
}
</style>
