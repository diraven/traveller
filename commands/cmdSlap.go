package commands

import (
	"fmt"
	"math/rand"
	"time"

	"github.com/bwmarrin/discordgo"
)

var templates = []string{
	"%s прикладає %s по спині величезним сомом.",
	"%s демонструє %s щорічну заяву Арестовича на звільнення.",
	"%s щось кричить %s на вухо.",
	"%s уважно дивиться %s в очі.",
	"%s хизується електрохарчуванням перед %s.",
}

var cmdSlap = &Command{
	Definition: &discordgo.ApplicationCommand{
		Name:        "slap",
		Description: "???",
		Options: []*discordgo.ApplicationCommandOption{
			{
				Type:        discordgo.ApplicationCommandOptionUser,
				Name:        "user",
				Description: "Користувач",
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
		rand.Seed(time.Now().Unix())
		s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
			Type: discordgo.InteractionResponseChannelMessageWithSource,
			Data: &discordgo.InteractionResponseData{
				Embeds: []*discordgo.MessageEmbed{
					{
						Description: fmt.Sprintf(templates[rand.Intn(len(templates))], i.Member.Mention(), (optionMap["user"]).UserValue(s).Mention()),
					},
				},
			},
		})
	},
}
