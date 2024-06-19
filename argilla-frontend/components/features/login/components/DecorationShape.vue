<template>
  <svg
    class="deco--bottom"
    width="771"
    height="464"
    viewBox="0 0 771 464"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <ellipse
      cx="79.5"
      cy="77.5"
      rx="79.5"
      ry="77.5"
      transform="matrix(-1 0 0 1 515 142)"
      fill="url(#paint0_linear_5498_324)"
      fill-opacity="0.8"
    />
    <path
      d="M709.445 146.303C698.068 201.929 638.806 236.924 576.896 224.447C514.985 211.971 473.903 156.755 484.958 101.063L709.445 146.303Z"
      fill="url(#paint1_linear_5498_324)"
    />
    <path
      d="M730.352 46.0295C718.975 101.656 659.713 136.651 597.802 124.174C535.892 111.698 494.81 56.4815 505.865 0.790103L730.352 46.0295Z"
      fill="url(#paint2_linear_5498_324)"
    />
    <path
      d="M752.559 330.202C716.44 390.212 638.651 409.697 578.718 373.7L525.406 462.276C465.607 426.058 446.282 348.152 482.4 288.141C518.519 228.13 596.352 208.824 656.285 244.82L709.597 156.244C769.352 192.285 788.677 270.191 752.559 330.202Z"
      fill="#FF675F"
    />
    <path
      d="M181.513 364.13C181.513 418.886 225.902 463.274 280.658 463.274C335.414 463.274 379.802 418.886 379.802 364.13C379.802 309.374 335.414 264.986 280.658 264.986C225.902 264.986 181.513 309.374 181.513 364.13Z"
      fill="url(#paint3_linear_5498_324)"
    />
    <path
      d="M183.408 349.102C168.98 381.915 130.381 396.663 97.0533 382.115C63.7256 367.566 48.3363 329.147 62.5518 296.343L183.408 349.102Z"
      fill="url(#paint4_linear_5498_324)"
      fill-opacity="0.9"
    />
    <path
      d="M-2.74348e-05 409.436C14.4286 376.623 53.0274 361.874 86.3551 376.423C119.683 390.972 135.072 429.391 120.857 462.194L-2.74348e-05 409.436Z"
      fill="url(#paint5_linear_5498_324)"
      fill-opacity="0.9"
    />
    <path
      d="M495.862 457.741C452.044 474.614 402.702 452.418 385.457 408.097C368.212 363.776 389.714 314.082 433.326 297.02L495.862 457.741Z"
      fill="url(#paint6_linear_5498_324)"
    />
    <defs>
      <linearGradient
        id="paint0_linear_5498_324"
        x1="-28.8223"
        y1="59.9977"
        x2="122.512"
        y2="271.388"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint1_linear_5498_324"
        x1="742.278"
        y1="193.508"
        x2="642.695"
        y2="368.536"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint2_linear_5498_324"
        x1="763.185"
        y1="93.2343"
        x2="663.602"
        y2="268.263"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint3_linear_5498_324"
        x1="415.747"
        y1="341.74"
        x2="220.608"
        y2="607.46"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint4_linear_5498_324"
        x1="106"
        y1="398.838"
        x2="79.194"
        y2="249.951"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint5_linear_5498_324"
        x1="69.3754"
        y1="452.539"
        x2="42.569"
        y2="303.651"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
      <linearGradient
        id="paint6_linear_5498_324"
        x1="471.878"
        y1="353.664"
        x2="358.537"
        y2="516.005"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0.0151877" stop-color="#FF675F" />
        <stop offset="1" stop-color="#F73D3D" />
      </linearGradient>
    </defs>
  </svg>
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
  &--bottom {
    right: 0;
    bottom: 0;
    width: clamp(560px, 70%, 800px);
    @extend %deco;
  }
}
</style>
