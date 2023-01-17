package state

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
)

type State struct {
	Guilds map[string]Guild `json:"guilds"`
}

type Guild struct{}

func Load() *State {
	jsonFile, err := os.Open("state.json")
	defer jsonFile.Close()
	if err != nil {
		fmt.Println(err)
	}
	byteValue, _ := ioutil.ReadAll(jsonFile)
	var state *State = &State{}
	json.Unmarshal([]byte(byteValue), state)
	return state
}
