# Commonly used footprints
*NOTE: This project was originally for use in APRL*

This repo contains a set of common libraries to use with KiCAD for clubs such as APRL (Aggie Propulsion & Rocketry Lab). It contains common footprints and their symbols.

## Usage
Simply use git submodules to add this repo. I'd recommend adding a subdirectory to your project called "external", then adding the submodule there. This is because I used the following convention to embed 3D models:
`${KIPRJMOD}/external/APRLPrints/external/footprint/packages3d/CRYSTAL-SMD_4P-L3.2-W2.5-BL-2.step`
If you choose to use another path, then you will have to adjust this manually to get a complete 3D render.

The correct command might look like:
```bash
git submodule add -- https://github.com/npgo22/APRLPrints.git external/APRLPrints
```

## Obtaining 3D Models
To get 3D models, you can use: 
```bash
JLC2KiCadLib -dir external --no_symbol C<Part number>
```
Just be sure to not include anything other than .step files in this repo. We wouldn't want people to accidentally use LCSC/JLCPCB's/Ultralibrarian's actual footprints, as they are terrible.

## Requirements:
Everything **MUST** be in accordance with JLCPCB standards. Most importantly, this means keeping a silkscreen distance of 0.2mm away from the pads. This is why this library exists: this constraint is completely violated with stock KiCAD footprints.


## Footprint list:

| Name    | L.P. Creator  | Description                                                   |
|---------|----------|---------------------------------------------------------------|
| 3225-4P | Akoustis | A common footprint for 4 pad crystal oscillators. Very compact. |
| ARPL_Logo | Daniel & Co. | The APRL logo. Slightly cleaned up and aligned as to not trigger DRC. |
| {R,C,L,LED}_0402 |Worthington | "The perfect 0402" |
| {R,C,L,LED}_0603 |Worthington | "The perfect 0603" |
| {R,C,L}_0805 |Worthington | "The perfect 0805" |
| SOD323 | Nolan | An SOD-323 footprint which uses larger pads. |