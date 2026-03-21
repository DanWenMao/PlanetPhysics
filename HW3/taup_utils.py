from obspy.taup import TauPyModel

model = TauPyModel(model="iasp91")

def compute_travel_times(dist, depth):
    arrivals = model.get_travel_times(
        source_depth_in_km=depth,
        distance_in_degree=dist,
        phase_list=["P", "S"]
    )

    tP, tS = None, None

    for a in arrivals:
        if a.name == "P" and tP is None:
            tP = a.time
        if a.name == "S" and tS is None:
            tS = a.time

    return tP, tS