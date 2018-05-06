# Plot data from TheThingsNetwork on Nodewatcher
This code is a simple bridge enabling the data from TheThingsNetwork Application to be plotted on the Nodewatcher platform, for example http://nodes.wlan-si.net

What this code does is:
 * Plots the RSSI value on one graph for all gateways that received the LoraWAN packet
 * Plots all the payload field on one graph, you can turn on and off the ones you want to check
 * You can define custom graphs in the code

To achieve this you have to do the following:

1. Create a TTN Application and write a decoder
1. Register a node on Nodewatcher (one per application, all devices are plotted in one node)
1. Run the python code on a server somewhere, for example Ubuntu on AWS or similar
1. Enjoy the graphs

## Register the sensor with nodewatcher
1. Register and log on [nodewatcher](https://nodes.wlan-si.net/)
 1. Select `Register New Node` under your user account
 1. Turn `Advanced mode` to `ON` on top right
 1. Now select `Disable defaults`
 1. Select the sensor name by entering it into `Name` field
 1. Select `Platform` to be `---------`
 1. Configure location on the map if you wish
 1. Select `Telemetry source` to be `Push from Node`
 1. Add `Identity Mechanisms` field and select `HMAC Signature`
 1. Tick the box `Trusted`
 1. Pick your key and enter it, insert in python code as `INSERTNWHMACKEY`
 1. Remove `Router Identifier`
 1. Remove `DNS servers`

## Configure python code
Replace the following values:
 1. `INSERTAPPEUI` with value you can find on TTN Application EUI
 1. `INSERTAPPID` with value you can find on TTN Application
 1. `INSERTACCESSKEY` with value you can find on TTN Application
 1. `push.nodes.wlan-si.net` is the default server, replace if you have your own
 1. `INSERTNWUUID` with value you can find on Nodewatcher in the URL
 1. `INSERTNWHMACKEY`with the HMAC key you have set

Run the code with `nohup python ttn-mqtt-nodewatcher.py &`
