<template>
  <div class="text_field_component" :key="fieldText">
    <div class="title-area --body2">
      <span class="text_field_component__title-content" v-text="title" />
      <BaseActionTooltip
        class="text_field_component__tooltip"
        tooltip="Copied"
        tooltip-position="left"
      >
        <BaseButton
          title="Copy to clipboard"
          class="text_field_component__copy-button"
          @click.prevent="$copyToClipboard(fieldText)"
        >
          <svgicon color="#acacac" name="copy" width="18" height="18" />
        </BaseButton>
      </BaseActionTooltip>
    </div>
    <div :id="`fields-content-${name}`" class="content-area --body1">
      <div :class="classes" v-if="!useMarkdown" v-html="fieldText" />
      <Sandbox v-else :fieldText="example2" :record="record" />
      <template>
        <style :key="name" scoped>
          ::highlight(search-text-highlight-{{name}}) {
            color: #ff675f;
          }
        </style>
      </template>
    </div>
  </div>
</template>

<script>
import { useTextFieldViewModel } from "./useTextFieldViewModel";

export default {
  name: "TextFieldComponent",
  props: {
    name: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    searchText: {
      type: String,
      default: "",
    },
    fieldText: {
      type: String,
      required: true,
    },
    useMarkdown: {
      type: Boolean,
      default: false,
    },
    record: {
      type: Object,
    },
  },
  data() {
    return {
      example1: `<link href="https://cdn.jsdelivr.net/npm/flowbite@2.4.1/dist/flowbite.min.css" rel="stylesheet" />
<style>
    body {
      background-color: #E20074
    }

    .bg-telekom-magenta {
        background-color: #E20074
    }
</style>

<div class="flex-1 p:2 sm:p-6 justify-between flex flex-col">
<div id="messages" class="flex flex-col space-y-4 p-3 overflow-y-auto scrollbar-thumb-blue scrollbar-thumb-rounded scrollbar-track-blue-lighter scrollbar-w-2 scrolling-touch">
<div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

<div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

      <div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

      <div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

      <div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

      <div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

      <div class="chat-message">
         <div class="flex items-end ">
            <div class="flex flex-col space-y-2 text-xs max-w-xs mx-2 order-2 items-start">
               <div><span class="px-4 py-2 rounded-lg inline-block rounded-bl-none bg-gray-300 text-gray-600">Bereitstellung</span></div>
            </div>
            <img src="https://img.daisyui.com/images/stock/photo-1534528741775-53994a69daeb.webp" alt="My profile" class="w-6 h-6 rounded-full order-1">
         </div>
      </div>

</div>
</div>

<h2 class="ml-2">Vue JS</h2>

<script src="https://unpkg.com/vue@3/dist/vue.global.js"><\/script>

<div id="app">
  <p class="ml-2">{{ message }}</p>

  <input type="text" v-model="message" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="John" required />

  <br />

  <button class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800" @click="counter++">+</button>

  {{counter}}

  <button type="button" class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800" @click="counter--">-</button>

  <h3>Data</h3>

  {{ JSON.stringify(fromOutside) }}
</div>

<script>
  const { createApp, ref } = Vue

  createApp({
    setup() {
      const message = ref('Hello vue!')
      const counter = ref(0)
      const fromOutside = ref("NONE")

      window.addEventListener('message', ({data})=>  {
        fromOutside.value = JSON.parse(data);
      });

      return {
        message,
        counter,
        fromOutside
      }
    }
  }).mount('#app')
<\/script>
`,

      example2: `


		<style>
			body {
				background-color: #bfe3dd;
				color: #000;
			}

			a {
				color: #2983ff;
			}
		</style>

		<div id="container"></div>

		<div id="info">
			<a href="https://threejs.org" target="_blank" rel="noopener">three.js</a> webgl - animation - keyframes<br/>
			Model: <a href="https://artstation.com/artwork/1AGwX" target="_blank" rel="noopener">Littlest Tokyo</a> by
			<a href="https://artstation.com/glenatron" target="_blank" rel="noopener">Glen Fox</a>, CC Attribution.
		</div>

<script type="importmap">
  {
    "imports": {
      "three": "https://cdn.jsdelivr.net/npm/three@latest/build/three.module.js",
      "three/addons/": "https://cdn.jsdelivr.net/npm/three@latest/examples/jsm/"
    }
  }
<\/script>

<script type="module">

			import * as THREE from 'three';

			import Stats from 'three/addons/libs/stats.module.js';

			import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
			import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

			import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
			import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

			let mixer;

			const clock = new THREE.Clock();
			const container = document.getElementById( 'container' );

			const stats = new Stats();
			container.appendChild( stats.dom );

			const renderer = new THREE.WebGLRenderer( { antialias: true } );
			renderer.setPixelRatio( window.devicePixelRatio );
			renderer.setSize( window.innerWidth, window.innerHeight );
			container.appendChild( renderer.domElement );

			const pmremGenerator = new THREE.PMREMGenerator( renderer );

			const scene = new THREE.Scene();
			scene.background = new THREE.Color( 0xbfe3dd );
			scene.environment = pmremGenerator.fromScene( new RoomEnvironment( renderer ), 0.04 ).texture;

			const camera = new THREE.PerspectiveCamera( 40, window.innerWidth / window.innerHeight, 1, 100 );
			camera.position.set( 5, 2, 8 );

			const controls = new OrbitControls( camera, renderer.domElement );
			controls.target.set( 0, 0.5, 0 );
			controls.update();
			controls.enablePan = false;
			controls.enableDamping = true;

			const dracoLoader = new DRACOLoader();
			dracoLoader.setDecoderPath( ' http://localhost:8081/jsm/libs/draco/gltf/' );

			const loader = new GLTFLoader();
			loader.setDRACOLoader( dracoLoader );
			loader.load( ' http://localhost:8080/models/gltf/LittlestTokyo.glb', function ( gltf ) {

				const model = gltf.scene;
				model.position.set( 1, 1, 0 );
				model.scale.set( 0.01, 0.01, 0.01 );
				scene.add( model );

				mixer = new THREE.AnimationMixer( model );
				mixer.clipAction( gltf.animations[ 0 ] ).play();

				renderer.setAnimationLoop( animate );

			}, undefined, function ( e ) {

				console.error( e );

			} );


			window.onresize = function () {

				camera.aspect = window.innerWidth / window.innerHeight;
				camera.updateProjectionMatrix();

				renderer.setSize( window.innerWidth, window.innerHeight );

			};


			function animate() {

				const delta = clock.getDelta();

				mixer.update( delta );

				controls.update();

				stats.update();

				renderer.render( scene, camera );

			}


		<\/script>




`,
    };
  },
  computed: {
    classes() {
      return this.$language.isRTL(this.fieldText) ? "--rtl" : "--ltr";
    },
  },
  setup(props) {
    return useTextFieldViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.text_field_component {
  $this: &;
  display: flex;
  flex-direction: column;
  gap: $base-space;
  padding: 2 * $base-space;
  background: palette(grey, 800);
  border-radius: $border-radius-m;
  &:hover {
    #{$this}__copy-button {
      opacity: 1;
    }
  }
  .title-area {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: $base-space;
    color: $black-87;
  }
  .content-area {
    white-space: pre-wrap;
    word-break: break-word;
  }
  &__title-content {
    word-break: break-word;
    width: calc(100% - 30px);
  }
  &__tooltip {
    display: flex;
    align-self: flex-start;
  }
  &__copy-button {
    flex-shrink: 0;
    padding: 0;
    opacity: 0;
  }
}
.fade-enter-active,
.fade-leave-active {
  transition: all 0.25s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
