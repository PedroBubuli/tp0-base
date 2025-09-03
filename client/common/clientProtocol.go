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

func (cp *ClientProtocol) ReadAll(size int) ([]byte, error) {
	buf := make([]byte, size)
	totalRead := 0

	for totalRead < size {
		n, err := cp.skt.Read(buf[totalRead:])
		if err != nil {
			return nil, err
		}
		totalRead += n
	}
	return buf, nil
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

func serializeString(my_string string) []byte {
	var data = make([]byte, 0)
	data = append(data, byte(len(my_string)))
	data = append(data, []byte(my_string)...)
	return data
}

func serializeUint32(num uint32) []byte {
	data := make([]byte, 4)
	binary.BigEndian.PutUint32(data, num)
	return data
}

func (cp *ClientProtocol) serializeBetInfo(name string, surname string, dni uint32, date_of_birth string, number uint32) []byte {

	var data = make([]byte, 0)

	data = append(data, serializeString(name)...)
	data = append(data, serializeString(surname)...)
	data = append(data, serializeUint32(dni)...)
	data = append(data, serializeString(date_of_birth)...)
	data = append(data, serializeUint32(number)...)

	return data
}

func (cp *ClientProtocol) sendAgencyID(id uint8) error {
	return cp.SendAll([]byte{id})
}

func (cp *ClientProtocol) sendBetInfo(data []byte, size uint8) error {
	return cp.SendAll(append([]byte{size}, data...))
}

func (cp *ClientProtocol) recvSuccessMessage() (bool, error) {
	confirmation, err := cp.ReadAll(1)
	if err == nil && confirmation[0] == 1 {
		return true, nil
	}
	return false, err
}

func (cp *ClientProtocol) AskForWinners() error {
	return cp.SendAll([]byte{0})
}

func (cp *ClientProtocol) ReceiveWinners() ([]int, error) {
	sizeBuf, err := cp.ReadAll(4)
	if err != nil {
		return nil, err
	}
	size := binary.BigEndian.Uint32(sizeBuf)
	winners := make([]int, size)
	for i := uint32(0); i < size; i++ {
		numBuf, err := cp.ReadAll(4)
		if err != nil {
			return nil, err
		}
		number := binary.BigEndian.Uint32(numBuf)
		winners[i] = int(number)
	}
	return winners, nil
}
func (cp *ClientProtocol) Close() {
	if cp.skt != nil {
		cp.skt.Close()
	}
}
