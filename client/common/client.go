package common

import (
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config   ClientConfig
	protocol *ClientProtocol
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) connectToServer() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.protocol = NewClientProtocol(conn)
	return nil
}

func (c *Client) Bet(name string, surname string, dni uint32, date_of_birth string, number uint32) {

	c.connectToServer()
	defer c.protocol.Close()

	signalChannel := make(chan os.Signal, 1)
	signal.Notify(signalChannel, os.Interrupt, syscall.SIGTERM)

	select {
	case <-signalChannel:
		log.Infof("action: exit | result: success | client_id: %v", c.config.ID)
		c.protocol.Close()
		return
	default:
		err := c.protocol.sendBetInfo(name, surname, dni, date_of_birth, number)
		if err != nil {
			log.Errorf("action: apuesta_enviada | result: fail | dni: %v | numero: %v",
				dni,
				number,
			)
			return
		}

	}
	log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
		dni,
		number,
	)
}
