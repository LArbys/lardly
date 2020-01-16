# lardly


Still in development. Python scripts in the folder serve as examples to program your own displays.

Some examples:


### `test_3d.py`

Using this script to play around. You can load in a `larlite` file and an `larcv` file.

![Image](test3d_screenshot.png?raw=true)

### `test_dlmerged.py`

This script plots most of the reconstruction quantities in the DL reco. chain.
Runs on the `merged_dlreco` files produced by the production at FNAL (and now Tufts).

### `plot_lfcluster.py`

This shows how one setups menu buttons.

### `test_crt.py`

Example for plotting CRT.

![Image](screenshot_test_crt.png?raw=true)

# Installation instructions

Follow [this page](https://dash.plot.ly/installation) to install `plotly dash`.

You also need to build EITHER `ubdl` or `dllee_unified` version of the DL LEE software.

The `ubdl` [repo](https://github.com/larbys/ubdl).

The `dllee_unified` [repo](https://github.com/larbys/dllee_unified).

# Using `lardly` on MicroBooNE build machine

First log into `uboonebuild02` with port forwarding (setup using the `-L` flag in the command below). 
Right now this is the only machine that will work, as it runs SL7.
In the future, will make an SL6 solution for the UB gpvms.

    ssh -XY -L 8005:localhost:8005 username@uboonebuild02.fnal.gov

Note that the port I use, `8005`, can be changed. And only one person can use a port at a time. 
When you log in and see a message of a port already in use, try another one. By convention use something above and around `8000`.

## First time use: install dependences, `plot.ly` and `dash`

You only need to do this once

    source /cvmfs/uboone.opensciencegrid.org/products/setup_uboone.sh
    setup dllee_unified v1_0_3 -q e17:prof
    pip install --user plotly
    pip install --user dash==1.8.0

The `--user` is important. So is setting up `dllee_unified` before running `pip`.  
This makes sure you are using the right version of `python`/`pip`.

Now get the `lardly` code.

    git clone https://github.com/larbys/lardly


## Subsequent uses after installation

Note, you always have to setup port forwarding (see above) and you have to setup `cvmfs` everytime you start a new login.

    source /cvmfs/uboone.opensciencegrid.org/products/setup_uboone.sh

You also have to setup `dllee_unified` for each new login as well.

    setup dllee_unified v1_0_3 -q e17:prof

Now go back to the `lardly` folder you cloned.
The you can start an event viewer.

    python test_dlmerged.py --input-file [dlmerged root file] -e 0 -p 8005

Note the port you used. `dash` will use `8050` by default, so you need to set the port to the one you used in your `ssh` command.

Then open a browser on your local machine (e.g. laptop) and go to `https://localhost:8005`. Again, use your port.

The event should load -- it'll take awhile as the image data is large. But once loaded, navigation "should" be fairly fast.

This is just a development script. Play around with it!  There are flags to turn certain things on and off.
There are other scripts that may or may not work. 

     

    
    