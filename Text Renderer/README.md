## GLSL Debug Text Renderer
> by SixthSurge

Character set based on Monocraft by IdreesInc
https://github.com/IdreesInc/Monocraft

With additional characters added by WoMspace

### Usage
```glsl
// Call beginText to initialize the text renderer. You can scale the fragment position to adjust the size of the text
beginText(ivec2(gl_FragCoord.xy), ivec2(0, viewHeight));
        ^ fragment position     ^ text box position (upper left corner)

// You can print various data types
printBool(false);
printFloat(sqrt(-1.0)); // Prints "NaN"
printInt(42);
printVec3(skyColor);

// ...or arbitrarily long strings
printString((_H, _e, _l, _l, _o, _comma, _space, _w, _o, _r, _l, _d));

// To start a new line, use
printLine();

// You can also configure the text color on the fly
text.fgCol = vec4(1.0, 0.0, 0.0, 1.0);
text.bgCol = vec4(0.0, 0.0, 0.0, 1.0);

// ...as well as the number base and number of decimal places to print
text.base = 16;
text.fpPrecision = 4;

// Finally, call endText to blend the current fragment color with the text
endText(fragColor);
```

**Important**: any variables you display must be the same for all fragments, or
at least all of the fragments that the text covers. Otherwise, different
fragments will try to print different values, resulting in, well, a mess.
