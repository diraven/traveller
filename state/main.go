package state

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"os"

	"github.com/bwmarrin/discordgo"
)

type state struct {
	Guilds map[string]*guild `json:"guilds"`
	Users  map[string]*user  `json:"users"`
}

type guild struct {
	Name string  `json:"name"`
	T    *tGuild `json:"t"`
}

type user struct {
	Name    string `json:"name"`
	IsOwner bool   `json:"is_owner"`
	T       *tUser `json:"t"`
}

type tGuild struct {
	Hp   float32 `json:"hp"`
	Food int     `json:"food"`
}

type tUser struct {
	Action string `json:"action"`
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

func (s *state) GetUser(discordUser *discordgo.User) *user {
	// Search for user in state.
	userState, ok := s.Users[discordUser.ID]
	if !ok {
		userState = &user{
			Name: discordUser.Username + "#" + discordUser.Discriminator,
		}
	}

	// Set name if not exists.
	if userState.Name == "" {
		userState.Name = discordUser.Username + "#" + discordUser.Discriminator
	}

	// Initialize T if not exists.
	if userState.T == nil {
		userState.T = &tUser{}
	}

	// User not found in state.
	return userState
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
