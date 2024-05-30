<template>
  <span>
    <svg
      class="deco--top"
      width="381"
      height="273"
      viewBox="0 0 381 273"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M49.4543 168.671C131.001 283.218 286.601 306.073 397.175 219.655L397.175 -6.04227C214.413 -6.04227 1.68281 -6.04227 1.68281 -6.04227C-2.99505 54.3839 12.3499 116.551 49.4543 168.671Z"
        fill="url(#paint0_linear_4458_4403)"
      />
      <defs>
        <linearGradient
          id="paint0_linear_4458_4403"
          x1="176.672"
          y1="264.361"
          x2="219.437"
          y2="-31.7149"
          gradientUnits="userSpaceOnUse"
        >
          <stop stop-color="#FFB097" />
          <stop offset="1" stop-color="#F73D3D" />
        </linearGradient>
      </defs>
    </svg>

    <svg
      class="deco--center"
      width="543"
      height="420"
      viewBox="0 0 543 420"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g clip-path="url(#clip0_5185_2603)">
        <path
          d="M481.316 122.082C398.97 39.7831 265.575 39.4794 183.228 121.475L61.6838 0C-20.3587 82.2993 -20.3587 215.618 61.9877 297.918C144.334 380.217 277.729 380.217 360.076 298.221L481.62 419.696C563.663 337.701 563.663 204.382 481.316 122.082Z"
          fill="url(#paint0_linear_5185_2603)"
        />
      </g>
      <defs>
        <linearGradient
          id="paint0_linear_5185_2603"
          x1="271.652"
          y1="0"
          x2="271.652"
          y2="419.696"
          gradientUnits="userSpaceOnUse"
        >
          <stop stop-color="#FFB097" />
          <stop offset="1" stop-color="#F73D3D" />
        </linearGradient>
        <clipPath id="clip0_5185_2603">
          <rect width="543" height="420" fill="white" />
        </clipPath>
      </defs>
    </svg>

    <svg
      class="deco--bottom"
      width="446"
      height="255"
      viewBox="0 0 446 255"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M382.271 78.1171C297.195 -5.55388 159.378 -5.86263 74.3021 77.4996L-4.00006 0.490662L-4.00006 256.883H444.363C452.587 193.414 431.911 126.937 382.271 78.1171Z"
        fill="url(#paint0_linear_4458_4645)"
      />
      <defs>
        <linearGradient
          id="paint0_linear_4458_4645"
          x1="221.059"
          y1="0.490662"
          x2="221.059"
          y2="256.883"
          gradientUnits="userSpaceOnUse"
        >
          <stop stop-color="#FFB097" />
          <stop offset="1" stop-color="#F73D3D" />
        </linearGradient>
      </defs>
    </svg>
  </span>
</template>

<style lang="scss" scoped>
%deco {
  display: none;
  @include media(">desktop") {
    display: block;
    position: absolute;
    height: auto;
  }
}
.deco {
  &--top {
    top: 0;
    right: 0;
    width: max(300px, 30%);
    @extend %deco;
  }
  &--center {
    bottom: 0;
    top: 0;
    left: 0;
    right: 0;
    width: max(400px, 50%);
    margin: auto;
    @extend %deco;
  }
  &--bottom {
    bottom: 0;
    left: 0;
    width: max(200px, 34%);
    @extend %deco;
  }
}
</style>