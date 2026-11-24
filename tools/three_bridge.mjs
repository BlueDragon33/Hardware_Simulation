// Bundle Three.js from the pinned npm package into a self-contained browser global.
// Historical prototype expects window.THREE. No runtime network dependency.
import * as THREE from 'three';
window.THREE = THREE;
