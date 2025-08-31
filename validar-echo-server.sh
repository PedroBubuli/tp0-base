#!/bin/bash
# validar-echo-server.sh
# uso: ./validar-echo-server.sh

TEST_MSG="hola_echo"

#container temporal con netcat en la misma red que el server
REPLY=$(docker run --rm --network tp0_testing_net alpine \
    sh -c "echo $TEST_MSG | nc -w 2 server 12345")

#validar 
if [ "$REPLY" = "$TEST_MSG" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi
