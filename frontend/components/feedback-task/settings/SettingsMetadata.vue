<template>
  <div class="settings__container">
    <div class="settings__edition-form">
      <h2 class="--heading5 --medium" v-text="$t('settings.editMetadata')" />
      <div v-for="metadata in settings.metadataProperties" :key="metadata.id">
        <form
          @submit.prevent="updateMetadata(metadata)"
          class="settings__edition-form__metadata"
        >
          <div class="settings__edition-form__name">
            <h4 class="--body1 --medium" v-text="metadata.name" />
            <BaseBadge class="--capitalized" :text="metadata.settings.type" />
          </div>

          <Validation
            :validations="metadata.validate().title"
            class="settings__edition-form__group"
          >
            <label for="metadata.title" v-text="$t('title')" />
            <input type="text" id="metadata.title" v-model="metadata.title" />
          </Validation>

          <BaseSwitch v-model="metadata.visibleForAnnotators">{{
            $t("visibleForAnnotators")
          }}</BaseSwitch>

          <div class="settings__edition-form__footer">
            <BaseButton
              type="button"
              class="secondary light small"
              @on-click="restore(metadata)"
              :disabled="!metadata.isModified"
            >
              <span v-text="$t('cancel')" />
            </BaseButton>
            <BaseButton
              type="submit"
              class="primary small"
              :disabled="!metadata.isModified || !metadata.isValid"
            >
              <span v-text="$t('update')" />
            </BaseButton>
          </div>
        </form>
      </div>

      <h2 class="--heading5 --medium" v-text="$t('extraMetadata')" />
      <form
        @submit.prevent="updateDataset(settings.dataset)"
        class="settings__edition-form__metadata"
      >
        <BaseSwitch v-model="settings.dataset.allowExtraMetadata">{{
          $t("allowExtraMetadata")
        }}</BaseSwitch>
        <div class="settings__edition-form__footer">
          <BaseButton
            type="button"
            class="secondary light small"
            @on-click="settings.dataset.restore()"
            :disabled="!settings.dataset.isModified"
          >
            <span v-text="$t('cancel')" />
          </BaseButton>
          <BaseButton
            type="submit"
            class="primary small"
            :disabled="!settings.dataset.isModified"
          >
            <span v-text="$t('update')" />
          </BaseButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { useSettingsMetadataViewModel } from "./useSettingsMetadataViewModel";

export default {
  name: "SettingsMetadata",
  props: {
    settings: {
      type: Object,
      required: true,
    },
  },
  setup() {
    return useSettingsMetadataViewModel();
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
    max-width: 1000px;
    padding-top: $base-space;

    &__metadata {
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
        color: $black-54;
      }
      .badge {
        margin-inline: 0 auto;
      }
    }

    &__group {
      display: flex;
      flex-direction: column;
      width: 100%;
      gap: $base-space;

      & label {
        width: fit-content;
        height: 14px;
        color: $black-54;
      }

      & input {
        display: flex;
        flex-direction: row;
        align-items: center;
        width: 100%;
        height: 24px;
        padding: 16px;
        background: palette(white);
        border: 1px solid $black-20;
        border-radius: $border-radius;
        outline: 0;
        &:focus {
          border: 1px solid $primary-color;
        }
      }
    }

    &__footer {
      width: 100%;
      flex-direction: row;
      justify-content: flex-end;
      align-items: center;
      padding: $base-space * 2 0;
      border-bottom: 1px solid $black-10;
      display: inline-flex;
      gap: $base-space;
    }
  }
}
</style>
