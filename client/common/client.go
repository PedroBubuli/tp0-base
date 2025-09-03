package common

import (
	"bufio"
	"net"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"syscall"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

const (
	NAME_POS          = 0
	SURNAME_POS       = 1
	DNI_POS           = 2
	DATE_OF_BIRTH_POS = 3
	NUMBER_POS        = 4
	MAX_SIZE          = (8 * 1024) - 4
)

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

func (c *Client) Bet(id uint8, maxBets uint8) {

	file, err := os.Open("agency.csv")
	if err != nil {
		log.Criticalf("action: open_file | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	chunk := make([]byte, 0)
	betsCount := 0

	signalChannel := make(chan os.Signal, 1)
	signal.Notify(signalChannel, os.Interrupt, syscall.SIGTERM)

	c.connectToServer()
	defer c.protocol.Close()

	select {
	case <-signalChannel:
		log.Infof("action: exit | result: success | client_id: %v", c.config.ID)
		c.protocol.Close()
		file.Close()
		return
	default:
		for scanner.Scan() {
			line := scanner.Text()
			parts := strings.Split(line, ",")
			if len(parts) != 5 {
				log.Errorf("action: parse_line | result: fail | client_id: %v | line: %v",
					c.config.ID,
					line,
				)
				continue
			}
			dni, _ := strconv.ParseUint(parts[DNI_POS], 10, 32)
			num, _ := strconv.ParseUint(parts[NUMBER_POS], 10, 32)
			bytes := c.protocol.serializeBetInfo(parts[NAME_POS], parts[SURNAME_POS], uint32(dni), parts[DATE_OF_BIRTH_POS], uint32(num))

			chunk = append(chunk, bytes...)
			betsCount++

			if len(chunk) > MAX_SIZE || betsCount > int(maxBets) {
				err := c.protocol.sendAgencyID(id)
				if err != nil {
					log.Errorf("action: send_agency_id | result: fail | client_id: %v | error: %v",
						c.config.ID,
						err,
					)
					return
				}
				err = c.protocol.sendBetInfo(chunk[:len(chunk)-len(bytes)], uint8(betsCount-1))
				if err != nil {
					log.Errorf("action: send_bet_info | result: fail | error: %v", err)
					return
				}
				if b, e := c.protocol.recvSuccessMessage(); e != nil || !b {
					log.Errorf("action: recv_success_message | result: fail | error: %v", e)
					return
				}
				log.Infof("action: send_bet_info| result: success | bets_sent: %v", betsCount-1)
				chunk = append(make([]byte, 0), bytes...)
				betsCount = 1
			}
		}

		if betsCount > 0 {
			err := c.protocol.sendAgencyID(id)
			if err != nil {
				log.Errorf("action: send_agency_id | result: fail | client_id: %v | error: %v",
					c.config.ID,
					err,
				)
				return
			}
			err = c.protocol.sendBetInfo(chunk, uint8(betsCount))
			if err != nil {
				log.Errorf("action: send_bet_info | result: fail | error: %v", err)
				return
			}
			if b, e := c.protocol.recvSuccessMessage(); e != nil || !b {
				log.Errorf("action: recv_success_message | result: fail | error: %v", e)
				return
			}
			log.Infof("action: send_bet_info| result: success | bets_sent: %v", betsCount)
		}
		err := c.protocol.AskForWinners()
		if err != nil {
			log.Errorf("action: ask_for_winners | result: fail | error: %v", err)
			return
		}
		winners, err := c.protocol.ReceiveWinners()
		if err != nil {
			log.Errorf("action: receive_winners | result: fail | error: %v", err)
			return
		} else {
			log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %d", len(winners))
		}
	}
}
