#!/usr/bin/env python3
# custom_prediction.py - Custom prediction interface for PsyNet

from psynet_integration import PsyNetIntegration
import json
import sys

def make_prediction(prediction_type, **parameters):
    """Make a prediction using PsyNet integration"""
    psynet = PsyNetIntegration()
    result = psynet.handle_prediction_request({
        'prediction_type': prediction_type,
        'parameters': parameters
    })
    return result

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python custom_prediction.py <prediction_type> <query> [time_horizon]")
        sys.exit(1)
        
    prediction_type = sys.argv[1]
    query = sys.argv[2]
    time_horizon = int(sys.argv[3]) if len(sys.argv) > 3 else 14
    
    result = make_prediction(prediction_type, query=query, time_horizon=time_horizon)
    print(json.dumps(result, indent=2))
