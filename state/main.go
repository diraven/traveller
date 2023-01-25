package state

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"os"
)

type state struct {
	Guilds map[string]guild `json:"guilds"`
	Users  map[string]user  `json:"users"`
}

type guild struct {
	Name string `json:"name"`
}

type user struct {
	Name    string `json:"name"`
	IsOwner bool   `json:"is_owner"`
}

var State = &state{}

func (s *state) Load() {
	jsonFile, err := os.Open("state.json")
	defer jsonFile.Close()
	if err != nil {
		log.Panic(err)
	}
	byteValue, _ := ioutil.ReadAll(jsonFile)
	json.Unmarshal([]byte(byteValue), s)
}

func (s *state) Save() {
	file, err := json.MarshalIndent(s, "", "    ")
	if err != nil {
		log.Panic(err)
	}

	err = ioutil.WriteFile("state.json", file, 0644)
	if err != nil {
		log.Panic(err)
	}
}

func (s *state) IsOwner(userId string) bool {
	for userId, user := range s.Users {
		if userId == userId && user.IsOwner {
			return true
		}
	}
	return false
}

func init() {
	State.Load()
}
