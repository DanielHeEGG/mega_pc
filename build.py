import gdsfactory as gf
import gfelib as gl
import sys
import argparse

parser = argparse.ArgumentParser(description="Build script for MEGA-PC")
parser.add_argument(
    "--nomerge",
    action="store_true",
    help="Don't merge the device patterns (e.g. release holes), because it can be very slow",
)
parser.add_argument(
    "--show",
    action="store_true",
    help="Show the last pattern with KLayout",
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

d = device()

d.write_gds("./build/mega_pc_SOURCE.gds")

c = gf.Component(name="chip")

if not args.nomerge:
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
    operation="-",
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

c.write_gds("./build/mega_pc_BUILD.gds")

if args.show:
    c.show()
