package state

import (
	"encoding/json"
	"io/ioutil"
	"log"
	"os"

	"github.com/bwmarrin/discordgo"
)

type state struct {
	Guilds map[string]*Guild `json:"guilds"`
	Users  map[string]*User  `json:"users"`
}

type Guild struct {
	Name         string  `json:"name"`
	IsActive     bool    `json:"is_active"`
	LogChannelId string  `json:"log_channel_id"`
	T            *TGuild `json:"t"`
}

type User struct {
	Name    string `json:"name"`
	IsOwner bool   `json:"is_owner"`
	T       *TUser `json:"t"`
}

type TGuild struct {
	Hp   float32 `json:"hp"`
	Food int     `json:"food"`
}

type TUser struct {
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

func (s *state) GetUser(discordUser *discordgo.User) *User {
	// Search for user in state.
	userState, ok := s.Users[discordUser.ID]
	if !ok {
		userState = &User{
			Name: discordUser.Username + "#" + discordUser.Discriminator,
		}
	}

	// Set name if not exists.
	if userState.Name == "" {
		userState.Name = discordUser.Username + "#" + discordUser.Discriminator
	}

	// Initialize T if not exists.
	if userState.T == nil {
		userState.T = &TUser{}
	}

	// User not found in state.
	return userState
}

func (s *state) IsOwner(userId string) bool {
	for stateUserId, user := range s.Users {
		if userId == stateUserId && user.IsOwner {
			return true
		}
	}
	return false
}

func (s *state) ActiveGuilds() map[string]*Guild {
	guilds := make(map[string]*Guild, 0)
	for guildId, guild := range s.Guilds {
		guilds[guildId] = guild
	}
	return guilds
}

func init() {
	State.Load()
}
