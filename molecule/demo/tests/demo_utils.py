def check_demo(host):
    host.run("""
    /usr/local/bin/cronscript
    cd /srv/securedrop
    for i in *.sh ; do
       timeout 1800 flock /tmp/$i.lock $i wait_ports
       echo $i done
    done
    """)
