package commands

import (
	"log"

	"github.com/bwmarrin/discordgo"
	"github.com/diraven/traveller/state"
)

var commands = []*Command{
	// cmdTest,
	cmdFaq,
	cmdSetLogChannel,
	cmdGBanUid,
	cmdSlap,
	cmdRusniPizda,
	cmdState,
	cmdTraveller,
	cmdSum,
	cmdSum20,
}

func Init(s *discordgo.Session) {
	for _, cmd := range commands {
		definition := cmd.Definition
		handler := cmd.Handler
		// Register command for all the active guilds.
		for guildId, guild := range state.State.ActiveGuilds() {
			log.Printf("Initializing command '" + definition.Name + "' for server '" + guild.Name + "'")
			_, err := s.ApplicationCommandCreate(s.State.User.ID, guildId, definition)
			if err != nil {
				log.Panicf("Cannot create '%v' command: %v", definition.Name, err)
			}
		}
		// Add handler.
		s.AddHandler(func(s *discordgo.Session, i *discordgo.InteractionCreate) {
			if i.ApplicationCommandData().Name == definition.Name {
				handler(s, i)
			}
		})
	}
}

func DeInit(s *discordgo.Session) {
	// Delete all commands for all guilds.
	for guildId := range state.State.ActiveGuilds() {
		registeredCommands, err := s.ApplicationCommands(s.State.User.ID, guildId)
		if err != nil {
			log.Fatalf("Could not fetch registered commands: %v", err)
		}
		for _, v := range registeredCommands {
			err := s.ApplicationCommandDelete(s.State.User.ID, guildId, v.ID)
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
