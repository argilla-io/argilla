<template>
  <div class="loading">
    <div class="spinner">

      <svg width="57px" height="80px" viewBox="0 0 57 80" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
          <defs>
              <polygon id="path-1" points="0.252982353 0.168277311 53.6816471 0.168277311 53.6816471 79.2097353 0.252982353 79.2097353"></polygon>
              <polygon id="path-3" points="0 0.242536842 53.88005 0.242536842 53.88005 63.6754842 0 63.6754842"></polygon>
          </defs>
          <g id="RUBRIX" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
              <g id="Page-1">
                  <g id="blue" transform="translate(3.000000, 0.000000)">
                      <mask id="mask-2" fill="white">
                          <use xlink:href="#path-1"></use>
                      </mask>
                      <g id="Clip-2"></g>
                      <path d="M12.6881,36.4647353 L16.6376294,36.4647353 C28.4133353,36.4647353 34.3063941,32.1473403 34.3063941,23.5125504 C34.3063941,15.4217941 28.5764529,11.376416 17.1165706,11.376416 L12.6881,11.376416 L12.6881,36.4647353 Z M28.1669235,45.5284748 L53.6826882,79.2097353 L38.4676294,79.2097353 L14.9301,46.8536849 L12.6881,46.8536849 L12.6881,79.2097353 L0.252982353,79.2097353 L0.252982353,0.167928571 L14.8225118,0.167928571 C25.7132176,0.167928571 33.5775706,2.13133193 38.4155706,6.05465126 C43.7498647,10.4243571 46.4222176,16.1925084 46.4222176,23.3556176 C46.4222176,28.9563739 44.7459235,33.768979 41.4037471,37.7934328 C38.0615706,41.8213739 33.6469824,44.3985588 28.1669235,45.5284748 Z" id="Fill-1" fill="#0508D9" mask="url(#mask-2)"></path>
                  </g>
                  <g id="pink" transform="translate(0.000000, 11.000000)">
                      <mask id="mask-4" fill="white">
                          <use xlink:href="#path-3"></use>
                      </mask>
                      <g id="Clip-5"></g>
                      <path d="M34.34305,8.19727368 C34.34305,16.7981158 28.40355,21.0985368 16.52455,21.0985368 L12.54155,21.0985368 L12.54155,0.242536842 L-0.00245,0.242536842 L-0.00245,63.6754842 L12.54155,63.6754842 L12.54155,31.4501158 L14.80255,31.4501158 L38.53955,63.6754842 L53.88005,63.6754842 L28.14805,30.1266421 C33.67805,29.0011684 38.12655,26.4341158 41.50055,22.4220105 C44.87455,18.4133789 46.55805,13.6196947 46.55805,8.04443158 C46.55805,5.2238 46.12055,2.62895789 45.28055,0.242536842 L31.32605,0.242536842 C33.32805,2.19822105 34.34305,4.84516842 34.34305,8.19727368" id="Fill-4" fill="#F2067A" mask="url(#mask-4)"></path>
                  </g>
              </g>
          </g>
      </svg>
    </div>
  </div>
</template>

<script>
import "assets/icons/hipo";

export default {
  methods: {},
};
</script>

<style lang="scss" scoped>
.loading {
  background: $bg;
  height: 100vh;
  width: 100vw;
  z-index: 1;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}
#pink {
    animation: opacity 2.0s infinite ease-in-out;
}
.spinner {
    width: 57px;
    height: 80px;
    position: relative;
    margin: auto;
    text-align: center;
    display: flex;
    position: absolute;
    bottom: 0;
    top: 0;
    right: 0;
    left: 0;
    z-index: 9999;
    animation: sk-bounce 2.0s infinite ease-in-out;
    .icon {
        display: block;
        margin: auto;
        z-index: 1;
        fill: $secondary-lighter-color !important;
    }
}

.loading--content {
    @include media('>desktop') {
        left: 220px;
    }
}

.loading--inverse {
    &.spinner:after {
        background-color: #9ce4e1;
    }
    .icon {
        fill: $secondary-color;
    }
}

@keyframes sk-bounce {
    0%,
    100% {
        transform: scale(0.9);
    }
    50% {
        transform: scale(1.0);
    }
}

@keyframes opacity {
    0%,
    100% {
        opacity: 0
    }
    50% {
        opacity: 1
    }
}
</style>


