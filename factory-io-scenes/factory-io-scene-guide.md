# SmartLine 360 — Factory I/O Scene Build Guide

Custom 3-station scene: **Infeed & Color Sorting → Assembly → Packaging & Palletizing**

> ✅ Verified against the official Factory I/O manual (docs.factoryio.com).
> Corrections from the earlier draft are marked with a ⚠️ note where relevant.

---

## Palette cheat-sheet

Factory I/O's Palette is organized into these categories. Knowing this up
front saves you from hunting for a part in the wrong place:

| Category | What's in it |
| --- | --- |
| **Heavy Load Parts** | Roller conveyors, curves, turntables — for boxes/pallets |
| **Light Load Parts** | Belt conveyors, **Pusher**, **Positioning Bars**, Stop Blade — for small/light items |
| **Sensors** | Diffuse, Retroreflective, Inductive, Capacitive, Vision, RFID, Light Array |
| **Operators** ⚠️ | Control-panel hardware only — E-Stop, push buttons, indicators, selectors. **Not actuators like the Pusher.** |
| **Stations** | Machining Center, Elevator, Pick & Place, **Two-Axis Pick & Place**, Palletizer, Stacker Crane & Rack, Tank |
| **Items** | Boxes, Pallets, Stackable Box, Raw Material, Product Lid, Product Base, Final Product |
| **Emitter / Remover** ⚠️ | Not in the original guide at all — but **required**. The Emitter spawns items into the scene; without one, nothing will ever appear on your conveyors. The Remover deletes items at the end of a line so they don't pile up. |

**Colors:** Raw Material, Product Lid, and Product Base come in **Blue,
Green, or Metal** — not literally "Red." The Vision Sensor detects these
three item types and their colors specifically; it does not detect plain
Boxes. Keep this in mind for Station 1.

---

## Step 0: Setup

1. Open Factory I/O.
2. **File → New** (or `Ctrl+N`) to create an empty scene.
3. Confirm you're in **Edit Mode** — the Play button (`F5`) toggles between
   Edit and Run mode. In Edit Mode you place and arrange parts; in Run Mode
   the scene simulates in real time.
4. The **Palette** panel should be visible; use its category dropdown to
   filter parts, or the search box to find one by name.

**Useful controls while building:**
- Drag a part from the Palette into the 3D view to place it.
- Left-click and drag a placed part to move it (hold `V` while dragging to move it vertically instead of horizontally).
- Press `Y` to Yaw (rotate around the vertical axis) — most parts only rotate in 90° steps; sensors rotate freely.
- A part outlined in **red** is intersecting another part and will be deleted when you enter Run Mode — fix its position first.

---

## Station 1: Infeed & Color Sorting

**Goal:** spawn colored items, detect them, and divert them onto separate lanes by color.

**Step 1 — Add an Emitter (the item source)**
1. From the **Emitter** section of the Palette, drag an **Emitter** to the start of your layout.
2. Right-click it → **Configuration**, and set it to emit **Raw Material**. You can set it to cycle through Blue/Green/Metal, or fix it to one color per emitter if you want dedicated lanes per color later.

**Step 2 — Build the main conveyor line**
1. From **Heavy Load Parts**, drag a **Roller Conveyor (2m)** so its infeed end sits right at the Emitter's output.
2. Right-click → rotate (`Y`) if you need to change its direction.

**Step 3 — Add presence detection**
1. From **Sensors**, drag a **Diffuse Sensor** near the start of the conveyor, aimed across it.
2. This gives a simple Boolean "item present" signal — useful for triggering downstream logic or counting items.

**Step 4 — Add color detection**
1. From **Sensors**, drag a **Vision Sensor** and place it further down the conveyor, after the Diffuse Sensor.
2. Right-click → **Configuration**, and choose what it reports — e.g. per-color Boolean outputs (Blue Raw / Green Raw / Metal Raw) or a single "All ID" numerical output. This is what your PLC will read to know each item's color.

**Step 5 — Build the diverting mechanism**
1. From **Light Load Parts** ⚠️ (not Operators), drag a **Pusher** and place it across from the Vision Sensor.
2. Position it so extending pushes items off the main conveyor onto a side lane. For sorting into more than one color, you'll want one Pusher per diverted lane, each keyed to a different color signal from the Vision Sensor.
3. From **Heavy Load Parts**, drag additional **Roller Conveyors**, placed perpendicular to the main line at each Pusher, as the diverted lanes.

**Step 6 — Remove finished items**
1. From the **Remover** section, drop a **Remover** at the end of each lane so items disappear instead of piling up (Factory I/O scenes cap out around 500 items).

