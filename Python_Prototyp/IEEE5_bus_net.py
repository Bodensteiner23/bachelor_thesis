import pandapower as pp


# Create empty low-voltage network
net = pp.create_empty_network()

# Create 5 buses at 0.4 kV
b1 = pp.create_bus(net, vn_kv=0.4, name="Bus 1")
b2 = pp.create_bus(net, vn_kv=0.4, name="Bus 2")
b3 = pp.create_bus(net, vn_kv=0.4, name="Bus 3")
b4 = pp.create_bus(net, vn_kv=0.4, name="Bus 4")
b5 = pp.create_bus(net, vn_kv=0.4, name="Bus 5")

# Create slack/ext grid at Bus 1
pp.create_ext_grid(net, bus=b1, vm_pu=1.0, name="Slack")

# Add loads in kW / kvar (converted to MW / MVAR)
pp.create_load(net, bus=b2, p_mw=0.020, q_mvar=0.005, name="Load 2")
pp.create_load(net, bus=b3, p_mw=0.030, q_mvar=0.010, name="Load 3")
pp.create_load(net, bus=b4, p_mw=0.010, q_mvar=0.003, name="Load 4")
pp.create_load(net, bus=b5, p_mw=0.015, q_mvar=0.004, name="Load 5")

# Add lines with realistic LV impedance and short lengths (~100m)
pp.create_line_from_parameters(net, from_bus=b1, to_bus=b2, length_km=0.1,
                               r_ohm_per_km=0.4, x_ohm_per_km=0.1,
                               c_nf_per_km=0, max_i_ka=0.2, name="Line 1-2")

# pp.create_line_from_parameters(net, from_bus=b1, to_bus=b3, length_km=0.07,
#                                r_ohm_per_km=0.37, x_ohm_per_km=0.1,
#                                c_nf_per_km=0, max_i_ka=0.2, name="Line 1-3")

pp.create_line_from_parameters(net, from_bus=b2, to_bus=b3, length_km=0.15,
                               r_ohm_per_km=0.35, x_ohm_per_km=0.09,
                               c_nf_per_km=0, max_i_ka=0.2, name="Line 2-3")

pp.create_line_from_parameters(net, from_bus=b3, to_bus=b4, length_km=0.1,
                               r_ohm_per_km=0.38, x_ohm_per_km=0.1,
                               c_nf_per_km=0, max_i_ka=0.2, name="Line 3-4")

pp.create_line_from_parameters(net, from_bus=b4, to_bus=b5, length_km=0.08,
                               r_ohm_per_km=0.42, x_ohm_per_km=0.11,
                               c_nf_per_km=0, max_i_ka=0.2, name="Line 4-5")

pp.create_line_from_parameters(net, from_bus=b5, to_bus=b1, length_km=0.12,
                               r_ohm_per_km=0.36, x_ohm_per_km=0.095,
                               c_nf_per_km=0, max_i_ka=0.2, name="Line 5-1")

# pp.plotting.simple_plot(net)

import numpy as np

# Store base values so we can modify them randomly each run
base_p = net.load.p_mw.copy()
base_q = net.load.q_mvar.copy()

n_runs = 10  # how many randomized simulations
results = []

for run in range(0, n_runs):
    # Randomize loads: ±25% around base values
    net.load.p_mw = base_p * (0.875 + 0.25 * np.random.rand(len(base_p)))
    net.load.q_mvar = base_q * (0.875 + 0.25 * np.random.rand(len(base_q)))

    # Run power flow
    pp.runpp(net, algorithm='nr')

    # Collect data for each line
    for i, line in net.line.iterrows():
        from_bus = line.from_bus
        to_bus = line.to_bus
        v_from = net.res_bus.vm_pu[from_bus]
        v_to = net.res_bus.vm_pu[to_bus]
        delta_v = v_from - v_to
        p = net.res_line.p_from_mw[i]
        q = net.res_line.q_from_mvar[i]
        r = line.r_ohm_per_km * line.length_km
        x = line.x_ohm_per_km * line.length_km
        v_drop_expected = (r * p * 1e6 + x * q * 1e6)  # now in volts
        results.append({
            "run": run,
            "line": line.name,
            "from_bus": from_bus,
            "to_bus": to_bus,
            "p_mw": p,
            "q_mvar": q,
            "delta_v_pu": delta_v,
            "delta_v_volt": delta_v * 400,
            "v_drop_expected": v_drop_expected / 400
        })


import pandas as pd
df = pd.DataFrame(results)
# print(df.head())
df.to_csv("line_measurements.csv", index=False)  # export to CSV
