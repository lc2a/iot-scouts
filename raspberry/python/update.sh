# We run this script in a screen in /etc/rc.local
#!/bin/bash
while :
do
    echo "Bringing down the network..."
    gotInternet=1
    sudo ifdown eth0
    sudo ifdown wlan0
    sleep 5
    echo "Trying with eth0..."
    sudo ifup eth0
    sleep 5
    echo "Trying to ping google.com..."
    sleep 1
    ping -c 5 8.8.8.8
    pingerEth=$?
    if [ $pingerEth = 0 ]
    then
        gotInternet=0
    else
        echo "Trying with wlan0..."
        sudo ifup wlan0
        sleep 5
        ping -c 5 8.8.8.8
        pingerWlan=$?
        if [ $pingerWlan = 0 ]
        then
            gotInternet=0
        fi
    fi
    if [ $gotInternet = 0 ]
    then
        echo "Everything is OK, starting up..."
        wget -O /path/to/somefolder/startUp.py https://cybertrust.labranet.jamk.fi/cf2017/iot-scouts/raw/master/raspberry/python/startUp.py
        python3 /path/to/somefolder/startUp.py -user username -passw password -ip tbgateway_ip_address
    else
        echo ""
        echo "It seems you have a problem. Check your internet! Is it even working?"
        echo ""
    fi
done