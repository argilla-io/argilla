<template>
  <div class="view-mode">
    <p class="view-mode__text">{{annotationMode ? 'Turn off annotation mode' : 'Turn on annotation mode'}}</p>
    <ReButton :class="['view-mode__button', annotationMode ? '--on' : '']" @click="$emit('onChangeMode')">
      <svgicon class="view-mode__icon" name='editable' width="30" height="30" color="#ffffff"></svgicon>
    </ReButton>
  </div>
</template>

<script>
import 'assets/icons/editable';
export default {
  data: () => {
    return {
      allow: false,
    }
  },
  props: {
    annotationMode: {
      type: Boolean,
      default: false,
    }
  },
}
</script>

<style lang="scss" scoped>
$size: 50px;
.view-mode {
  position: fixed;
  bottom: 1em;
  right: 3em;
  &:hover {
    .view-mode__text {
      display: block;
    }
  }
  &__button {
    cursor: pointer;
    outline: none;
    height: $size;
    width: $size;
    border-radius: 50%;
    border: none;
    background: lighten($neutral-color, 30%);
    display: flex;
    text-align: center;
    margin: auto;
    &.--on {
      background: $primary-color;
      &:hover {
        background: darken($primary-color, 10%);
      }
    }
    &:hover {
      background: lighten($neutral-color, 20%);
    }
  }
  &__icon {
    margin: auto;
  }
  &__text {
    display: none;
    color: $lighter-color;
    background: lighten($neutral-color, 30%);
    position: absolute;
    bottom: 50px;
    right: 50%;
    transform: translateX(50%);
    width: 120px;
    text-align: center;
    border-radius: 3px;
    padding: 0.5em;
    @include font-size(12px);
  }
}
</style>