**Step 7 — Test the layout**
1. Press `F5` to enter Run Mode.
2. Confirm items spawn, travel, get detected, and divert correctly.
3. Any part with a red outline needs repositioning before it will work in Run Mode.

---

## Station 2: Assembly

**Goal:** assemble a Product Base and a Product Lid into a Final Product, then quality-check it.

**Step 1 — Emit the parts to assemble**
1. Add two **Emitters**: one configured to emit **Product Base**, one for **Product Lid** (matching colors if you want same-color assemblies).
2. Feed each onto its own short conveyor leading into the assembly point.

**Step 2 — Align with Positioning Bars**
1. From **Light Load Parts**, add **Positioning Bars** at the point where the base (and separately the lid) arrives, so each part is precisely aligned before assembly. Misaligned parts won't assemble correctly.

**Step 3 — Assemble with the Two-Axis Pick & Place** ⚠️
1. From **Stations**, drag a **Two-Axis Pick & Place** — this is the part specifically built to place a Lid onto a Base (not the general 3-axis Pick & Place, which is for moving boxes around).
2. Position it so it can reach both the aligned Base and the aligned Lid, and place the assembled result onto an outfeed conveyor.
3. Your PLC sequence will step it through: move to Lid → grab → move to Base position → release (assembling Lid onto Base) → return.

**Step 4 — Add quality control**
1. From **Sensors**, add a second **Vision Sensor** after the assembly point, configured to check the resulting **Final Product** (e.g. confirm both colors are present/matching).

**Step 5 — Add the reject mechanism**
1. From **Light Load Parts** ⚠️, add another **Pusher** after the Quality Vision Sensor.
2. It diverts failed assemblies onto a short reject lane — put a **Remover** at the end of that lane.

---

## Station 3: Packaging & Palletizing

**Goal:** move finished Final Products onto pallets for "shipping."

**Step 1 — Connect the line**
1. Use **Roller Conveyors** (Heavy Load Parts) to carry Station 2's good output into Station 3.

**Step 2 — Palletize** ⚠️
1. From **Stations**, drag a **Palletizer** — Factory I/O has a purpose-built part for this (a high-level station that stacks boxes onto pallets), so you don't need to repurpose a Pick & Place for it.
2. From **Items**, place a **Pallet** (or **Square Pallet**) at the Palletizer's stacking location.
3. Configure the Palletizer's stacking pattern (rows/columns/layers) via its configuration panel.

**Step 3 — Optional: box the products first**
If you want products boxed before palletizing (closer to the original "elevator into a box" idea):
1. Add a **Pick & Place** (3-axis, Stations) to move Final Products into a **Stackable Box** (Items) sitting on a short conveyor.
2. Send the filled Stackable Box onward to the Palletizer instead of feeding it Final Products directly.
3. An **Elevator** (Stations) is useful here only if your layout genuinely needs to change floor levels to route boxes to the Palletizer — it's a vertical transport part, not a box-filling station.

---

## Mapping the I/O to your PLC

1. Tags are generated **automatically** for every sensor/actuator as you add parts — no separate menu step needed to create them.
2. In Run Mode, use the toolbar toggles to show **Sensor Tags** / **Actuator Tags** as an overlay. Click a tag to rename it (e.g. rename a Vision Sensor's tag to `ColorSensor_S1`) — do this for every tag you'll reference in TIA Portal, so the names are self-explanatory later.
3. Tags are typed as **Bool**, **Float**, or **Int** depending on the part.
4. Go to **File → Driver Configuration** to open the Driver window.
5. Select your driver — for TIA Portal/S7-1200, choose **Siemens S7-1200/1500**.
6. Open its **Configuration** panel, map each scene tag to a PLC-side I/O point, and set the Host address once you're connecting to PLCSIM or a real controller.
7. You can **export the tag mapping as TIA-Portal-compatible XML** directly from the Driver window — import that into your TIA Portal tag table instead of retyping every tag by hand.
8. Click **Connect**. A green icon confirms the link; grayed-out points mean a tag mismatch with the PLC side.

---

## Next Steps

- **PLC Programming:** In TIA Portal, create a new S7-1200 project, import the exported tag table, and write the sequences described above (sorting, assembly, palletizing) as function blocks.
- **Connectivity:** Use PLCSIM for pure simulation, or Modbus TCP/an S7 connection for a physical/virtual PLC.
- **Test:** Download the PLC program, set Factory I/O to Run Mode, and verify the full line — sort → assemble → palletize — runs under PLC control with no forced tags.
