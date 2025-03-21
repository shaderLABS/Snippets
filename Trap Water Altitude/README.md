# Trap Water Altitude
> by SpacEagle17

This shader snippet provides a custom uniform to record the altitude of water bodies. The recorded altitude:

- Defaults to 61.9 when exiting water, entering from a cave, or during shader reload
- Maintains the entered altitude value until the player exits the water
- Uses a smooth transition technique to capture the eye altitude while in water

The code should be added to your `shaders.properties` file. Then, to use this functionality, declare the uniform in your shader program like this:
```glsl
uniform float waterAltitude = 61.9; // Tracks the altitude of water bodies, with default value for fallback
```
Works on Iris and OptiFine  
Special thanks to Xonk for the large number smooth() trick used to record values.

> Used in Euphoria Patches to progressively darken water as the player descends deeper

For more information about custom uniforms, visit the [shaders.properties documentation](https://shaders.properties/current/reference/shadersproperties/custom_uniforms/).