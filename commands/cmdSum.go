package commands

import (
	"fmt"

	"github.com/bwmarrin/discordgo"
)

var cmdSum = &Command{
	Definition: &discordgo.ApplicationCommand{
		Name:        "sum",
		Description: "Пошук слова в словнику української мови",
		Options: []*discordgo.ApplicationCommandOption{
			{
				Type:        discordgo.ApplicationCommandOptionString,
				Name:        "word",
				Description: "слово",
				Required:    true,
			},
		},
	},
	Handler: func(s *discordgo.Session, i *discordgo.InteractionCreate) {
		// Convert options to map.
		options := i.ApplicationCommandData().Options
		optionMap := make(map[string]*discordgo.ApplicationCommandInteractionDataOption, len(options))
		for _, opt := range options {
			optionMap[opt.Name] = opt
		}

		// Respond.
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Content: fmt.Sprintf("http://sum.in.ua/?swrd=%s", optionMap["word"].StringValue()),
			},
		})
	},
}
