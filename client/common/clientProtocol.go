package common

import (
	"encoding/binary"
	"net"
)

const sizeofUint32 = 4

type ClientProtocol struct {
	skt net.Conn
}

func NewClientProtocol(skt net.Conn) *ClientProtocol {
	return &ClientProtocol{
		skt: skt,
	}
}

func (cp *ClientProtocol) SendAll(data []byte) error {
	totalSent := 0
	dataLen := len(data)

	for totalSent < dataLen {
		n, err := cp.skt.Write(data[totalSent:])
		if err != nil {
			return err
		}
		totalSent += n
	}
	return nil
}

func (cp *ClientProtocol) SendNumber(num uint32) error {
	data := make([]byte, sizeofUint32)
	binary.BigEndian.PutUint32(data, num)
	err := cp.SendAll(data)
	return err
}

func (cp *ClientProtocol) SendString(str string) error {
	buf := make([]byte, 1)
	buf[0] = byte(len(str))
	err := cp.SendAll(buf)
	if err != nil {
		return err
	}
	return cp.SendAll([]byte(str))
}

func (cp *ClientProtocol) sendBetInfo(name string, surname string, dni uint32, date_of_birth string, number uint32) error {

	err := cp.SendString(name)
	if err != nil {
		return err
	}

	err = cp.SendString(surname)
	if err != nil {
		return err
	}

	err = cp.SendNumber(dni)
	if err != nil {
		return err
	}

	err = cp.SendString(date_of_birth)
	if err != nil {
		return err
	}

	err = cp.SendNumber(number)
	if err != nil {
		return err
	}

	return nil
}

func (cp *ClientProtocol) Close() {
	if cp.skt != nil {
		cp.skt.Close()
	}
}
