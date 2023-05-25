<template>
  <div class="markdown_editor">
    <textarea
      class="markdown_editor__input"
      v-model="markdown"
      :placeholder="placeholder"
      rows=9
    />

    <div class="markdown_editor__preview">
      <MarkdownElementComponent :markdown="markdown" />
    </div>

    <div class="markdown_editor__actions">
      <base-button @click="submit" class="markdown_editor__actions__save primary small">Save</base-button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    placeholder: {
      type: String,
      required: true,
    },
    value: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      markdown: this.value
    }
  },
  methods: {
    submit() {
      this.$emit('save')
    },
  },
}
</script>

<style lang="scss" scoped>

.markdown_editor {
  display: flex;
  flex-wrap: wrap;
  padding-bottom: 32px;

  &__input {
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 5px;
    width: 100%;

    @include media(">desktop") {
      width: 50%;
    }
  }

  &__preview {
    width: 100%;

    @include media(">desktop") {
      padding-left: 20px;
      width: 50%;
    }
  }

  &__actions {
    padding-top: 20px;
    width: 100%;

    &__save {
      float: right;
    }
  }
}

</style>
