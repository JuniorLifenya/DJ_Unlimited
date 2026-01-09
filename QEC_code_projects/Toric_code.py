import numpy as np 
import stim 
import pymatching 

circuit = stim.Circuit.generated(
        'surface_code: rotated_memory_x',
        distance = 5 ,
        round = 5 ,
        after_clifford_depolarization = 0.005
 )
model = circuit.detector_error_model(decompose_errors = True)
matching = pymatching.Matching.from_detector_error_model(model)


print(circuit)