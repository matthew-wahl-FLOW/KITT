# // Integration simulation for a train run
# // Simulates sensor events and verifies orchestrator publishes expected jmri commands
#
# PSEUDOCODE:
# start simulated MQTT broker (or use test broker)
# publish fake order to kitt/order/new
# simulate sensors: occupancy, rfid, loadcell
# assert jmri_bridge received expected commands in correct order
