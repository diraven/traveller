package state

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
)

type state struct {
	Guilds map[string]guild `json:"guilds"`
	Owners []string         `json:"owners"`
}

type guild struct {
	Name string `json:"name"`
}

var State = &state{}

func init() {
	jsonFile, err := os.Open("state.json")
	defer jsonFile.Close()
	if err != nil {
		fmt.Println(err)
	}
	byteValue, _ := ioutil.ReadAll(jsonFile)
	json.Unmarshal([]byte(byteValue), State)
}
