package commands

import (
	"log"

	"github.com/bwmarrin/discordgo"
	"github.com/diraven/traveller/state"
)

var commands = []*Command{
	// cmdTest,
	cmdFaq,
}

func Init(s *discordgo.Session, state *state.State) {
	for _, cmd := range commands {
		cmd.Init(s, state)
	}
}

func DeInit(s *discordgo.Session, state *state.State) {
	for _, cmd := range commands {
		if cmd.DeInit != nil {
			cmd.DeInit(s, state)
		}
	}

	// Delete all commands for all guilds.
	for GuildID := range state.Guilds {
		registeredCommands, err := s.ApplicationCommands(s.State.User.ID, GuildID)
		if err != nil {
			log.Fatalf("Could not fetch registered commands: %v", err)
		}
		for _, v := range registeredCommands {
			err := s.ApplicationCommandDelete(s.State.User.ID, GuildID, v.ID)
			if err != nil {
				log.Panicf("Cannot delete '%v' command: %v", v.Name, err)
			}
		}
	}
	// Delete global commands.
	registeredCommands, err := s.ApplicationCommands(s.State.User.ID, "")
	if err != nil {
		log.Fatalf("Could not fetch registered commands: %v", err)
	}
	for _, v := range registeredCommands {
		err := s.ApplicationCommandDelete(s.State.User.ID, "", v.ID)
		if err != nil {
			log.Panicf("Cannot delete '%v' command: %v", v.Name, err)
		}
	}

}
