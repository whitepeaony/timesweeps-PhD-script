# %%
from syringe_pump import Quantity
from aioserial import AioSerial
import asyncio
from tabulate import tabulate
from timesweeps_pump.legato_101 import Legato101
import datetime

# %%
serial = AioSerial(port="COM8", timeout=1)
pump = await Legato101.from_serial(serial)

# %%
# variables - define at the start of experiment

# Reactor volume in ml
Vrec = 0.323

# Dead volume (from the reactor to NMR) in ml
Vded = 0.227

# stabilisation factor, unitless
stab_fac = 2

# Timesweep ranges [min]
t1 = 4  # sweep1 starting residence time
t2 = 45  # sweep1 ending / sweep2 starting residence time

tend = 15  # steady-state for manual sample collection at the end

sweep_no = 1  # number of timesweeps

# %%
### Flow rates [ml/min] ###
v1 = Vrec / t1  # sweep1 starting rate
v2 = Vrec / t2  # sweep1 ending/sweep2 starting rate

## Times of experiment phases [s] ##
stab_time = stab_fac * t1 * 60
dead1_time = (
    Vded * t2 * 60
) / Vrec  # t needed to push the start of the sweep through the Vdead
sweep1_time = t2 * 60


## Pump times [s] ##
v1_time = stab_time
v2_time = dead1_time + sweep1_time + tend * 60


# time required for the experiment
time_total = stab_time + dead1_time + sweep1_time

# reaction volume
total_volume = stab_fac * Vrec + sweep_no * Vrec + sweep_no * Vded

print(
    tabulate(
        [
            ["v1", f"{v1:.4f}"],
            ["v2", f"{v2:.4f}"],
        ],
        headers=["Flow rate", "[ml/min]"],
    )
)
print("Total experiment time: " + f"{(time_total/60):.2f}" + " min")
print("Total experiment volume: " + f"{total_volume:.2f}" + " ml")


# %%
# Timesweep experiment

await pump.infusion_volume.clear()

# stabilisation and sweep #1
await pump.infusion_rate.set(Quantity(f"{v1} ml/min"))
print(await pump.infusion_rate.get())
await pump.run()
print("Start: " + f"{datetime.datetime.now()}")
await asyncio.sleep(v1_time)
print(f"{v1_time}" + " s")
await pump.stop()
print("Stop: " + f"{datetime.datetime.now()}")

await pump.infusion_rate.set(Quantity(f"{v2} ml/min"))
print(await pump.infusion_rate.get())
await pump.run()
print("Start: " + f"{datetime.datetime.now()}")
await asyncio.sleep(v2_time)
print(f"{v2_time}" + "s")
await pump.stop()
print("Stop: " + f"{datetime.datetime.now()}")
