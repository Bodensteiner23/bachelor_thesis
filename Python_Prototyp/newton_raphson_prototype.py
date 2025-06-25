import pandapower as pp

net = pp.create_empty_network()
bus1 = pp.create_bus(net, vn_kv=0.4)
bus2 = pp.create_bus(net, vn_kv=0.4)
pp.create_ext_grid(net, bus1, vm_pu=1.0)
pp.create_load(net, bus2, p_mw=0.1, q_mvar=0.05)
pp.create_line_from_parameters(net, from_bus=bus1, to_bus=bus2,
                               length_km=0.1, r_ohm_per_km=0.64,
                               x_ohm_per_km=0.08, c_nf_per_km=0, max_i_ka=0.1)
pp.runpp(net)
print(net.res_bus)