import gdsfactory as gf
import gfebuild as gb
import gfelib as gl
import sys
import datetime
import argparse

parser = argparse.ArgumentParser(description="Build script for MEGA-PC")
parser.add_argument(
    "--no-merge",
    action="store_true",
    help="Don't merge the device patterns (e.g. release holes), because it can be very slow",
)
parser.add_argument(
    "--mirror",
    action="store_true",
    help="Write additional ASML reticle files that are mirrored across x=0 (PLACEMENTS file is not mirrored)",
)
parser.add_argument(
    "--show",
    action="store_true",
    help="Show the last pattern with KLayout",
)
parser.add_argument(
    "--version",
    action="store",
    type=str,
    help="Add version number text",
    required=True,
)
parser.add_argument(
    "--hash",
    action="store",
    type=str,
    help="Add hash text",
    default="",
)


args = parser.parse_args()


gf.clear_cache()

from pdk import LAYERS, PDK
from device import device, CHIP_SIZE, CAVITY_WIDTH

PDK.activate()

CHIP_RECT = gf.components.rectangle(
    size=(CHIP_SIZE, CHIP_SIZE),
    layer=LAYERS.DUMMY,
    centered=True,
)

d = device(version=args.version, hash=args.hash)

d.write_gds(f"./build/mega_pc_{args.version}_SOURCE.gds")

c = gf.Component(name="chip")

if not args.no_merge:
    # DEVICE merged
    _ = c << gf.boolean(
        A=gf.boolean(
            A=CHIP_RECT,
            B=d,
            operation="-",
            layer=LAYERS.DUMMY,
            layer1=LAYERS.DUMMY,
            layer2=LAYERS.DEVICE,
        ),
        B=d,
        operation="|",
        layer=LAYERS.DEVICE_REMOVE,
        layer1=LAYERS.DUMMY,
        layer2=LAYERS.DEVICE_REMOVE,
    )
else:
    # DEVICE and DEVICE_REMOVE not merged
    _ = c << d.extract(layers=[LAYERS.DEVICE, LAYERS.DEVICE_REMOVE])

# HANDLE
handle = gf.Component()

for i in range(7, -1, -1):
    handle = gf.boolean(
        A=handle,
        B=d,
        operation="-",
        layer=LAYERS.DUMMY,
        layer1=LAYERS.DUMMY,
        layer2=(LAYERS.HANDLE_P0[0], i),
    )

    exp = gf.boolean(
        A=gf.Component(),
        B=d,
        operation="|",
        layer=LAYERS.DUMMY,
        layer1=LAYERS.DUMMY,
        layer2=(LAYERS.HANDLE_P0[0], i),
    )
    exp.offset(layer=LAYERS.DUMMY, distance=CAVITY_WIDTH)

    border = gf.boolean(
        A=exp,
        B=d,
        operation="-",
        layer=LAYERS.DUMMY,
        layer1=LAYERS.DUMMY,
        layer2=(LAYERS.HANDLE_P0[0], i),
    )

    handle = gf.boolean(
        A=handle,
        B=border,
        operation="|",
        layer=LAYERS.DUMMY,
        layer1=LAYERS.DUMMY,
        layer2=LAYERS.DUMMY,
    )

_ = c << gf.boolean(
    A=handle,
    B=d,
    operation="|",
    layer=LAYERS.HANDLE_REMOVE,
    layer1=LAYERS.DUMMY,
    layer2=LAYERS.HANDLE_REMOVE,
)


# POSITIVE LAYERS
for layer in [
    LAYERS.VIAS_ETCH,
    LAYERS.CAP_TRENCH_ETCH,
    LAYERS.CAP_BACKSIDE,
]:
    _ = c << gf.boolean(
        A=CHIP_RECT,
        B=d,
        operation="&",
        layer=layer,
        layer1=LAYERS.DUMMY,
        layer2=layer,
    )

# NEGATIVE LAYERS
for layer in [
    LAYERS.POLY,
    LAYERS.OXIDE,
    LAYERS.NITRIDE,
    LAYERS.CAP_OXIDE,
    LAYERS.CAP_NITRIDE,
]:
    _ = c << gf.boolean(
        A=CHIP_RECT,
        B=d,
        operation="-",
        layer=layer,
        layer1=LAYERS.DUMMY,
        layer2=layer,
    )

c.flatten()
c.write_gds(f"./build/mega_pc_{args.version}_BUILD.gds")

reticles, placements = gb.asml300.reticle(
    component=c,
    image_size=(CHIP_SIZE, CHIP_SIZE),
    image_layers=[
        LAYERS.VIAS_ETCH,
        LAYERS.POLY,
        LAYERS.OXIDE,
        LAYERS.NITRIDE,
        LAYERS.DEVICE_REMOVE,
        LAYERS.CAP_OXIDE,
        LAYERS.CAP_NITRIDE,
        LAYERS.CAP_TRENCH_ETCH,
    ],
    id=f"MPC-{args.version}",
    text=str(datetime.date.today()),
)

for i, reticle in enumerate(reticles):
    reticle.write_gds(f"./build/mega_pc_{args.version}_BUILD_ASML_{i}.gds")

    if args.mirror:
        reticle.mirror_x(0)
        reticle.write_gds(f"./build/mega_pc_{args.version}_BUILD_ASML_{i}_MIRROR.gds")

with open(f"./build/mega_pc_{args.version}_BUILD_ASML_PLACEMENTS.txt", "w") as f:
    for key, value in placements.items():
        f.write(f"{LAYERS(key)}: R {value[0]}, CX {value[1]:.2f}, CY {value[2]:.2f}\n")

if args.show:
    c.show()
