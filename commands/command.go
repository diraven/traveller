package commands

import (
	"github.com/bwmarrin/discordgo"
	"github.com/diraven/traveller/state"
)

type Command struct {
	Init   func(s *discordgo.Session, state *state.State) error
	DeInit func(s *discordgo.Session, state *state.State) error
}
