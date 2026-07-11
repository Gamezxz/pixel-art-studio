# Study: Dynamic attack canvas for long weapons

- **source**: two user-provided sprite-sheet examples · studied: 2026-07-11
- **true size**: 768x192 and 1536x4736 at 1x · **colors**: 31 / 127 (checkerboard included) · **palette saved as**: not saved
- **subject**: small chibi character locomotion and spear/polearm attack poses

## Measurements (from report.json)
- ramps: warm skin/brown ramps dominate the character; cool neutral ramps appear in weapon details
- outline: dark brown/purple selective outline; reported background colors are checkerboard, not art colors
- dithering: reported ~1.5% is largely checker/background interference, not a defining sprite technique
- value range: about 0.07–0.96; high separation between dark outline and pale skin

## Observations (from LOOKING at the supplied sheets)
- Normal movement poses occupy narrow compact cells close to the body's silhouette.
- Polearm poses use substantially wider transparent regions; weapon reach, not body width, determines the cell.
- The character remains aligned around a consistent ground/body anchor while transparent space expands left or right.
- Each attack sequence keeps a consistent frame footprint even though weapon reach changes between poses.
- Spear tips remain fully visible with breathing room; no frame trims tightly against the weapon extremity.

## Rules to apply (imperative — used when creating in this style)
- Choose canvas dimensions per action family, not one body-sized cell for the entire character.
- Compute the union bounds of character, complete weapon, anticipation, follow-through, and effects across all attack frames.
- Use that union plus a native-resolution safety margin as one fixed canvas for the complete attack sequence.
- Preserve the same feet/body pivot in every frame; add transparent padding asymmetrically when reach extends farther on one side.
- Keep idle/walk/run cells compact unless their actual silhouette requires expansion.
- Reject any export where an opaque weapon or effect pixel touches a canvas edge.

## Do NOT copy
- Do not treat the checkerboard preview as sprite pixels or palette colors.
- Do not center each frame independently; that creates visible jitter.
- Do not enlarge the character artwork itself merely because the canvas grows.

