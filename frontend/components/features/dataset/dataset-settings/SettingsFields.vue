<template>
  <div class="settings-fields__container">
    <div class="settings-fields__edition-form">
      <h2 class="--heading5 --medium">Edit fields</h2>
      <div v-for="field in settings.fields" :key="field.id">
        <form
          @submit.prevent="onSubmit(field)"
          class="settings-fields__edition-form-fields"
        >
          <div
            class="settings-fields__edition-form-name"
            v-optional-field="!field.required"
          >
            <h4 class="--body1 --medium --capitalized" v-text="field.name" />
          </div>
          <div class="settings-fields__edition-form-group">
            <label for="field.id">Title</label>
            <input type="type" id="field.id" v-model="field.title" />
            <template v-if="!field.isTitleValid">
              <span
                class="--validation"
                v-for="validation in field.validate().title"
                :key="validation"
                v-html="validation"
              />
            </template>
          </div>

          <BaseSwitch v-model="field.settings.use_markdown"
            >Use Markdown</BaseSwitch
          >

          <div class="settings-fields__edition-form-footer">
            <BaseButton
              type="button"
              class="secondary light small"
              @on-click="restore(field)"
              :disabled="!field.isModified"
            >
              <span v-text="'Cancel'" />
            </BaseButton>
            <BaseButton
              type="submit"
              class="primary small"
              :disabled="!field.isModified || !field.isFieldValid"
            >
              <span v-text="'Update'" />
            </BaseButton>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { useSettingsFieldsViewModel } from "./useSettingsFieldsViewModel";

export default {
  name: "SettingsFields",
  props: {
    settings: {
      type: Object,
      required: true,
    },
  },
  methods: {
    onSubmit(field) {
      this.update(field);
    },
  },
  setup() {
    return useSettingsFieldsViewModel();
  },
};
</script>
<style lang="scss" scoped>
.settings-fields {
  &__container {
    display: flex;
    gap: $base-space * 4;
    height: 100%;
    max-width: 1000px;
    flex-wrap: wrap;
    min-height: 0;
  }

  &__edition-form {
    display: flex;
    flex: 1;
    flex-direction: column;
    gap: $base-space * 2;
    height: 100%;
    overflow: auto;
    padding-right: $base-space * 2;

    &-fields {
      display: flex;
      flex-direction: column;
      gap: $base-space * 2;
    }

    &-name {
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
    }

    &-group {
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
        box-sizing: border-box;
        display: flex;
        flex-direction: row;
        align-items: center;
        height: 24px;
        padding: 16px;
        background: #ffffff;
        border: 1px solid rgba(0, 0, 0, 0.2);
        border-radius: 5px;
      }
    }

    &-footer {
      width: 100%;
      display: flex;
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
.--validation {
  color: red;
}
</style>
